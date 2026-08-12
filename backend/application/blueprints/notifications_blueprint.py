from functools import wraps

from flask import Blueprint, jsonify, request

from application.helpers.decorators import requires_user
from application.helpers.exceptions import LogicException
from application.infrastructure import limiter
from application.methods import (
    create_external_notification,
    create_telegram_link,
    disconnect_telegram_for_user,
    get_notification_client,
    telegram_status,
)
from application.tasks.notifications import enqueue_notification_delivery
from application.validators import validate_external_notification


notifications_blueprint = Blueprint('notifications', __name__)


def requires_notification_client(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        authorization = request.authorization
        if not authorization or authorization.type.lower() != 'basic':
            response = jsonify({'message': 'Требуется HTTP Basic API-аутентификация.'})
            response.status_code = 401
            response.headers['WWW-Authenticate'] = 'Basic realm="notifications"'
            return response
        try:
            client = get_notification_client(authorization.username, authorization.password)
        except LogicException as error:
            if error.code != 401:
                raise
            response = jsonify({'message': error.message})
            response.status_code = 401
            response.headers['WWW-Authenticate'] = 'Basic realm="notifications"'
            return response
        return func(client, *args, **kwargs)

    return wrapper


@notifications_blueprint.route('/settings/notifications/telegram', methods=['GET'])
@requires_user
def telegram_settings(user):
    return jsonify(telegram_status(user))


@notifications_blueprint.route('/settings/notifications/telegram/link', methods=['POST'])
@requires_user
@limiter.limit('20 per hour')
def telegram_link(user):
    return jsonify(create_telegram_link(user)), 201


@notifications_blueprint.route('/settings/notifications/telegram', methods=['DELETE'])
@requires_user
def telegram_disconnect(user):
    return jsonify({'disconnected': disconnect_telegram_for_user(user)})


@notifications_blueprint.route('/external/notifications', methods=['POST'])
@limiter.limit('600 per minute')
@requires_notification_client
def external_notification(client):
    data = validate_external_notification(
        request.get_json(silent=True), request.headers.get('Idempotency-Key')
    )
    notification, created = create_external_notification(
        client, data, request.headers['Idempotency-Key']
    )
    try:
        enqueue_notification_delivery(notification.id)
    except Exception as error:
        raise LogicException(
            'Уведомление сохранено, но очередь доставки временно недоступна. Повторите запрос.',
            503,
        ) from error
    return jsonify({
        'id': notification.id,
        'status': 'queued',
        'idempotent_replay': not created,
    }), 202 if created else 200
