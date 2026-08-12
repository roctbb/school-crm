import base64
import hashlib
import secrets
from urllib.parse import parse_qs, urlsplit

from flask_jwt_extended import create_access_token
from joserfc import jwt
from joserfc.jwk import RSAKey

from application.infrastructure import bcrypt, db
from application.models import OAuthAuthorizationCode, OAuthClient, OAuthConsent, OAuthToken, User
from application.models import Object, ObjectType, UploadedFile
from application.constants import UPLOAD_FOLDER
from application.oidc import token_digest
from .fixtures import *


CLIENT_ID = 'test-lms'
REDIRECT_URI = 'https://lms.example.test/auth/callback'
LOGOUT_URI = 'https://lms.example.test/logged-out'


def _auth_header(user):
    return {'Authorization': f'Bearer {create_access_token(identity=str(user.id))}'}


def _create_user(role='student', email='student@example.test'):
    user = User(
        name='Test Student',
        email=email,
        password=bcrypt.generate_password_hash('password123').decode('utf-8'),
        role=role,
    )
    type_code = f'{role}s'
    object_type = ObjectType.query.filter_by(code=type_code).first()
    if not object_type:
        object_type = ObjectType(name=type_code.title(), code=type_code)
    identity = Object(name=f'{role.title()} CRM Object', type=object_type)
    identity.owners.append(user)
    user.identity_object = identity
    db.session.add_all([user, object_type, identity])
    db.session.commit()
    return user


def _client_payload(**overrides):
    payload = {
        'client_id': CLIENT_ID,
        'name': 'Test LMS',
        'description': 'OIDC integration test',
        'redirect_uris': [REDIRECT_URI],
        'post_logout_redirect_uris': [LOGOUT_URI],
        'allowed_scopes': ['openid', 'profile', 'email', 'roles', 'avatar', 'offline_access'],
        'allowed_roles': ['student', 'teacher', 'admin'],
        'is_confidential': True,
        'is_active': True,
    }
    payload.update(overrides)
    return payload


def _create_registered_client(client, confidential=True):
    admin = _create_user('admin', 'admin@example.test')
    response = client.post(
        '/api/oauth/clients',
        json=_client_payload(is_confidential=confidential),
        headers=_auth_header(admin),
    )
    assert response.status_code == 201, response.get_json()
    return response.get_json(), admin


def _authorization_params(verifier=None, **overrides):
    verifier = verifier or secrets.token_urlsafe(64)
    challenge = base64.urlsafe_b64encode(
        hashlib.sha256(verifier.encode('ascii')).digest()
    ).rstrip(b'=').decode('ascii')
    params = {
        'client_id': CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': REDIRECT_URI,
        'scope': 'openid profile email roles offline_access',
        'state': secrets.token_urlsafe(32),
        'nonce': secrets.token_urlsafe(32),
        'code_challenge': challenge,
        'code_challenge_method': 'S256',
    }
    params.update(overrides)
    return verifier, params


def _authorize(client, user, params):
    request_response = client.get(
        '/api/oauth/authorize/request', query_string=params, headers=_auth_header(user)
    )
    assert request_response.status_code == 200, request_response.get_json()

    response = client.post(
        '/api/oauth/authorize',
        json={**params, 'decision': True},
        headers=_auth_header(user),
    )
    assert response.status_code == 200, response.get_json()
    redirect = response.get_json()['redirect_uri']
    query = parse_qs(urlsplit(redirect).query)
    assert query['state'][0] == params['state']
    return query['code'][0]


def _basic_auth(client_id, secret):
    encoded = base64.b64encode(f'{client_id}:{secret}'.encode()).decode()
    return {'Authorization': f'Basic {encoded}'}


def _exchange_code(client, code, verifier, secret=None):
    headers = _basic_auth(CLIENT_ID, secret) if secret else {}
    return client.post(
        '/api/oauth/token',
        base_url='https://localhost',
        data={
            'grant_type': 'authorization_code',
            'client_id': CLIENT_ID,
            'code': code,
            'redirect_uri': REDIRECT_URI,
            'code_verifier': verifier,
        },
        headers=headers,
    )


