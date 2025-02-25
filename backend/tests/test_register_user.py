import pytest
from app import create_app, db
from app.models import User, Entity, EntityType, Role
from flask_migrate import upgrade


@pytest.fixture(scope='function')
def test_client():
    """Фикстура для создания тестового клиента Flask и управления сессией"""
    app = create_app('testing')  # Создаём приложение с тестовой конфигурацией
    client = app.test_client()

    with app.app_context():
        # Полностью сбрасываем базу
        db.session.remove()  # Убираем рабочую сессию
        db.drop_all()  # Удаляем схемы
        db.create_all()  # Заново создаем на основе модели
        upgrade()  # Накатываем миграции

        # Работа с текущей транзакцией
        connection = db.engine.connect()
        transaction = connection.begin()

        db.session.bind = connection

        yield client

        transaction.rollback()  # Откатываем изменения
        connection.close()
        db.session.remove()

@pytest.fixture
def test_data():
    """Фикстура для заполнения тестовых данных (Entity, Role и т.д.)"""
    # Создаём тестовый тип сущности
    entity_type = EntityType(name="Test EntityType")
    db.session.add(entity_type)
    db.session.commit()

    # Создаём тестовые сущности
    entity = Entity(
        name='Test Entity',
        invite_code='test-entity-code',
        type_id=entity_type.id  # Обязательно указываем type_id
    )
    db.session.add(entity)

    # Создаём тестовые роли
    role1 = Role(name='Admin', invite_code='test-role-code')
    role2 = Role(name='Editor', invite_code='test-role-code')
    db.session.add_all([role1, role2])

    db.session.commit()

    return {
        'entity': entity,
        'entity_type': entity_type,
        'roles': [role1, role2]
    }



def test_register_user_with_entity(test_client, test_data):
    """Тест: регистрация пользователя с invite_code для Entity"""
    # Отправляем запрос с данными для регистрации
    response = test_client.post('/api/auth/signup', json={
        'name': 'John Doe',
        'email': 'john.doe@example.com',
        'password': 'securepassword',
        'invite_code': 'test-entity-code'
    })

    print(response.json)

    # Проверяем, что запрос успешен
    assert response.status_code == 201
    assert response.json['message'] == 'Пользователь успешно зарегистрирован'
    assert 'access_token' in response.json

    # Проверяем, что пользователь создан в базе данных
    user = User.query.filter_by(email='john.doe@example.com').first()
    assert user is not None
    assert user