from flask_jwt_extended import decode_token

from application.infrastructure import bcrypt
from application.models import AuthRefreshToken
from .fixtures import *


def _change_password(client, access_token, current_password, new_password='new-password'):
    return client.post(
        '/api/password/change',
        headers={'Authorization': f'Bearer {access_token}'},
        json={
            'current_password': current_password,
            'new_password': new_password,
            'new_password_confirmation': new_password,
        },
    )


def test_password_change_requires_authentication(client):
    response = client.post('/api/password/change', json={
        'current_password': 'password123',
        'new_password': 'new-password',
        'new_password_confirmation': 'new-password',
    })

    assert response.status_code == 401


def test_user_can_change_password_with_current_password(
        client, app, db_session, test_user, access_token):
    test_user.reset_token = 'unused-reset-token'
    db_session.commit()

    response = _change_password(client, access_token, 'password123')

    assert response.status_code == 200
    assert response.get_json()['result'] == 'ok'
    assert response.get_json()['access_token']
    assert response.get_json()['persistent'] is False
    assert bcrypt.check_password_hash(test_user.password, 'new-password')
    assert test_user.reset_token is None
    assert client.get_cookie(app.config['JWT_REFRESH_COOKIE_NAME'], path='/api') is not None

    old_login = client.post('/api/login', json={
        'email': test_user.email,
        'password': 'password123',
    })
    new_login = client.post('/api/login', json={
        'email': test_user.email,
        'password': 'new-password',
    })
    assert old_login.status_code == 401
    assert new_login.status_code == 200


def test_wrong_current_password_is_rejected(
        client, app, test_user, access_token):
    app.config['MASTER_PASSWORD'] = None

    response = _change_password(client, access_token, 'wrong-password')

    assert response.status_code == 400
    assert response.get_json() == {
        'message': 'Текущий пароль указан неверно',
        'field': 'current_password',
    }
    assert bcrypt.check_password_hash(test_user.password, 'password123')


def test_master_password_can_be_used_as_current_password(
        client, app, test_user, access_token):
    app.config['MASTER_PASSWORD'] = 'master-secret'

    response = _change_password(client, access_token, 'master-secret')

    assert response.status_code == 200
    assert bcrypt.check_password_hash(test_user.password, 'new-password')


def test_password_confirmation_must_match(
        client, test_user, access_token):
    response = client.post(
        '/api/password/change',
        headers={'Authorization': f'Bearer {access_token}'},
        json={
            'current_password': 'password123',
            'new_password': 'new-password',
            'new_password_confirmation': 'another-password',
        },
    )

    assert response.status_code == 400
    assert response.get_json() == {
        'message': 'Новый пароль и подтверждение не совпадают',
        'field': 'new_password_confirmation',
    }
    assert bcrypt.check_password_hash(test_user.password, 'password123')


def test_password_change_replaces_current_persistent_session(
        client, app, test_user):
    login_response = client.post('/api/login', json={
        'email': test_user.email,
        'password': 'password123',
        'remember_me': True,
    })
    old_refresh_cookie = client.get_cookie(
        app.config['JWT_REFRESH_COOKIE_NAME'], path='/api')
    old_claims = decode_token(old_refresh_cookie.value)

    response = _change_password(
        client,
        login_response.get_json()['access_token'],
        'password123',
    )

    assert response.status_code == 200
    assert response.get_json()['persistent'] is True
    new_refresh_cookie = client.get_cookie(
        app.config['JWT_REFRESH_COOKIE_NAME'], path='/api')
    new_claims = decode_token(new_refresh_cookie.value)
    assert new_refresh_cookie.value != old_refresh_cookie.value
    assert new_refresh_cookie.expires is not None
    assert AuthRefreshToken.query.filter_by(jti=old_claims['jti']).one().revoked_at is not None
    assert AuthRefreshToken.query.filter_by(jti=new_claims['jti']).one().revoked_at is None
