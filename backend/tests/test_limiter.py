from .fixtures import *

def test_login_rate_limit(client):
    """Тест: лимитер должен пропускать только 240 запросов в день на /api/login"""
    request_environment = {'REMOTE_ADDR': '127.0.0.10'}
    for _ in range(240):
        response = client.post('/api/login', json={
            "email": "john.doe@example.com",
            "password": "securepassword"
        }, environ_base=request_environment)
        assert response.status_code in [200, 401]  # 200 если успешный вход, 401 если неверные данные
    
    # 241-й запрос должен быть заблокирован
    response = client.post('/api/login', json={
        "email": "john.doe@example.com",
        "password": "securepassword"
    }, environ_base=request_environment)
    assert response.status_code == 429  # Too Many Requests

def test_signup_rate_limit(client, test_invite):
    """Тест: лимитер должен пропускать только 240 запросов в день на /api/signup"""
    request_environment = {'REMOTE_ADDR': '127.0.0.11'}
    for _ in range(240):
        response = client.post('/api/signup', json={
            "name": "John Doe",
            "email": "john.doe@example.com",
            "password": "securepassword",
            "invite": "valid-invite-code"
        }, environ_base=request_environment)
        assert response.status_code in [201, 400]  # 201 если регистрация успешна, 400 если инвайт недействителен
    
    # 241-й запрос должен быть заблокирован
    response = client.post('/api/signup', json={
        "name": "John Doe",
        "email": "john.doe@example.com",
        "password": "securepassword",
        "invite": "valid-invite-code"
    }, environ_base=request_environment)
    assert response.status_code == 429  # Too Many Requests
