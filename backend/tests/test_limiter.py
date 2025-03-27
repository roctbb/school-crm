from .fixtures import *

def test_login_rate_limit(client):
    """Тест: лимитер должен пропускать только 30 запросов в день на /api/login"""
    for _ in range(30):
        response = client.post('/api/login', json={
            "email": "john.doe@example.com",
            "password": "securepassword"
        })
        assert response.status_code in [200, 401]  # 200 если успешный вход, 401 если неверные данные
    
    # 31-й запрос должен быть заблокирован
    response = client.post('/api/login', json={
        "email": "john.doe@example.com",
        "password": "securepassword"
    })
    assert response.status_code == 429  # Too Many Requests

def test_signup_rate_limit(client, test_invite):
    """Тест: лимитер должен пропускать только 3 запроса в день на /api/signup"""
    for _ in range(3):
        response = client.post('/api/signup', json={
            "name": "John Doe",
            "email": "john.doe@example.com",
            "password": "securepassword",
            "invite": "valid-invite-code"
        })
        assert response.status_code in [201, 400]  # 201 если регистрация успешна, 400 если инвайт недействителен
    
    # 4-й запрос должен быть заблокирован
    response = client.post('/api/signup', json={
        "name": "John Doe",
        "email": "john.doe@example.com",
        "password": "securepassword",
        "invite": "valid-invite-code"
    })
    assert response.status_code == 429  # Too Many Requests