def test_discovery_and_jwks(client):
    discovery = client.get('/.well-known/openid-configuration')
    assert discovery.status_code == 200
    metadata = discovery.get_json()
    assert metadata['issuer'] == 'http://localhost:5173'
    assert metadata['authorization_endpoint'].endswith('/oauth/authorize')
    assert metadata['code_challenge_methods_supported'] == ['S256']
    assert 'avatar' in metadata['scopes_supported']
    assert 'picture' in metadata['claims_supported']

    jwks_response = client.get('/api/oauth/jwks')
    assert jwks_response.status_code == 200
    key = jwks_response.get_json()['keys'][0]
    assert key['kty'] == 'RSA'
    assert key['alg'] == 'RS256'
    assert key['use'] == 'sig'
    assert key['kid']


def test_token_endpoint_trusts_https_from_the_nearest_proxy(client):
    response = client.post(
        '/api/oauth/token',
        base_url='http://lk.silaeder.ru',
        headers={'X-Forwarded-Proto': 'https'},
        data={
            'grant_type': 'authorization_code',
            'client_id': 'missing-client',
            'code': 'missing-code',
            'redirect_uri': REDIRECT_URI,
            'code_verifier': 'a' * 43,
        },
    )
    assert response.status_code == 400
    assert response.get_json()['error'] == 'invalid_client'


def test_userinfo_returns_standard_bearer_error(client):
    response = client.get('/api/oauth/userinfo')
    assert response.status_code == 401
    assert response.get_json()['error'] == 'missing_authorization'
    assert response.headers['WWW-Authenticate'].lower().startswith('bearer ')


def test_admin_manages_clients_and_secret_is_only_returned_once(client):
    created, admin = _create_registered_client(client)
    secret = created.pop('client_secret')
    assert len(secret) >= 48

    stored = OAuthClient.query.filter_by(client_id=CLIENT_ID).one()
    assert secret not in stored.client_secret_hash
    assert bcrypt.check_password_hash(stored.client_secret_hash, secret)

    listed = client.get('/api/oauth/clients', headers=_auth_header(admin))
    assert listed.status_code == 200
    assert 'client_secret' not in listed.get_json()[0]

    student = _create_user()
    forbidden = client.get('/api/oauth/clients', headers=_auth_header(student))
    assert forbidden.status_code == 403

    rotated = client.post(
        f"/api/oauth/clients/{created['id']}/rotate-secret",
        headers=_auth_header(admin),
    )
    assert rotated.status_code == 200
    assert rotated.get_json()['client_secret'] != secret


def test_authorization_code_pkce_userinfo_refresh_and_revocation(client):
    registered, _admin = _create_registered_client(client)
    secret = registered['client_secret']
    user = _create_user()
    verifier, params = _authorization_params()
    code = _authorize(client, user, params)

    stored_code = OAuthAuthorizationCode.query.one()
    assert stored_code.code_hash == token_digest(code)
    assert code not in stored_code.code_hash

    token_response = _exchange_code(client, code, verifier, secret)
    assert token_response.status_code == 200, token_response.get_json()
    token = token_response.get_json()
    assert token['token_type'].lower() == 'bearer'
    assert token['expires_in'] == 900
    assert token['refresh_token']
    assert token['id_token']
    assert OAuthAuthorizationCode.query.count() == 0

    stored_token = OAuthToken.query.one()
    assert stored_token.access_token_hash == token_digest(token['access_token'])
    assert stored_token.refresh_token_hash == token_digest(token['refresh_token'])
    assert token['access_token'] not in stored_token.access_token_hash

    public_key = RSAKey.import_key(client.get('/api/oauth/jwks').get_json()['keys'][0])
    id_token = jwt.decode(token['id_token'], public_key, algorithms=['RS256'])
    claims = id_token.claims
    assert claims['iss'] == 'http://localhost:5173'
    assert claims['aud'] == [CLIENT_ID]
    assert claims['sub'] == user.identity_object.sso_subject
    assert claims['name'] == user.identity_object.name
    assert claims['object_id'] == user.identity_object.id
    assert claims['object_type'] == 'students'
    assert claims['crm_object'] == {
        'id': user.identity_object.id,
        'type': 'students',
        'name': user.identity_object.name,
    }
    assert claims['nonce'] == params['nonce']
    assert claims['email'] == user.email
    assert claims['roles'] == ['student']

    logout = client.get('/api/oauth/logout/request', query_string={
        'id_token_hint': token['id_token'],
        'post_logout_redirect_uri': LOGOUT_URI,
        'state': 'logout-state',
    })
    assert logout.status_code == 200
    assert logout.get_json()['redirect_uri'] == f'{LOGOUT_URI}?state=logout-state'

    userinfo = client.get(
        '/api/oauth/userinfo',
        headers={'Authorization': f"Bearer {token['access_token']}"},
    )
    assert userinfo.status_code == 200
    assert userinfo.get_json()['sub'] == user.identity_object.sso_subject
    assert userinfo.get_json()['crm_object']['id'] == user.identity_object.id

    replay = _exchange_code(client, code, verifier, secret)
    assert replay.status_code == 400
    assert replay.get_json()['error'] == 'invalid_grant'

    refresh = client.post(
        '/api/oauth/token',
        base_url='https://localhost',
        data={
            'grant_type': 'refresh_token',
            'refresh_token': token['refresh_token'],
            'client_id': CLIENT_ID,
        },
        headers=_basic_auth(CLIENT_ID, secret),
    )
    assert refresh.status_code == 200, refresh.get_json()
    refreshed = refresh.get_json()
    assert refreshed['access_token'] != token['access_token']
    assert refreshed['refresh_token'] != token['refresh_token']

    old_refresh = client.post(
        '/api/oauth/token',
        base_url='https://localhost',
        data={
            'grant_type': 'refresh_token',
            'refresh_token': token['refresh_token'],
            'client_id': CLIENT_ID,
        },
        headers=_basic_auth(CLIENT_ID, secret),
    )
    assert old_refresh.status_code == 400

    revoke = client.post(
        '/api/oauth/revoke',
        base_url='https://localhost',
        data={
            'token': refreshed['access_token'],
            'token_type_hint': 'access_token',
            'client_id': CLIENT_ID,
        },
        headers=_basic_auth(CLIENT_ID, secret),
    )
    assert revoke.status_code == 200, revoke.get_json()
    revoked_userinfo = client.get(
        '/api/oauth/userinfo',
        headers={'Authorization': f"Bearer {refreshed['access_token']}"},
    )
    assert revoked_userinfo.status_code == 401


