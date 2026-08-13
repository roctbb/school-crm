from datetime import datetime, timezone
from html import escape

from flask import current_app
from flask_mail import Message

from application.infrastructure import celery, db, mail
from application.models import Notification, TelegramConnection
from application.telegram import TelegramAPIError, TelegramBotAPI


def enqueue_notification_delivery(notification_id):
    send_notification_email.delay(notification_id)
    send_notification_telegram.delay(notification_id)


def _utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


@celery.task(
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
    retry_kwargs={'max_retries': 5},
)
def send_notification_email(notification_id):
    notification = Notification.query.filter_by(id=notification_id).with_for_update(
        of=Notification
    ).first()
    if not notification or notification.email_sent_at:
        return

    link_html = ''
    if notification.url:
        safe_url = escape(notification.url, quote=True)
        link_html = f'<p><a href="{safe_url}">Открыть в сервисе</a></p>'
    html = (
        f'<p><strong>{escape(notification.title)}</strong></p>'
        f'<p>{escape(notification.message).replace(chr(10), "<br>")}</p>'
        f'{link_html}'
        f'<p style="color:#6c757d">Источник: {escape(notification.source_name)}</p>'
    )
    try:
        mail.send(Message(
            subject=f'{current_app.config["APP_NAME"]} — {notification.title}',
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
    retry_backoff=True,
    retry_jitter=True,
    retry_kwargs={'max_retries': 5},
)
def send_notification_telegram(notification_id):
    notification = Notification.query.filter_by(id=notification_id).with_for_update(
        of=Notification
    ).first()
    if not notification or notification.telegram_sent_at:
        return

    connection = TelegramConnection.query.filter_by(user_id=notification.user_id).first()
    if not connection:
        return

    text = f'{notification.title}\n\n{notification.message}'
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
