import base64
import importlib
from datetime import datetime, timedelta, timezone

import pytest
from flask_jwt_extended import create_access_token

from application.infrastructure import bcrypt, db
from application.methods.notification_methods import (
    connect_telegram,
    create_telegram_link,
    disconnect_telegram_chat,
    telegram_status,
)
from application.models import (
    Notification, Object, ObjectType, OAuthClient, TelegramConnection, TelegramLinkToken, User,
)
from application.tasks.notifications import send_notification_email, send_notification_telegram
from .fixtures import *


def _basic_auth(client_id, secret):
    value = base64.b64encode(f'{client_id}:{secret}'.encode()).decode()
    return {'Authorization': f'Basic {value}'}


def _notification_client(secret='notification-secret', enabled=True):
    client = OAuthClient(
        client_id='wallet-service',
        client_secret_hash=bcrypt.generate_password_hash(secret).decode(),
        name='Кошелёк мотивашек',
        redirect_uris=['https://wallet.example.test/callback'],
        post_logout_redirect_uris=[],
        allowed_scopes=['openid', 'profile'],
        allowed_roles=['student'],
        is_confidential=True,
        is_active=True,
        can_send_notifications=enabled,
    )
    db.session.add(client)
    db.session.commit()
    return client, secret


def _attach_identity(user, type_code='students'):
    object_type = ObjectType.query.filter_by(code=type_code).first()
    if not object_type:
        object_type = ObjectType(name=type_code.title(), code=type_code)
    identity = Object(name=f'{user.name} CRM Object', type=object_type)
    identity.owners.append(user)
    user.identity_object = identity
    db.session.add_all([object_type, identity])
    db.session.commit()
    return identity


def test_user_creates_one_time_telegram_link_and_bot_connects(app, test_user):
    app.config.update(
        TELEGRAM_BOT_TOKEN='test-token',
        TELEGRAM_BOT_USERNAME='school_crm_bot',
        TELEGRAM_LINK_TOKEN_EXPIRES=600,
    )
    link = create_telegram_link(test_user)
    raw_token = link['url'].split('start=', 1)[1]
    stored = TelegramLinkToken.query.one()
    assert raw_token not in stored.token_hash
    assert telegram_status(test_user)['connected'] is False

    connection = connect_telegram(raw_token, 123456, 'student_tg', 'Student')
    assert connection.user_id == test_user.id
    assert telegram_status(test_user)['username'] == 'student_tg'
    assert TelegramLinkToken.query.count() == 0

    with pytest.raises(Exception) as replay:
        connect_telegram(raw_token, 123456, 'student_tg', 'Student')
    assert getattr(replay.value, 'code', None) == 400
    assert disconnect_telegram_chat(123456) is True
    assert telegram_status(test_user)['connected'] is False


def test_expired_telegram_link_is_rejected(app, test_user):
    token = 'expired-token'
    from application.methods.notification_methods import _token_digest

    db.session.add(TelegramLinkToken(
        user_id=test_user.id,
        token_hash=_token_digest(token),
        expires_at=datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(seconds=1),
    ))
    db.session.commit()
    with pytest.raises(Exception) as result:
        connect_telegram(token, 123456)
    assert getattr(result.value, 'code', None) == 400


def test_external_notification_queues_email_and_telegram_once(
        client, test_user, monkeypatch):
    test_user.role = 'student'
    identity = _attach_identity(test_user)
    db.session.commit()
    oauth_client, secret = _notification_client()
    dispatched = []
    blueprint_module = importlib.import_module('application.blueprints.notifications_blueprint')
    monkeypatch.setattr(
        blueprint_module,
        'enqueue_notification_delivery',
        lambda notification_id: dispatched.append(notification_id),
    )
    headers = {
        **_basic_auth(oauth_client.client_id, secret),
        'Idempotency-Key': 'wallet-operation-1234',
    }
    payload = {
        'recipient_sub': identity.sso_subject,
        'title': 'Начислены мотивашки',
        'message': 'Начислено 50 мотивашек.',
        'url': 'https://wallet.example.test/operations/42',
    }

    response = client.post('/api/external/notifications', json=payload, headers=headers)
    assert response.status_code == 202, response.get_json()
    notification_id = response.get_json()['id']
    assert dispatched == [notification_id]
    notification = db.session.get(Notification, notification_id)
    assert notification.user_id == test_user.id
    assert notification.source_client_id == oauth_client.client_id

    replay = client.post('/api/external/notifications', json=payload, headers=headers)
    assert replay.status_code == 200
    assert replay.get_json()['idempotent_replay'] is True
    assert Notification.query.count() == 1
    assert dispatched == [notification_id, notification_id]

    conflict = client.post(
        '/api/external/notifications',
        json={**payload, 'message': 'Другое сообщение'},
        headers=headers,
    )
    assert conflict.status_code == 409


