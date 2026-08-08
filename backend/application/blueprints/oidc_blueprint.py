from authlib.integrations.flask_oauth2 import current_token
from flask import Blueprint, current_app, jsonify, request

from application.helpers.decorators import requires_roles, requires_user, validate_request_with
from application.helpers.exceptions import LogicException
from application.infrastructure import limiter
from application.methods import (
    authorize_oauth_request,
    authorization_requires_consent,
    create_oauth_client,
    deny_oauth_request,
    get_oauth_client,
    get_oauth_clients,
    rotate_oauth_client_secret,
    update_oauth_client,
    validate_authorization_request,
    validate_logout_request,
)
from application.oidc import (
    authorization_server,
    get_oidc_issuer,
    get_public_jwks,
    oidc_user_info,
    require_oauth,
)
from application.presenters import present_oauth_client
from application.validators import validate_oauth_client


oidc_blueprint = Blueprint('oidc', __name__, url_prefix='/oauth')
oidc_public_blueprint = Blueprint('oidc_public', __name__)


@oidc_public_blueprint.route('/.well-known/openid-configuration', methods=['GET'])
def openid_configuration():
    issuer = get_oidc_issuer()
    return jsonify({
        'issuer': issuer,
        'authorization_endpoint': f'{issuer}/oauth/authorize',
        'token_endpoint': f'{issuer}/api/oauth/token',
        'userinfo_endpoint': f'{issuer}/api/oauth/userinfo',
        'jwks_uri': f'{issuer}/api/oauth/jwks',
        'revocation_endpoint': f'{issuer}/api/oauth/revoke',
        'end_session_endpoint': f'{issuer}/oauth/logout',
        'response_types_supported': ['code'],
        'grant_types_supported': ['authorization_code', 'refresh_token'],
        'subject_types_supported': ['public'],
        'id_token_signing_alg_values_supported': ['RS256'],
        'token_endpoint_auth_methods_supported': [
            'client_secret_basic', 'client_secret_post', 'none',
        ],
        'scopes_supported': ['openid', 'profile', 'email', 'roles', 'offline_access'],
        'claims_supported': [
            'iss', 'sub', 'aud', 'exp', 'iat', 'auth_time', 'nonce',
            'name', 'preferred_username', 'email', 'email_verified', 'role', 'roles',
        ],
        'code_challenge_methods_supported': ['S256'],
    })


@oidc_blueprint.route('/jwks', methods=['GET'])
def oidc_jwks():
    response = jsonify(get_public_jwks())
    response.headers['Cache-Control'] = 'public, max-age=300'
    return response


@oidc_blueprint.route('/token', methods=['POST'])
@limiter.limit('240 per minute')
def oidc_token():
    return authorization_server.create_token_response()


@oidc_blueprint.route('/revoke', methods=['POST'])
@limiter.limit('240 per minute')
def oidc_revoke():
    return authorization_server.create_endpoint_response('revocation')


@oidc_blueprint.route('/userinfo', methods=['GET', 'POST'])
@require_oauth('openid')
def oidc_userinfo():
    return jsonify(dict(oidc_user_info(current_token.user, current_token.scope)))


@oidc_blueprint.route('/authorize/request', methods=['GET'])
@requires_user
@limiter.limit('240 per minute')
def oidc_authorization_request(user):
    validated = validate_authorization_request(request.args, user)
    client = validated['client']
    return jsonify({
        'client': {
            'client_id': client.client_id,
            'name': client.name,
            'description': client.description or '',
        },
        'scopes': validated['scopes'],
        'user': {
            'name': user.name,
            'email': user.email,
            'role': user.role,
        },
        'requires_consent': authorization_requires_consent(user, validated),
    })


@oidc_blueprint.route('/authorize', methods=['POST'])
@requires_user
@limiter.limit('120 per minute')
def oidc_authorize(user):
    data = request.get_json(silent=True) or {}
    decision = data.pop('decision', None)
    if not isinstance(decision, bool):
        raise LogicException("Поле decision должно быть boolean.", 422)
    redirect_uri = authorize_oauth_request(user, data) if decision else deny_oauth_request(user, data)
    return jsonify({'redirect_uri': redirect_uri})


@oidc_blueprint.route('/logout/request', methods=['GET'])
def oidc_logout_request():
    redirect_uri = validate_logout_request(
        request.args.get('client_id'),
        request.args.get('post_logout_redirect_uri'),
        request.args.get('id_token_hint'),
        request.args.get('state'),
    )
    return jsonify({'redirect_uri': redirect_uri or current_app.config['BASE_URL']})


@oidc_blueprint.route('/clients', methods=['GET'])
@requires_user
@requires_roles(['admin'])
def oauth_clients_endpoint(user):
    return jsonify([present_oauth_client(client) for client in get_oauth_clients()])


@oidc_blueprint.route('/clients', methods=['POST'])
@requires_user
@requires_roles(['admin'])
@validate_request_with(validate_oauth_client)
def create_oauth_client_endpoint(validated_data, user):
    client, secret = create_oauth_client(user, validated_data)
    result = present_oauth_client(client)
    result['client_secret'] = secret
    return jsonify(result), 201


@oidc_blueprint.route('/clients/<int:client_pk>', methods=['PUT'])
@requires_user
@requires_roles(['admin'])
@validate_request_with(validate_oauth_client)
def update_oauth_client_endpoint(validated_data, user, client_pk):
    client = get_oauth_client_by_pk(client_pk)
    client, secret = update_oauth_client(client, validated_data)
    result = present_oauth_client(client)
    if secret:
        result['client_secret'] = secret
    return jsonify(result)


@oidc_blueprint.route('/clients/<int:client_pk>/rotate-secret', methods=['POST'])
@requires_user
@requires_roles(['admin'])
def rotate_oauth_client_secret_endpoint(user, client_pk):
    client = get_oauth_client_by_pk(client_pk)
    client, secret = rotate_oauth_client_secret(client)
    result = present_oauth_client(client)
    result['client_secret'] = secret
    return jsonify(result)


def get_oauth_client_by_pk(client_pk):
    from application.models import OAuthClient

    client = OAuthClient.query.filter_by(id=client_pk).first()
    if not client:
        raise LogicException("OIDC-клиент не найден.", 404)
    return client
