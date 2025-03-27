import pytest
from flask_jwt_extended import create_access_token
from application.models import User, Invitation, db
from application.infrastructure import bcrypt
from datetime import datetime
from application import create_app


@pytest.fixture
def app():
    app, _ = create_app('testing')
    # Создаём контекст приложения
    context = app.app_context()
    context.push()

    # Сбрасываем и создаём базу данных перед каждым тестом
    db.drop_all()
    db.create_all()

    yield app

    db.session.remove()
    db.drop_all()
    context.pop()


@pytest.fixture
def db_session(app):
    yield db.session


@pytest.fixture(scope='function')
def client(app):
    """Фикстура для создания тестового клиента Flask."""
    # Инициализация тестовой конфигурации
    yield app.test_client()


@pytest.fixture
def test_invite():
    """Фикстура для создания тестового инвайта"""
    invite = Invitation(
        email="invite@example.com",
        key="valid-invite-code",
        role="user",
        object_id=None,
        used_at=None
    )
    db.session.add(invite)
    db.session.commit()
    return invite


@pytest.fixture
def used_invite():
    """Фикстура для создания использованного инвайта"""
    invite = Invitation(
        email="used-invite@example.com",
        key="used-invite-code",
        role="user",
        object_id=None,
        used_at=datetime.utcnow()  # Метка об использовании
    )
    db.session.add(invite)
    db.session.commit()
    return invite


@pytest.fixture
def test_user():
    """Фикстура для создания тестового пользователя"""
    user = User(
        name="Test User",
        email="test@example.com",
        password=bcrypt.generate_password_hash("password123").decode('utf-8'),
        role="user"
    )
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def access_token(test_user):
    token = create_access_token(identity=str(test_user.id))  # Создание токена
    return token


@pytest.fixture
def test_existing_user():
    """Фикстура для создания пользователя с занятой почтой"""
    user = User(
        name="Existing User",
        email="existing_user@example.com",
        password=bcrypt.generate_password_hash("password123").decode('utf-8'),
        role="user"
    )
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def auth_headers(test_user):
    """Создает заголовок авторизации для тестов"""
    token = create_access_token(identity=str(test_user.id))
    return {'Authorization': f'Bearer {token}'}
