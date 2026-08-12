import hashlib
import json
import secrets
from datetime import datetime, timedelta, timezone

from flask import current_app
from sqlalchemy.exc import IntegrityError

from application.helpers.exceptions import LogicException
from application.infrastructure import db
from application.models import (
    Notification,
    Object,
    OAuthClient,
    TelegramConnection,
    TelegramLinkToken,
)


def _token_digest(token):
    return hashlib.sha256(token.encode('utf-8')).hexdigest()


def _utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def telegram_status(user):
    connection = TelegramConnection.query.filter_by(user_id=user.id).first()
    return {
        'configured': bool(
            current_app.config.get('TELEGRAM_BOT_TOKEN')
            and current_app.config.get('TELEGRAM_BOT_USERNAME')
        ),
        'connected': connection is not None,
        'username': connection.username if connection else None,
        'first_name': connection.first_name if connection else None,
        'linked_at': connection.linked_at.isoformat() if connection else None,
    }


def create_telegram_link(user):
    bot_username = current_app.config.get('TELEGRAM_BOT_USERNAME')
    if not current_app.config.get('TELEGRAM_BOT_TOKEN') or not bot_username:
        raise LogicException('Telegram-бот не настроен администратором.', 503)

    now = _utcnow()
    TelegramLinkToken.query.filter(
        (TelegramLinkToken.user_id == user.id) | (TelegramLinkToken.expires_at <= now)
    ).delete(synchronize_session=False)

    token = secrets.token_urlsafe(32)
    expires_at = now + timedelta(seconds=current_app.config['TELEGRAM_LINK_TOKEN_EXPIRES'])
    db.session.add(TelegramLinkToken(
        user_id=user.id,
        token_hash=_token_digest(token),
        expires_at=expires_at,
    ))
    db.session.commit()
    return {
        'url': f'https://t.me/{bot_username}?start={token}',
        'expires_at': expires_at.isoformat(),
    }


def connect_telegram(token, chat_id, username=None, first_name=None):
    now = _utcnow()
    link_token = TelegramLinkToken.query.filter_by(token_hash=_token_digest(token)).first()
    if not link_token or link_token.expires_at <= now:
        if link_token:
            db.session.delete(link_token)
            db.session.commit()
        raise LogicException(
            'Ссылка недействительна или устарела. Создайте новую ссылку в настройках личного кабинета.',
            400,
        )

    occupied = TelegramConnection.query.filter_by(chat_id=chat_id).first()
    if occupied and occupied.user_id != link_token.user_id:
        raise LogicException(
            'Этот Telegram уже привязан к другому аккаунту. Сначала отправьте боту /stop.',
            409,
        )

    connection = TelegramConnection.query.filter_by(user_id=link_token.user_id).first()
    if not connection:
        connection = occupied or TelegramConnection(user_id=link_token.user_id, chat_id=chat_id)
        db.session.add(connection)

    connection.chat_id = chat_id
    connection.username = (username or '')[:64] or None
    connection.first_name = (first_name or '')[:255] or None
    connection.linked_at = now
    TelegramLinkToken.query.filter_by(user_id=link_token.user_id).delete(synchronize_session=False)
    db.session.commit()
    return connection


def disconnect_telegram_for_user(user):
    deleted = TelegramConnection.query.filter_by(user_id=user.id).delete()
    TelegramLinkToken.query.filter_by(user_id=user.id).delete()
    db.session.commit()
    return bool(deleted)


def disconnect_telegram_chat(chat_id):
    deleted = TelegramConnection.query.filter_by(chat_id=chat_id).delete()
    db.session.commit()
    return bool(deleted)


def notification_payload_hash(recipient_sub, title, message, url):
    canonical = json.dumps(
        {
            'recipient_sub': recipient_sub,
            'title': title,
            'message': message,
            'url': url,
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(',', ':'),
    )
    return hashlib.sha256(canonical.encode('utf-8')).hexdigest()


def create_external_notification(client, data, idempotency_key):
    payload_hash = notification_payload_hash(
        data['recipient_sub'], data['title'], data['message'], data.get('url')
    )
    existing = Notification.query.filter_by(
        source_client_id=client.client_id,
        idempotency_key=idempotency_key,
    ).first()
    if existing:
        if existing.payload_hash != payload_hash:
            raise LogicException(
                'Этот Idempotency-Key уже использован с другим содержимым.', 409
            )
        return existing, False

    identity = Object.query.filter_by(
        sso_subject=data['recipient_sub'], deleted_at=None
    ).first()
    user = identity.identity_user if identity else None
    if not user:
        raise LogicException(
            'Объект-получатель с таким sub не найден или не привязан к аккаунту.',
            404,
            field='recipient_sub',
        )
    if user.role not in (client.allowed_roles or []):
        raise LogicException('Роль получателя запрещена для этого API-клиента.', 403)

    notification = Notification(
        user_id=user.id,
        source_client_id=client.client_id,
        source_name=client.name,
        idempotency_key=idempotency_key,
        payload_hash=payload_hash,
        title=data['title'],
        message=data['message'],
        url=data.get('url'),
    )
    db.session.add(notification)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        existing = Notification.query.filter_by(
            source_client_id=client.client_id,
            idempotency_key=idempotency_key,
        ).first()
        if not existing or existing.payload_hash != payload_hash:
            raise LogicException(
                'Этот Idempotency-Key уже использован с другим содержимым.', 409
            )
        return existing, False
    return notification, True


def get_notification_client(client_id, client_secret):
    client = OAuthClient.query.filter_by(client_id=client_id, is_active=True).first()
    if not (
        client
        and client.is_confidential
        and client.can_send_notifications
        and client.check_client_secret(client_secret)
    ):
        raise LogicException('Неверные данные API-клиента.', 401)
    return client
