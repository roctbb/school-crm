import re
import secrets
import time
from datetime import timedelta
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from flask import current_app

from application.helpers.decorators import transaction
from application.helpers.exceptions import LogicException
from application.infrastructure import bcrypt, db
from application.models import OAuthAuthorizationCode, OAuthClient, OAuthToken
from application.oidc import get_client_id_from_id_token_hint, token_digest, utcnow


PKCE_PATTERN = re.compile(r'^[A-Za-z0-9._~-]{43,128}$')
SUPPORTED_SCOPES = {'openid', 'profile', 'email', 'roles', 'offline_access'}


def get_oauth_clients():
    return OAuthClient.query.order_by(OAuthClient.name, OAuthClient.id).all()


def get_oauth_client(client_id, include_inactive=False):
    query = OAuthClient.query.filter_by(client_id=client_id)
    if not include_inactive:
        query = query.filter_by(is_active=True)
    client = query.first()
    if not client:
        raise LogicException("OIDC-клиент не найден.", 404)
    return client


def _generate_client_secret():
    return secrets.token_urlsafe(48)


@transaction
def create_oauth_client(user, data):
    if OAuthClient.query.filter_by(client_id=data['client_id']).first():
        raise LogicException("Клиент с таким client_id уже существует.", 409, field='client_id')

    client_secret = _generate_client_secret() if data['is_confidential'] else None
    client = OAuthClient(
        client_id=data['client_id'],
        client_secret_hash=(
            bcrypt.generate_password_hash(client_secret).decode('utf-8') if client_secret else None
        ),
        name=data['name'],
        description=data.get('description'),
        redirect_uris=data['redirect_uris'],
        post_logout_redirect_uris=data['post_logout_redirect_uris'],
        allowed_scopes=data['allowed_scopes'],
        allowed_roles=data['allowed_roles'],
        is_confidential=data['is_confidential'],
        is_active=data['is_active'],
        creator_id=user.id,
    )
    db.session.add(client)
    return client, client_secret


@transaction
def update_oauth_client(client, data):
    if data['client_id'] != client.client_id:
        raise LogicException("client_id существующего клиента изменять нельзя.", 409, field='client_id')

    revoke_tokens = (
        client.is_confidential != data['is_confidential']
        or set(client.allowed_scopes or []) != set(data['allowed_scopes'])
        or set(client.allowed_roles or []) != set(data['allowed_roles'])
        or not data['is_active']
    )

    new_secret = None
    if data['is_confidential'] and not client.client_secret_hash:
        new_secret = _generate_client_secret()
        client.client_secret_hash = bcrypt.generate_password_hash(new_secret).decode('utf-8')
    elif not data['is_confidential']:
        client.client_secret_hash = None

    client.name = data['name']
    client.description = data.get('description')
    client.redirect_uris = data['redirect_uris']
    client.post_logout_redirect_uris = data['post_logout_redirect_uris']
    client.allowed_scopes = data['allowed_scopes']
    client.allowed_roles = data['allowed_roles']
    client.is_confidential = data['is_confidential']
    client.is_active = data['is_active']

    OAuthAuthorizationCode.query.filter_by(client_id=client.client_id).delete()
    if revoke_tokens:
        revoked_at = int(time.time())
        OAuthToken.query.filter_by(client_id=client.client_id).update({
            OAuthToken.access_token_revoked_at: revoked_at,
            OAuthToken.refresh_token_revoked_at: revoked_at,
        })
    return client, new_secret


@transaction
def rotate_oauth_client_secret(client):
    if not client.is_confidential:
        raise LogicException("У публичного клиента нет client secret.", 409)
    secret = _generate_client_secret()
    client.client_secret_hash = bcrypt.generate_password_hash(secret).decode('utf-8')
    OAuthAuthorizationCode.query.filter_by(client_id=client.client_id).delete()
    revoked_at = int(time.time())
    OAuthToken.query.filter_by(client_id=client.client_id).update({
        OAuthToken.access_token_revoked_at: revoked_at,
        OAuthToken.refresh_token_revoked_at: revoked_at,
    })
    return client, secret


