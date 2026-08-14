from datetime import timedelta

from flask_jwt_extended import create_access_token, decode_token

from application.models import AuthRefreshToken
from .fixtures import *


def _login(client, test_user, remember_me=False):
    return client.post('/api/login', json={
        'email': test_user.email,
        'password': 'password123',
        'remember_me': remember_me,
    })


def test_regular_login_does_not_create_persistent_session(client, app, test_user):
    response = _login(client, test_user)

    assert response.status_code == 200
    assert response.get_json()['persistent'] is False
    assert client.get_cookie(app.config['JWT_REFRESH_COOKIE_NAME'], path='/api') is None
    assert AuthRefreshToken.query.count() == 0


def test_remember_me_rotates_refresh_token(client, app, test_user):
    login_response = _login(client, test_user, remember_me=True)

    assert login_response.status_code == 200
    assert login_response.get_json()['persistent'] is True
    old_refresh = client.get_cookie(app.config['JWT_REFRESH_COOKIE_NAME'], path='/api').value
    old_csrf = client.get_cookie(app.config['JWT_REFRESH_CSRF_COOKIE_NAME']).value
    old_claims = decode_token(old_refresh)

    refresh_response = client.post(
        '/api/refresh',
        headers={app.config['JWT_REFRESH_CSRF_HEADER_NAME']: old_csrf},
    )

    assert refresh_response.status_code == 200
    assert refresh_response.get_json()['access_token']
    new_refresh = client.get_cookie(app.config['JWT_REFRESH_COOKIE_NAME'], path='/api').value
    assert new_refresh != old_refresh

    old_record = AuthRefreshToken.query.filter_by(jti=old_claims['jti']).one()
    new_record = AuthRefreshToken.query.filter_by(jti=decode_token(new_refresh)['jti']).one()
    assert old_record.revoked_at is not None
    assert old_record.replaced_by_jti == new_record.jti
    assert new_record.revoked_at is None
    assert old_record.family_id == new_record.family_id


def test_rotated_refresh_token_cannot_be_reused(client, app, test_user):
    _login(client, test_user, remember_me=True)
    old_refresh = client.get_cookie(app.config['JWT_REFRESH_COOKIE_NAME'], path='/api').value
    old_claims = decode_token(old_refresh)
    old_csrf = old_claims['csrf']

    first_refresh = client.post(
        '/api/refresh',
        headers={app.config['JWT_REFRESH_CSRF_HEADER_NAME']: old_csrf},
    )
    assert first_refresh.status_code == 200
    active_jti = decode_token(
        client.get_cookie(app.config['JWT_REFRESH_COOKIE_NAME'], path='/api').value
    )['jti']

    client.set_cookie(app.config['JWT_REFRESH_COOKIE_NAME'], old_refresh, path='/api')
    client.set_cookie(app.config['JWT_REFRESH_CSRF_COOKIE_NAME'], old_csrf, path='/')
    replay_response = client.post(
        '/api/refresh',
        headers={app.config['JWT_REFRESH_CSRF_HEADER_NAME']: old_csrf},
    )

    assert replay_response.status_code == 401
    assert 'Войдите снова' in replay_response.get_json()['message']
    assert AuthRefreshToken.query.filter_by(jti=active_jti).one().revoked_at is None


def test_logout_revokes_refresh_session_and_clears_cookies(client, app, test_user):
    _login(client, test_user, remember_me=True)
    refresh_token = client.get_cookie(app.config['JWT_REFRESH_COOKIE_NAME'], path='/api').value
    claims = decode_token(refresh_token)
    csrf = client.get_cookie(app.config['JWT_REFRESH_CSRF_COOKIE_NAME']).value

    response = client.post(
        '/api/logout',
        headers={app.config['JWT_REFRESH_CSRF_HEADER_NAME']: csrf},
    )

    assert response.status_code == 200
    assert AuthRefreshToken.query.filter_by(jti=claims['jti']).one().revoked_at is not None
    assert client.get_cookie(app.config['JWT_REFRESH_COOKIE_NAME'], path='/api') is None
    assert client.get_cookie(app.config['JWT_REFRESH_CSRF_COOKIE_NAME']) is None


def test_expired_access_token_has_readable_message(client, test_user):
    token = create_access_token(
        identity=str(test_user.id),
        expires_delta=timedelta(seconds=-1),
    )

    response = client.get('/api/me', headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == 401
    assert response.get_json() == {
        'message': 'Срок действия сессии истёк. Войдите снова.',
    }


def test_remember_me_must_be_boolean(client, test_user):
    response = client.post('/api/login', json={
        'email': test_user.email,
        'password': 'password123',
        'remember_me': 'yes',
    })

    assert response.status_code == 400
    assert response.get_json()['field'] == 'remember_me'
