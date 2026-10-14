from contextlib import contextmanager
from datetime import date, datetime, timezone
from html import escape

from flask import current_app
from flask_mail import Message

from application.infrastructure import celery, db, mail
from application.models import Notification, TelegramConnection
from application.methods.birthday_methods import school_today
from application.telegram import TelegramAPIError, TelegramBotAPI


def enqueue_notification_delivery(notification_id):
    send_notification_email.delay(notification_id)
    send_notification_telegram.delay(notification_id)


def _utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


@contextmanager
def _locked_notification(notification_id):
    try:
        # Do not occupy worker processes while another channel holds this row.
        # A busy row raises immediately and is retried by Celery with backoff.
        yield Notification.query.filter_by(id=notification_id).with_for_update(
            of=Notification, nowait=True,
        ).first()
    finally:
        # Also release locks on early returns, timeouts and unexpected errors.
        db.session.rollback()


def _delivery_content(notification):
    title, message = notification.title, notification.message
    key = notification.system_key or ''
    if key.startswith('birthday:'):
        try:
            birthday = date.fromisoformat(key.split(':')[1])
        except (ValueError, IndexError):
            return title, message
        if birthday < school_today():
            title = f'День рождения {birthday:%d.%m.%Y}'
            prefix = f'Сегодня, {birthday:%d.%m}, '
            if message.startswith(prefix):
                message = f'{birthday:%d.%m.%Y} ' + message[len(prefix):]
            message += '\n\nУведомление доставлено с задержкой.'
    return title, message


@celery.task(
    autoretry_for=(Exception,),
    retry_backoff=60,
    retry_backoff_max=3600,
    soft_time_limit=120,
    time_limit=150,
    rate_limit='30/m',
    retry_jitter=True,
    retry_kwargs={'max_retries': 5},
)
def send_notification_email(notification_id):
    with _locked_notification(notification_id) as notification:
        if not notification or notification.email_sent_at:
            return

        title, message = _delivery_content(notification)
        link_html = ''
        if notification.url:
            safe_url = escape(notification.url, quote=True)
            link_html = f'<p><a href="{safe_url}">Открыть в сервисе</a></p>'
        html = (
            f'<p><strong>{escape(title)}</strong></p>'
            f'<p>{escape(message).replace(chr(10), "<br>")}</p>'
            f'{link_html}'
            f'<p style="color:#6c757d">Источник: {escape(notification.source_name)}</p>'
        )
        try:
            mail.send(Message(
                subject=f'{current_app.config["APP_NAME"]} — {title}',
                recipients=[notification.user.email],
                html=html,
            ))
            notification.email_sent_at = _utcnow()
            notification.email_error = None
        except Exception as error:
            notification.email_error = str(error)[:2000]
            db.session.commit()
            raise
        db.session.commit()


@celery.task(
    autoretry_for=(Exception,),
    retry_backoff=60,
    retry_backoff_max=3600,
    soft_time_limit=120,
    time_limit=150,
    retry_jitter=True,
    retry_kwargs={'max_retries': 5},
)
def send_notification_telegram(notification_id):
    with _locked_notification(notification_id) as notification:
        if not notification or notification.telegram_sent_at:
            return

        connection = TelegramConnection.query.filter_by(user_id=notification.user_id).first()
        if not connection:
            return

        title, message = _delivery_content(notification)
        text = f'{title}\n\n{message}'
        if notification.url:
            text += f'\n\n{notification.url}'
        text += f'\n\nИсточник: {notification.source_name}'
        try:
            TelegramBotAPI(
                current_app.config.get('TELEGRAM_BOT_TOKEN'),
                proxy_url=current_app.config.get('TELEGRAM_PROXY_URL'),
            ).send_message(
                connection.chat_id, text
            )
            notification.telegram_sent_at = _utcnow()
            notification.telegram_error = None
        except Exception as error:
            notification.telegram_error = str(error)[:2000]
            if isinstance(error, TelegramAPIError) and error.error_code == 403:
                db.session.delete(connection)
            db.session.commit()
            raise
        db.session.commit()
