import fcntl
import hashlib
import os
import time
from datetime import datetime, timedelta, timezone

from authlib.integrations.flask_oauth2 import AuthorizationServer, ResourceProtector
from authlib.oauth2.rfc6749.grants import AuthorizationCodeGrant, RefreshTokenGrant
from authlib.oauth2.rfc6749.errors import InvalidGrantError
from authlib.oauth2.rfc6749.hooks import hooked
from authlib.oauth2.rfc6750 import BearerTokenValidator
from authlib.oauth2.rfc7009 import RevocationEndpoint
from authlib.oauth2.rfc7636 import CodeChallenge
from authlib.oidc.core import UserInfo
from authlib.oidc.core.grants import OpenIDCode
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from flask import current_app
from joserfc import jwt
from joserfc.jwk import RSAKey

from application.infrastructure import db
from application.models import OAuthAuthorizationCode, OAuthClient, OAuthToken, User


authorization_server = AuthorizationServer()
require_oauth = ResourceProtector()


def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def token_digest(value):
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


def get_oidc_issuer():
    return current_app.config['OIDC_ISSUER'].rstrip('/')


def _load_signing_key():
    key_path = current_app.config['OIDC_KEY_PATH']
    os.makedirs(os.path.dirname(key_path) or '.', exist_ok=True)
    lock_path = f'{key_path}.lock'

    with open(lock_path, 'a+', encoding='utf-8') as lock_file:
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
        if not os.path.exists(key_path):
            private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
            pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),
            )
            temporary_path = f'{key_path}.{os.getpid()}.tmp'
            with open(temporary_path, 'wb') as key_file:
                key_file.write(pem)
            os.chmod(temporary_path, 0o600)
            os.replace(temporary_path, key_path)

        with open(key_path, 'rb') as key_file:
            pem = key_file.read()

    key = RSAKey.import_key(pem)
    return pem, key.thumbprint(), key


def get_public_jwks():
    _pem, kid, key = _load_signing_key()
    public_key = key.as_dict(private=False)
    public_key.update({'kid': kid, 'use': 'sig', 'alg': 'RS256'})
    return {'keys': [public_key]}


def get_client_id_from_id_token_hint(id_token_hint):
    _pem, _kid, key = _load_signing_key()
    decoded = jwt.decode(id_token_hint, key, algorithms=['RS256'])
    claims = decoded.claims
    if claims.get('iss') != get_oidc_issuer() or not isinstance(claims.get('sub'), str):
        raise ValueError('Invalid ID token claims')

    audience = claims.get('aud')
    if isinstance(audience, str):
        return audience
    if isinstance(audience, list) and len(audience) == 1 and isinstance(audience[0], str):
        return audience[0]
    raise ValueError('Invalid ID token audience')


def query_client(client_id):
    return OAuthClient.query.filter_by(client_id=client_id, is_active=True).first()


def save_token(token, request):
    issued_at = int(time.time())
    refresh_token = token.get('refresh_token')
    OAuthToken.query.filter(
        OAuthToken.issued_at + OAuthToken.expires_in <= issued_at,
        db.or_(
            OAuthToken.refresh_expires_at.is_(None),
            OAuthToken.refresh_expires_at <= issued_at,
        ),
    ).delete(synchronize_session=False)
    item = OAuthToken(
        client_id=request.client.client_id,
        user_id=request.user.id,
        access_token_hash=token_digest(token['access_token']),
        refresh_token_hash=token_digest(refresh_token) if refresh_token else None,
        token_type=token.get('token_type', 'Bearer'),
        scope=token.get('scope', ''),
        issued_at=issued_at,
        expires_in=token.get('expires_in', current_app.config['OIDC_ACCESS_TOKEN_EXPIRES']),
        refresh_expires_at=(
            issued_at + current_app.config['OIDC_REFRESH_TOKEN_EXPIRES'] if refresh_token else None
        ),
    )
    db.session.add(item)


class OIDCAuthorizationCodeGrant(AuthorizationCodeGrant):
    TOKEN_ENDPOINT_AUTH_METHODS = ['client_secret_basic', 'client_secret_post', 'none']

    def save_authorization_code(self, code, request):
        item = OAuthAuthorizationCode(
            code_hash=token_digest(code),
            client_id=request.client.client_id,
            user_id=request.user.id,
            redirect_uri=request.payload.redirect_uri,
            scope=request.scope,
            nonce=request.payload.data.get('nonce'),
            code_challenge=request.payload.data.get('code_challenge'),
            code_challenge_method=request.payload.data.get('code_challenge_method', 'S256'),
            auth_time=int(time.time()),
            expires_at=utcnow() + timedelta(seconds=current_app.config['OIDC_AUTH_CODE_EXPIRES']),
        )
        db.session.add(item)
        db.session.commit()

    def query_authorization_code(self, code, client):
        return OAuthAuthorizationCode.query.filter(
            OAuthAuthorizationCode.code_hash == token_digest(code),
            OAuthAuthorizationCode.client_id == client.client_id,
            OAuthAuthorizationCode.expires_at > utcnow(),
        ).with_for_update(of=OAuthAuthorizationCode).first()

    def delete_authorization_code(self, authorization_code):
        db.session.delete(authorization_code)
        db.session.commit()

    def authenticate_user(self, authorization_code):
        return authorization_code.user

    @hooked
    def create_token_response(self):
        client = self.request.client
        authorization_code = self.request.authorization_code
        user = self.authenticate_user(authorization_code)
        if not user:
            raise InvalidGrantError("There is no 'user' for this code.")

        self.request.user = user
        scope = authorization_code.get_scope()
        token = self.generate_token(
            user=user,
            scope=scope,
            include_refresh_token=(
                client.check_grant_type('refresh_token')
                and 'offline_access' in set((scope or '').split())
            ),
        )
        self.save_token(token)
        self.delete_authorization_code(authorization_code)
        return 200, token, self.TOKEN_RESPONSE_HEADER


