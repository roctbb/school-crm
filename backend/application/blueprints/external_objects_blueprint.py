from functools import wraps

from flask import Blueprint, jsonify, request

from application.helpers.exceptions import LogicException
from application.infrastructure import limiter
from application.methods.external_objects_methods import get_external_objects
from application.models import OAuthClient


external_objects_blueprint = Blueprint('external_objects', __name__)


def requires_object_api_client(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        authorization = request.authorization
        client = None
        if authorization and authorization.type.lower() == 'basic':
            client = OAuthClient.query.filter_by(
                client_id=authorization.username, is_active=True,
            ).first()
        if not (client and client.is_confidential
                and client.check_client_secret(authorization.password)):
            response = jsonify({'message': 'Неверные данные API-клиента.'})
            response.status_code = 401
            response.headers['WWW-Authenticate'] = 'Basic realm="external-objects"'
            return response
        return func(client, *args, **kwargs)

    return wrapper


@external_objects_blueprint.after_request
def prevent_caching(response):
    response.headers['Cache-Control'] = 'no-store'
    return response


@external_objects_blueprint.route('/external/objects/<string:type_code>', methods=['GET'])
@limiter.limit('600 per minute')
@requires_object_api_client
def external_objects(client, type_code):
    if type_code not in (client.allowed_object_types or []):
        raise LogicException('Клиенту запрещено читать этот тип объектов.', 403)
    return jsonify(get_external_objects(type_code, request.args))
