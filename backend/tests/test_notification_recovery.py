import socket
import time
from datetime import date
from unittest.mock import Mock

import pytest
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from application.infrastructure import db, mail
from application.models import Notification, TelegramConnection
from application.tasks import notifications
from .fixtures import app, test_user


@pytest.fixture
def notification(app, test_user):
    item = Notification(user_id=test_user.id, source_name='Test', payload_hash='0' * 64,
                        title='Title', message='Message')
    db.session.add(item)
    db.session.commit()
    return item


@pytest.mark.parametrize('task', [notifications.send_notification_email,
                                 notifications.send_notification_telegram])
def test_busy_row_fails_immediately_and_session_recovers(notification, task):
    notification_id = notification.id
    with db.engine.begin() as holder:
        holder.execute(text('SELECT id FROM notifications WHERE id=:id FOR UPDATE'),
                       {'id': notification_id})
        # Bound the regression test itself if NOWAIT is accidentally removed.
        db.session.execute(text("SET LOCAL lock_timeout = '2s'"))
        started = time.monotonic()
        with pytest.raises(OperationalError) as error:
            task._orig_run(notification_id)
        assert error.value.orig.pgcode == '55P03'
        assert time.monotonic() - started < 1
        assert db.session.execute(text('SELECT 1')).scalar() == 1


def assert_row_unlocked(notification_id):
    with db.engine.begin() as other:
        other.execute(text('SELECT id FROM notifications WHERE id=:id FOR UPDATE NOWAIT'),
                      {'id': notification_id})


def test_timeout_is_saved_and_does_not_block_telegram(app, notification, monkeypatch):
    notification_id = notification.id
    db.session.add(TelegramConnection(user_id=notification.user_id, chat_id=1234))
    db.session.commit()
    monkeypatch.setattr(notifications.mail, 'send', Mock(side_effect=TimeoutError('SMTP timed out')))
    with pytest.raises(TimeoutError):
        notifications.send_notification_email._orig_run(notification_id)
    assert_row_unlocked(notification_id)
    assert db.session.get(Notification, notification_id).email_error == 'SMTP timed out'
    assert db.session.get(Notification, notification_id).email_sent_at is None
    app.config['TELEGRAM_BOT_TOKEN'] = 'test-token'
    sent = Mock()
    monkeypatch.setattr(notifications.TelegramBotAPI, 'send_message', sent)
    notifications.send_notification_telegram.run(notification_id)
    assert sent.call_count == 1
    assert db.session.get(Notification, notification_id).telegram_sent_at is not None


def test_early_returns_release_row_lock(notification, monkeypatch):
    notification_id = notification.id
    notifications.send_notification_telegram.run(notification_id)  # No linked Telegram.
    assert_row_unlocked(notification_id)
    sent = Mock()
    monkeypatch.setattr(notifications.mail, 'send', sent)
    notifications.send_notification_email.run(notification_id)
    notifications.send_notification_email.run(notification_id)  # Already delivered.
    assert_row_unlocked(notification_id)
    assert sent.call_count == 1


def test_late_birthdays_use_original_date_in_both_channels(app, notification, monkeypatch):
    notification.system_key = 'birthday:2026-10-11:90:1'
    notification.title = 'Сегодня день рождения!'
    notification.message = 'Сегодня, 11.10, день рождения у ученика: Ученик.'
    db.session.add(TelegramConnection(user_id=notification.user_id, chat_id=1234))
    db.session.commit()
    monkeypatch.setattr(notifications, 'school_today', lambda: date(2026, 10, 14))
    app.config['TELEGRAM_BOT_TOKEN'] = 'test-token'
    emails, messages = [], []
    monkeypatch.setattr(notifications.mail, 'send', emails.append)
    monkeypatch.setattr(notifications.TelegramBotAPI, 'send_message',
                        lambda _bot, _chat, message: messages.append(message))
    notifications.send_notification_email.run(notification.id)
    notifications.send_notification_telegram.run(notification.id)
    for content in (emails[0].subject, emails[0].html, messages[0]):
        assert '11.10.2026' in content
        assert 'Сегодня' not in content
    assert 'с задержкой' in messages[0]
    assert notification.message.startswith('Сегодня')  # Stored original stays intact.


@pytest.mark.parametrize('use_ssl,use_tls', [(False, True), (True, False)])
def test_smtp_timeout_is_passed_and_success_closes_without_quit(app, monkeypatch, use_ssl, use_tls):
    app.config['MAIL_TIMEOUT'] = 7
    settings = app.extensions['mail']
    monkeypatch.setattr(settings, 'suppress', False)
    monkeypatch.setattr(settings, 'use_ssl', use_ssl)
    monkeypatch.setattr(settings, 'use_tls', use_tls)
    monkeypatch.setattr(settings, 'username', 'test')
    monkeypatch.setattr(settings, 'password', 'test')
    host = Mock()
    factory = Mock(return_value=host)
    monkeypatch.setattr('application.mail_delivery.smtplib.' + ('SMTP_SSL' if use_ssl else 'SMTP'), factory)
    with mail.connect():
        pass
    factory.assert_called_once_with(settings.server, settings.port, timeout=7)
    assert host.starttls.call_count == int(use_tls)
    host.login.assert_called_once_with('test', 'test')
    host.close.assert_called_once()
    host.quit.assert_not_called()


def test_smtp_login_failure_closes_socket(app, monkeypatch):
    settings = app.extensions['mail']
    for key, value in {'suppress': False, 'use_ssl': False, 'use_tls': False,
                       'username': 'test', 'password': 'test'}.items():
        monkeypatch.setattr(settings, key, value)
    host = Mock()
    host.login.side_effect = TimeoutError('login timed out')
    monkeypatch.setattr('application.mail_delivery.smtplib.SMTP', Mock(return_value=host))
    with pytest.raises(TimeoutError):
        with mail.connect():
            pass
    host.close.assert_called_once()


def test_unresponsive_smtp_server_is_bounded(app, monkeypatch):
    app.config['MAIL_TIMEOUT'] = 0.1
    settings = app.extensions['mail']
    with socket.socket() as server:
        server.bind(('127.0.0.1', 0))
        server.listen(1)  # Accept TCP but never send the SMTP greeting.
        for key, value in {'suppress': False, 'use_ssl': False,
                           'server': '127.0.0.1', 'port': server.getsockname()[1]}.items():
            monkeypatch.setattr(settings, key, value)
        started = time.monotonic()
        from smtplib import SMTPServerDisconnected
        with pytest.raises(SMTPServerDisconnected):
            with mail.connect():
                pass
        assert time.monotonic() - started < 2