class OIDCRefreshTokenGrant(RefreshTokenGrant):
    TOKEN_ENDPOINT_AUTH_METHODS = ['client_secret_basic', 'client_secret_post', 'none']
    INCLUDE_NEW_REFRESH_TOKEN = True

    def authenticate_refresh_token(self, refresh_token):
        token = OAuthToken.query.filter_by(
            refresh_token_hash=token_digest(refresh_token)
        ).with_for_update(of=OAuthToken).first()
        return token if (
            token
            and token.is_refresh_token_active()
            and token.client.is_active
            and token.user.role in (token.client.allowed_roles or [])
        ) else None

    def authenticate_user(self, refresh_token):
        return refresh_token.user

    def revoke_old_credential(self, refresh_token):
        revoked_at = int(time.time())
        refresh_token.access_token_revoked_at = revoked_at
        refresh_token.refresh_token_revoked_at = revoked_at
        db.session.commit()


def oidc_user_info(user, scope):
    scopes = set((scope or '').split())
    info = UserInfo(sub=user.sso_subject)
    if 'profile' in scopes:
        info.update({
            'name': user.name,
            'preferred_username': user.email,
        })
    if 'email' in scopes:
        info.update({
            'email': user.email,
            'email_verified': False,
        })
    if 'roles' in scopes:
        info.update({
            'role': user.role,
            'roles': [user.role],
        })
    return info


class CRMOpenIDCode(OpenIDCode):
    def resolve_client_private_key(self, client):
        _pem, _kid, key = _load_signing_key()
        return key

    def get_client_algorithm(self, client):
        return 'RS256'

    def get_client_claims(self, client):
        now = int(time.time())
        return {
            'iss': get_oidc_issuer(),
            'aud': [client.client_id],
            'iat': now,
            'exp': now + current_app.config['OIDC_ID_TOKEN_EXPIRES'],
        }

    def get_encode_header(self, client):
        _pem, kid, _key = _load_signing_key()
        return {'alg': 'RS256', 'kid': kid, 'typ': 'JWT'}

    def exists_nonce(self, nonce, request):
        return OAuthAuthorizationCode.query.filter(
            OAuthAuthorizationCode.client_id == request.payload.client_id,
            OAuthAuthorizationCode.nonce == nonce,
            OAuthAuthorizationCode.expires_at > utcnow(),
        ).first() is not None

    def generate_user_info(self, user, scope):
        return oidc_user_info(user, scope)


class OAuthBearerTokenValidator(BearerTokenValidator):
    def authenticate_token(self, token_string):
        token = OAuthToken.query.filter_by(access_token_hash=token_digest(token_string)).first()
        if (
            not token
            or not token.client.is_active
            or token.user.role not in (token.client.allowed_roles or [])
        ):
            return None
        return token


class OAuthRevocationEndpoint(RevocationEndpoint):
    CLIENT_AUTH_METHODS = ['client_secret_basic', 'client_secret_post', 'none']

    def query_token(self, token_string, token_type_hint):
        digest = token_digest(token_string)
        if token_type_hint == 'access_token':
            return (
                OAuthToken.query.filter_by(access_token_hash=digest).first()
                or OAuthToken.query.filter_by(refresh_token_hash=digest).first()
            )
        if token_type_hint == 'refresh_token':
            return (
                OAuthToken.query.filter_by(refresh_token_hash=digest).first()
                or OAuthToken.query.filter_by(access_token_hash=digest).first()
            )
        return (
            OAuthToken.query.filter_by(access_token_hash=digest).first()
            or OAuthToken.query.filter_by(refresh_token_hash=digest).first()
        )

    def revoke_token(self, token, request):
        revoked_at = int(time.time())
        digest = token_digest(request.form['token'])
        if token.access_token_hash == digest:
            token.access_token_revoked_at = revoked_at
        else:
            token.access_token_revoked_at = revoked_at
            token.refresh_token_revoked_at = revoked_at
        db.session.commit()


authorization_server.register_grant(
    OIDCAuthorizationCodeGrant,
    extensions=[CodeChallenge(required=True), CRMOpenIDCode(require_nonce=True)],
)
authorization_server.register_grant(OIDCRefreshTokenGrant)
authorization_server.register_endpoint(OAuthRevocationEndpoint)
require_oauth.register_token_validator(OAuthBearerTokenValidator())


def init_oidc(app):
    authorization_server.init_app(app, query_client=query_client, save_token=save_token)
