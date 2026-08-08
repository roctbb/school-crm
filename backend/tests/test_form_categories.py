import pytest
from flask_jwt_extended import create_access_token

from application.infrastructure import bcrypt
from application.models import Form, FormCategory, ObjectType, User

from .fixtures import *


@pytest.fixture
def category_admin(db_session):
    user = User(
        name='Category Admin',
        email='category-admin@example.com',
        password=bcrypt.generate_password_hash('password123').decode('utf-8'),
        role='admin',
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def category_admin_headers(category_admin):
    token = create_access_token(identity=str(category_admin.id))
    return {'Authorization': f'Bearer {token}'}


def category_payload(name='Учебные результаты'):
    return {
        'name': name,
        'params': {
            'is_hidden': False,
            'is_private': True,
            'can_create': ['student'],
            'show_off_grouping': ['Учебный год'],
        },
        'common_fields': [{
            'name': 'Учебный год',
            'type': 'select',
            'required': True,
            'showoff': True,
            'options': ['2025/26', '2026/27'],
        }],
    }


def test_admin_creates_and_updates_form_category(
        client, db_session, category_admin, category_admin_headers):
    response = client.post(
        '/api/forms/categories',
        headers=category_admin_headers,
        json=category_payload(),
    )

    assert response.status_code == 201
    created = response.get_json()
    assert created['name'] == 'Учебные результаты'
    assert created['params']['is_private'] is True
    assert created['common_fields'][0]['name'] == 'Учебный год'
    category = db_session.get(FormCategory, created['id'])
    assert category.creator_id == category_admin.id

    payload = category_payload('Достижения')
    payload['params']['is_hidden'] = True
    payload['common_fields'][0]['options'] = ['2026/27', '2026/27', ' 2027/28 ']
    updated_response = client.put(
        f"/api/forms/categories/{created['id']}",
        headers=category_admin_headers,
        json=payload,
    )

    assert updated_response.status_code == 200
    updated = updated_response.get_json()
    assert updated['name'] == 'Достижения'
    assert updated['params']['is_hidden'] is True
    assert updated['common_fields'][0]['options'] == ['2026/27', '2027/28']


def test_non_admin_cannot_manage_form_categories(client, auth_headers):
    response = client.post('/api/forms/categories', headers=auth_headers, json=category_payload())
    assert response.status_code == 403


def test_admin_deletes_unused_form_category(
        client, db_session, category_admin, category_admin_headers):
    category = FormCategory(name='Пустая', creator_id=category_admin.id)
    db_session.add(category)
    db_session.commit()

    response = client.delete(
        f'/api/forms/categories/{category.id}',
        headers=category_admin_headers,
    )

    assert response.status_code == 200
    db_session.refresh(category)
    assert category.deleted_at is not None
    assert category.deleter_id == category_admin.id
    listed = client.get('/api/forms/categories', headers=category_admin_headers).get_json()
    assert all(item['id'] != category.id for item in listed)


def test_admin_cannot_delete_used_form_category(
        client, db_session, category_admin_headers):
    category = FormCategory(name='Используемая')
    form = Form(name='Анкета', category=category)
    object_type = ObjectType(name='Ученики', code='students', form_categories=[category])
    db_session.add_all([category, form, object_type])
    db_session.commit()

    usage = client.get(
        f'/api/forms/categories/{category.id}/usage',
        headers=category_admin_headers,
    )
    assert usage.status_code == 200
    assert usage.get_json()['form_count'] == 1
    assert usage.get_json()['object_type_count'] == 1

    response = client.delete(
        f'/api/forms/categories/{category.id}',
        headers=category_admin_headers,
    )
    assert response.status_code == 409
    db_session.refresh(category)
    assert category.deleted_at is None


def test_form_category_rejects_invalid_common_field(client, category_admin_headers):
    payload = category_payload()
    payload['common_fields'][0]['type'] = 'unknown'

    response = client.post('/api/forms/categories', headers=category_admin_headers, json=payload)

    assert response.status_code == 422
    assert response.get_json()['field'] == 'common_fields'