def test_consent_is_remembered_for_the_same_or_smaller_scope(client):
    _create_registered_client(client)
    user = _create_user()

    _verifier, initial_params = _authorization_params(scope='openid profile')
    initial_request = client.get(
        '/api/oauth/authorize/request',
        query_string=initial_params,
        headers=_auth_header(user),
    )
    assert initial_request.status_code == 200
    assert initial_request.get_json()['requires_consent'] is True

    approved = client.post(
        '/api/oauth/authorize',
        json={**initial_params, 'decision': True},
        headers=_auth_header(user),
    )
    assert approved.status_code == 200
    consent = OAuthConsent.query.filter_by(user_id=user.id, client_id=CLIENT_ID).one()
    assert set(consent.scopes) == {'openid', 'profile'}

    _verifier, repeated_params = _authorization_params(scope='openid profile')
    repeated = client.get(
        '/api/oauth/authorize/request',
        query_string=repeated_params,
        headers=_auth_header(user),
    )
    assert repeated.status_code == 200
    assert repeated.get_json()['requires_consent'] is False

    _verifier, smaller_params = _authorization_params(scope='openid')
    smaller = client.get(
        '/api/oauth/authorize/request',
        query_string=smaller_params,
        headers=_auth_header(user),
    )
    assert smaller.status_code == 200
    assert smaller.get_json()['requires_consent'] is False

    _verifier, expanded_params = _authorization_params(scope='openid profile email')
    expanded = client.get(
        '/api/oauth/authorize/request',
        query_string=expanded_params,
        headers=_auth_header(user),
    )
    assert expanded.status_code == 200
    assert expanded.get_json()['requires_consent'] is True

    _verifier, forced_params = _authorization_params(scope='openid', prompt='consent')
    forced = client.get(
        '/api/oauth/authorize/request',
        query_string=forced_params,
        headers=_auth_header(user),
    )
    assert forced.status_code == 200
    assert forced.get_json()['requires_consent'] is True