def test_notification_api_rejects_unauthorized_client_and_unknown_user(client, test_user):
    test_user.role = 'student'
    identity = _attach_identity(test_user)
    db.session.commit()
    oauth_client, secret = _notification_client(enabled=False)
    headers = {
        **_basic_auth(oauth_client.client_id, secret),
        'Idempotency-Key': 'wallet-operation-9999',
    }
    payload = {
        'recipient_sub': identity.sso_subject,
        'title': 'Title',
        'message': 'Message',
    }
    forbidden = client.post('/api/external/notifications', json=payload, headers=headers)
    assert forbidden.status_code == 401
    assert forbidden.headers['WWW-Authenticate'].startswith('Basic ')

    oauth_client.can_send_notifications = True
    db.session.commit()
    unknown = client.post(
        '/api/external/notifications',
        json={**payload, 'recipient_sub': '11111111-1111-4111-8111-111111111111'},
        headers=headers,
    )
    assert unknown.status_code == 404

    teacher = User(name='Teacher', email='teacher@example.test', role='teacher')
    db.session.add(teacher)
    db.session.commit()
    teacher_identity = _attach_identity(teacher, 'teachers')
    wrong_role = client.post(
        '/api/external/notifications',
        json={**payload, 'recipient_sub': teacher_identity.sso_subject},
        headers={**headers, 'Idempotency-Key': 'wallet-operation-teacher'},
    )
    assert wrong_role.status_code == 403


def test_telegram_settings_endpoints(client, app, test_user):
    app.config.update(
        TELEGRAM_BOT_TOKEN='test-token',
        TELEGRAM_BOT_USERNAME='school_crm_bot',
    )
    headers = {'Authorization': f'Bearer {create_access_token(identity=str(test_user.id))}'}
    status = client.get('/api/settings/notifications/telegram', headers=headers)
    assert status.status_code == 200
    assert status.get_json() == {
        'configured': True,
        'connected': False,
        'username': None,
        'first_name': None,
        'linked_at': None,
    }
    link = client.post('/api/settings/notifications/telegram/link', headers=headers)
    assert link.status_code == 201
    assert link.get_json()['url'].startswith('https://t.me/school_crm_bot?start=')


def test_celery_tasks_deliver_both_channels(app, test_user, monkeypatch):
    app.config['TELEGRAM_BOT_TOKEN'] = 'test-token'
    notification = Notification(
        user_id=test_user.id,
        source_name='Соревнования',
        payload_hash='0' * 64,
        title='Новый результат',
        message='Вы заняли первое место.',
        url='https://contest.example.test/results/42',
    )
    connection = TelegramConnection(
        user_id=test_user.id,
        chat_id=123456,
        username='student_tg',
    )
    db.session.add_all([notification, connection])
    db.session.commit()

    emails = []
    telegram_messages = []
    monkeypatch.setattr(
        'application.tasks.notifications.mail.send',
        lambda message: emails.append(message),
    )
    monkeypatch.setattr(
        'application.tasks.notifications.TelegramBotAPI.send_message',
        lambda _bot, chat_id, text: telegram_messages.append((chat_id, text)),
    )

    send_notification_email.run(notification.id)
    send_notification_telegram.run(notification.id)
    db.session.refresh(notification)

    assert len(emails) == 1
    assert emails[0].recipients == [test_user.email]
    assert notification.email_sent_at is not None
    assert telegram_messages == [(
        123456,
        'Новый результат\n\nВы заняли первое место.\n\n'
        'https://contest.example.test/results/42\n\nИсточник: Соревнования',
    )]
    assert notification.telegram_sent_at is not None
