from app.models import ObjectType
from app.presenters.presenters import present_object_type
from .fixtures import *


def test_object_types_success(client, db_session, test_user, auth_headers):
    """
    Тест успешного получения типов объектов.
    """
    # Создаем mock-данные ObjectType
    object_type1 = ObjectType(
        name="Type1",
        code="type1",
        available_attributes=["attr1", "attr2"],
        available_params=["param1"],
    )
    object_type2 = ObjectType(
        name="Type2",
        code="type2",
        available_attributes=["attr3"],
        available_params=["param2", "param3"],
    )
    db_session.add_all([object_type1, object_type2])
    db_session.commit()

    # Отправляем запрос
    response = client.get('/api/objects/', headers=auth_headers)
    assert response.status_code == 200

    # Проверяем, что данные корректно представлены
    expected_data = [present_object_type(object_type1, test_user), present_object_type(object_type2, test_user)]
    assert response.json == expected_data


def test_object_types_unauthorized(client):
    """
    Тест получения типов объектов без авторизации.
    """
    response = client.get('/api/objects/')
    assert response.status_code == 401


def test_object_types_no_data(client, auth_headers):
    """
    Тест обработки ситуации, когда нет доступных типов объектов.
    """
    response = client.get('/api/objects/', headers=auth_headers)
    assert response.status_code == 200
    assert response.json == []