def validate_authorization_request(data, user):
    client_id = data.get('client_id')
    client = get_oauth_client(client_id)

    if data.get('response_type') != 'code':
        raise LogicException("Поддерживается только response_type=code.", 400)

    redirect_uri = data.get('redirect_uri')
    if not redirect_uri or not client.check_redirect_uri(redirect_uri):
        raise LogicException("Некорректный redirect_uri.", 400)

    state = data.get('state', '')
    nonce = data.get('nonce', '')
    if not isinstance(state, str) or not 16 <= len(state) <= 512:
        raise LogicException("Параметр state обязателен и должен содержать от 16 до 512 символов.", 400)
    if not isinstance(nonce, str) or not 16 <= len(nonce) <= 255:
        raise LogicException("Параметр nonce обязателен и должен содержать от 16 до 255 символов.", 400)

    scopes = data.get('scope', '').split()
    if 'openid' not in scopes or not scopes:
        raise LogicException("OIDC-запрос должен содержать scope openid.", 400)
    if set(scopes) - set(client.allowed_scopes or []) or set(scopes) - SUPPORTED_SCOPES:
        raise LogicException("Запрошены недоступные scopes.", 400)

    code_challenge = data.get('code_challenge', '')
    if not PKCE_PATTERN.fullmatch(code_challenge):
        raise LogicException("Некорректный или отсутствующий PKCE code_challenge.", 400)
    if data.get('code_challenge_method') != 'S256':
        raise LogicException("Поддерживается только PKCE code_challenge_method=S256.", 400)

    if user.role not in (client.allowed_roles or []):
        raise LogicException("Вашей роли запрещён доступ к этому сервису.", 403)

    return {
        'client': client,
        'client_id': client.client_id,
        'redirect_uri': redirect_uri,
        'scope': ' '.join(scopes),
        'scopes': scopes,
        'state': state,
        'nonce': nonce,
        'code_challenge': code_challenge,
        'code_challenge_method': 'S256',
    }


def _add_redirect_params(uri, params):
    parsed = urlsplit(uri)
    query = parse_qsl(parsed.query, keep_blank_values=True)
    query.extend(params.items())
    return urlunsplit((parsed.scheme, parsed.netloc, parsed.path, urlencode(query), parsed.fragment))


@transaction
def authorize_oauth_request(user, data):
    validated = validate_authorization_request(data, user)
    duplicate_nonce = OAuthAuthorizationCode.query.filter(
        OAuthAuthorizationCode.client_id == validated['client_id'],
        OAuthAuthorizationCode.nonce == validated['nonce'],
        OAuthAuthorizationCode.expires_at > utcnow(),
    ).first()
    if duplicate_nonce:
        raise LogicException("Параметр nonce уже использован.", 400)

    OAuthAuthorizationCode.query.filter(
        OAuthAuthorizationCode.expires_at <= utcnow()
    ).delete(synchronize_session=False)

    code = secrets.token_urlsafe(48)
    db.session.add(OAuthAuthorizationCode(
        code_hash=token_digest(code),
        client_id=validated['client_id'],
        user_id=user.id,
        redirect_uri=validated['redirect_uri'],
        scope=validated['scope'],
        nonce=validated['nonce'],
        code_challenge=validated['code_challenge'],
        code_challenge_method=validated['code_challenge_method'],
        auth_time=int(time.time()),
        expires_at=utcnow() + timedelta(seconds=current_app.config['OIDC_AUTH_CODE_EXPIRES']),
    ))
    return _add_redirect_params(validated['redirect_uri'], {
        'code': code,
        'state': validated['state'],
    })


def deny_oauth_request(user, data):
    validated = validate_authorization_request(data, user)
    return _add_redirect_params(validated['redirect_uri'], {
        'error': 'access_denied',
        'error_description': 'The user denied the request.',
        'state': validated['state'],
    })


def validate_logout_request(client_id, post_logout_redirect_uri, id_token_hint=None, state=None):
    if id_token_hint:
        try:
            hinted_client_id = get_client_id_from_id_token_hint(id_token_hint)
        except Exception as error:
            raise LogicException("Некорректный id_token_hint.", 400) from error
        if client_id and client_id != hinted_client_id:
            raise LogicException("client_id не совпадает с id_token_hint.", 400)
        client_id = hinted_client_id

    if not client_id:
        raise LogicException("Нужен client_id или id_token_hint.", 400)
    client = get_oauth_client(client_id)
    if not post_logout_redirect_uri:
        return None
    if post_logout_redirect_uri not in (client.post_logout_redirect_uris or []):
        raise LogicException("Некорректный post_logout_redirect_uri.", 400)
    if state:
        if not isinstance(state, str) or len(state) > 512:
            raise LogicException("Некорректный state.", 400)
        return _add_redirect_params(post_logout_redirect_uri, {'state': state})
    return post_logout_redirect_uri
