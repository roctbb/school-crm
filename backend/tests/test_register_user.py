from .fixtures import *


# Тесты регистрации
def test_signup_success(client, test_invite):
    """Тест: успешная регистрация с валидным инвайтом"""
    response = client.post('/api/signup', json={
        "name": "John Doe",
        "email": "john.doe@example.com",
        "password": "securepassword",
        "invite": "valid-invite-code"
    })

    assert response.status_code == 201
    data = response.get_json()
    assert data["id"] > 0  # Убедимся, что пользователь зарегистрирован
    assert data["name"] == "John Doe"
    assert data["email"] == "john.doe@example.com"

    # Проверяем, что инвайт помечен как использованный
    invite = Invitation.query.filter_by(key="valid-invite-code").first()
    assert invite.used_at is not None


def test_signup_used_invite(client, used_invite):
    """Тест: ошибка регистрации с уже использованным инвайтом"""
    response = client.post('/api/signup', json={
        "name": "Jane Doe",
        "email": "jane.doe@example.com",
        "password": "securepassword",
        "invite": "used-invite-code"
    })

    assert response.status_code == 401


def test_signup_invalid_data(client, test_invite):
    """Тест: ошибка при передаче некорректных данных"""
    response = client.post('/api/signup', json={
        "name": "",  # Пустое имя
        "email": "invalid-email",  # Некорректный email
        "password": "short",  # Слишком короткий пароль
        "invite": "valid-invite-code"  # Валидный инвайт
    })

    assert response.status_code == 400


def test_signup_existing_email(client, test_existing_user, test_invite):
    """Тест: ошибка регистрации, если email уже занят"""
    response = client.post('/api/signup', json={
        "name": "New User",
        "email": "existing_user@example.com",  # Email уже занят
        "password": "securepassword",
        "invite": "valid-invite-code"
    })

    assert response.status_code == 400
    data = response.get_json()


# Тесты входа
def test_login_success(client, test_user):
    """Тест: успешный вход пользователя с корректными данными"""
    response = client.post('/api/login', json={
        "email": "test@example.com",
        "password": "password123"
    })

    assert response.status_code == 200
    data = response.get_json()
    assert "access_token" in data
    assert data["access_token"] is not None


def test_login_wrong_password(client, test_user):
    """Тест: ошибка входа с неверным паролем"""
    response = client.post('/api/login', json={
        "email": "test@example.com",
        "password": "wrongpassword"
    })

    assert response.status_code == 401


def test_login_user_not_found(client):
    """Тест: ошибка входа с несуществующим email"""
    response = client.post('/api/login', json={
        "email": "nonexistent@example.com",
        "password": "password123"
    })

    assert response.status_code == 401


# Тесты профиля
def test_profile_success(client, test_user, access_token):
    """Тест: успешное получение профиля с корректным токеном"""
    # Отправляем запрос с заголовком Authorization

    response = client.get('/api/me', headers={
        "Authorization": f"Bearer {access_token}"
    })

    assert response.status_code == 200
    data = response.get_json()
    assert data["id"] == test_user.id
    assert data["name"] == test_user.name
    assert data["email"] == test_user.email


def test_profile_no_token(client):
    """Тест: ошибка получения профиля без токена"""
    response = client.get('/api/me')

    assert response.status_code == 401