def test_pkce_redirect_role_and_public_client_protections(client):
    registered, _admin = _create_registered_client(client, confidential=False)
    assert registered['client_secret'] is None
    user = _create_user()
    verifier, params = _authorization_params()

    bad_redirect = client.get(
        '/api/oauth/authorize/request',
        query_string={**params, 'redirect_uri': 'https://evil.example.test/callback'},
        headers=_auth_header(user),
    )
    assert bad_redirect.status_code == 400

    bad_pkce = client.get(
        '/api/oauth/authorize/request',
        query_string={**params, 'code_challenge_method': 'plain'},
        headers=_auth_header(user),
    )
    assert bad_pkce.status_code == 400

    stored_client = OAuthClient.query.filter_by(client_id=CLIENT_ID).one()
    stored_client.allowed_roles = ['teacher']
    db.session.commit()
    forbidden_role = client.get(
        '/api/oauth/authorize/request', query_string=params, headers=_auth_header(user)
    )
    assert forbidden_role.status_code == 403

    stored_client.allowed_roles = ['student']
    db.session.commit()
    code = _authorize(client, user, params)
    wrong_verifier = _exchange_code(client, code, 'x' * 64)
    assert wrong_verifier.status_code == 400
    assert wrong_verifier.get_json()['error'] == 'invalid_grant'

    verifier, params = _authorization_params(scope='openid profile')
    code = _authorize(client, user, params)
    token_response = _exchange_code(client, code, verifier)
    assert token_response.status_code == 200, token_response.get_json()
    assert 'refresh_token' not in token_response.get_json()

    stored_client.allowed_roles = ['teacher']
    db.session.commit()
    blocked_userinfo = client.get(
        '/api/oauth/userinfo',
        headers={'Authorization': f"Bearer {token_response.get_json()['access_token']}"},
    )
    assert blocked_userinfo.status_code == 401


def test_logout_only_allows_registered_redirect(client):
    _create_registered_client(client)

    response = client.get('/api/oauth/logout/request', query_string={
        'client_id': CLIENT_ID,
        'post_logout_redirect_uri': LOGOUT_URI,
        'state': 'returned-state',
    })
    assert response.status_code == 200
    assert response.get_json()['redirect_uri'] == f'{LOGOUT_URI}?state=returned-state'

    invalid = client.get('/api/oauth/logout/request', query_string={
        'client_id': CLIENT_ID,
        'post_logout_redirect_uri': 'https://evil.example.test/',
    })
    assert invalid.status_code == 400


def test_avatar_scope_returns_picture_claim_and_protected_image(client):
    registered, _admin = _create_registered_client(client)
    secret = registered['client_secret']
    user = _create_user()
    obj = user.identity_object
    obj.type.available_attributes = [{'name': 'Photo', 'code': 'photo', 'type': 'file'}]
    uploaded_file = UploadedFile(
        user_id=user.id,
        original_filename='avatar.jpg',
        stored_filename='avatar.jpg',
    )
    db.session.add(uploaded_file)
    db.session.flush()
    obj.name = 'Student Object'
    obj.attributes = {'photo': f'/api/files/folder_{uploaded_file.id}/avatar.jpg'}
    db.session.commit()

    import os
    os.makedirs(os.path.join(UPLOAD_FOLDER, f'folder_{uploaded_file.id}'), exist_ok=True)
    avatar_path = os.path.join(UPLOAD_FOLDER, f'folder_{uploaded_file.id}', 'avatar.jpg')
    try:
        with open(avatar_path, 'wb') as avatar:
            avatar.write(b'fake-jpeg')

        verifier, params = _authorization_params(
            scope='openid profile avatar', nonce=secrets.token_urlsafe(32)
        )
        code = _authorize(client, user, params)
        token_response = _exchange_code(client, code, verifier, secret)
        assert token_response.status_code == 200, token_response.get_json()
        token = token_response.get_json()

        public_key = RSAKey.import_key(client.get('/api/oauth/jwks').get_json()['keys'][0])
        claims = jwt.decode(token['id_token'], public_key, algorithms=['RS256']).claims
        assert claims['picture'] == 'http://localhost:5173/api/oauth/avatar'

        avatar_response = client.get(
            '/api/oauth/avatar',
            headers={'Authorization': f"Bearer {token['access_token']}"},
        )
        assert avatar_response.status_code == 200
        assert avatar_response.data == b'fake-jpeg'
    finally:
        if os.path.exists(avatar_path):
            os.remove(avatar_path)


def test_oidc_rejects_account_without_identity_object(client):
    _create_registered_client(client)
    user = User(name='Unlinked', email='unlinked@example.test', role='student')
    db.session.add(user)
    db.session.commit()
    _verifier, params = _authorization_params()

    response = client.get(
        '/api/oauth/authorize/request', query_string=params, headers=_auth_header(user)
    )

    assert response.status_code == 403
    assert 'не привязан к объекту' in response.get_json()['message']
