from .fixtures import *


def _login(client, email, remote_addr='127.0.0.10', forwarded_for=None):
    headers = {'X-Forwarded-For': forwarded_for} if forwarded_for else {}
    return client.post(
        '/api/login',
        json={'email': email, 'password': 'wrong-password'},
        headers=headers,
        environ_base={'REMOTE_ADDR': remote_addr},
    )


def test_login_limit_is_per_email_for_users_behind_shared_ip(client, app):
    app.config.update(
        AUTH_LOGIN_IP_RATE_LIMIT='100 per minute',
        AUTH_LOGIN_EMAIL_RATE_LIMIT='2 per minute',
    )

    assert _login(client, 'first@example.com').status_code == 401
    assert _login(client, 'FIRST@example.com').status_code == 401
    assert _login(client, 'first@example.com').status_code == 429

    # Другой ученик с того же школьного IP не делит лимит первого аккаунта.
    assert _login(client, 'second@example.com').status_code == 401


def test_successful_logins_do_not_consume_shared_ip_quota(client, app, test_user):
    app.config.update(
        AUTH_LOGIN_IP_RATE_LIMIT='1 per minute',
        AUTH_LOGIN_EMAIL_RATE_LIMIT='10 per minute',
    )
    request_environment = {'REMOTE_ADDR': '127.0.0.11'}
    payload = {'email': test_user.email, 'password': 'password123'}

    assert client.post('/api/login', json=payload, environ_base=request_environment).status_code == 200
    assert client.post('/api/login', json=payload, environ_base=request_environment).status_code == 200


def test_signup_limit_is_per_invite_for_users_behind_shared_ip(client, app):
    app.config.update(
        AUTH_SIGNUP_IP_RATE_LIMIT='100 per minute',
        AUTH_SIGNUP_INVITE_RATE_LIMIT='2 per minute',
    )
    request_environment = {'REMOTE_ADDR': '127.0.0.12'}

    def signup(invite):
        return client.post('/api/signup', json={
            'name': 'John Doe',
            'email': 'john.doe@example.com',
            'password': 'securepassword',
            'invite': invite,
        }, environ_base=request_environment)

    assert signup('missing-invite-one').status_code == 400
    assert signup('missing-invite-one').status_code == 400
    assert signup('missing-invite-one').status_code == 429
    assert signup('missing-invite-two').status_code == 400


def test_ip_limit_uses_forwarded_client_address(client, app):
    app.config.update(
        AUTH_LOGIN_IP_RATE_LIMIT='1 per minute',
        AUTH_LOGIN_EMAIL_RATE_LIMIT='100 per minute',
    )
    proxy_address = '172.20.0.5'

    assert _login(client, 'one@example.com', proxy_address, '203.0.113.10').status_code == 401
    assert _login(client, 'two@example.com', proxy_address, '203.0.113.10').status_code == 429
    assert _login(client, 'three@example.com', proxy_address, '203.0.113.11').status_code == 401
