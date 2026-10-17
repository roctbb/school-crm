import base64
from datetime import datetime, timezone

import pytest
from flask_jwt_extended import create_access_token

from application.infrastructure import bcrypt, db
from application.models import Invitation, Object, ObjectType, OAuthClient, User
from application.oidc import oidc_user_info
from .fixtures import *


def _basic_auth(secret='object-api-secret', client_id='group-service'):
    value = base64.b64encode(f'{client_id}:{secret}'.encode()).decode()
    return {'Authorization': f'Basic {value}'}


@pytest.fixture
def object_api(app):
    students = ObjectType(name='Ученики', code='students')
    teachers = ObjectType(name='Учителя', code='teachers')
    api_client = OAuthClient(
        client_id='group-service', name='Группы',
        client_secret_hash=bcrypt.generate_password_hash('object-api-secret').decode(),
        redirect_uris=['https://groups.example.test/callback'],
        allowed_object_types=['students'],
    )
    db.session.add_all([students, teachers, api_client])
    db.session.commit()
    return api_client, students, teachers


def test_list_includes_unregistered_students_and_excludes_private_data(client, object_api):
    _api_client, students, teachers = object_api
    unregistered = Object(name='Иван Иванов', type=students, attributes={
        'grade': ['7'], 'email': 'private@example.test', 'birthday': '1.2.2012',
        'medical_notes': 'private', 'photo': '/private.jpg',
    }, params={'secret': 'private'})
    registered = Object(name='Анна Петрова', type=students, attributes={'grade': 8})
    user = User(name='Account', email='registered@example.test', role='student')
    user.identity_object = registered
    registered.owners.append(user)
    db.session.add_all([
        unregistered, registered, user,
        Object(name='Скрытый ученик', type=students, is_hidden=True),
        Object(name='Удалённый ученик', type=students,
               deleted_at=datetime.now(timezone.utc).replace(tzinfo=None)),
        Object(name='Учитель', type=teachers),
    ])
    db.session.commit()

    response = client.get('/api/external/objects/students', headers=_basic_auth())

    assert response.status_code == 200, response.get_json()
    assert response.headers['Cache-Control'] == 'no-store'
    assert response.get_json() == {
        'items': [{
            'sub': obj.sso_subject, 'object_id': obj.id, 'object_type': 'students',
            'name': obj.name, 'grade': grade,
        } for obj, grade in [(unregistered, 7), (registered, 8)]],
        'next_after_id': None,
    }


def test_sub_matches_oidc_after_signup(client, object_api):
    _api_client, students, _teachers = object_api
    student = Object(name='Иван Иванов', type=students)
    invitation = Invitation(key='external-api-student', role='student', object=student)
    db.session.add_all([student, invitation])
    db.session.commit()
    before = client.get('/api/external/objects/students', headers=_basic_auth()).get_json()
    assert student.identity_user is None

    signup = client.post('/api/signup', json={
        'name': 'Имя аккаунта', 'email': 'new-student@example.test',
        'password': 'securepassword', 'invite': invitation.key,
    })
    assert signup.status_code == 201, signup.get_json()
    user = User.query.filter_by(email='new-student@example.test').one()
    assert user.identity_object.id == student.id
    assert oidc_user_info(user, 'openid profile')['sub'] == before['items'][0]['sub']
    assert client.get(
        '/api/external/objects/students', headers=_basic_auth(),
    ).get_json() == before


def test_cursor_pagination_and_name_search(client, object_api):
    _api_client, students, _teachers = object_api
    objects = [Object(name=name, type=students) for name in [
        'Иван Иванов', 'Анна Петрова', 'Иван Петров', 'Тест %_слэш/',
    ]]
    db.session.add_all(objects)
    db.session.commit()
    first = client.get('/api/external/objects/students', headers=_basic_auth(),
                       query_string={'limit': 1, 'q': 'иван'}).get_json()
    assert [item['object_id'] for item in first['items']] == [objects[0].id]
    assert first['next_after_id'] == objects[0].id
    second = client.get('/api/external/objects/students', headers=_basic_auth(), query_string={
        'limit': 1, 'q': 'иван', 'after_id': first['next_after_id'],
    }).get_json()
    assert [item['object_id'] for item in second['items']] == [objects[2].id]
    assert second['next_after_id'] is None
    literal = client.get('/api/external/objects/students', headers=_basic_auth(),
                         query_string={'q': '%_слэш/'}).get_json()
    assert [item['object_id'] for item in literal['items']] == [objects[3].id]
    empty = client.get('/api/external/objects/students', headers=_basic_auth(),
                       query_string={'after_id': objects[-1].id}).get_json()
    assert empty == {'items': [], 'next_after_id': None}


@pytest.mark.parametrize('headers', [
    {}, {'Authorization': 'Bearer user-token'}, _basic_auth('wrong-secret'),
    _basic_auth(client_id='missing-client'), {'Authorization': 'Basic invalid'},
])
def test_authentication_is_required(client, object_api, headers):
    response = client.get('/api/external/objects/students', headers=headers)
    assert response.status_code == 401
    assert response.headers['WWW-Authenticate'].startswith('Basic ')
    assert response.headers['Cache-Control'] == 'no-store'


@pytest.mark.parametrize('field', ['is_active', 'is_confidential'])
def test_disabled_and_public_clients_are_rejected(client, object_api, field):
    api_client, _students, _teachers = object_api
    setattr(api_client, field, False)
    db.session.commit()
    response = client.get('/api/external/objects/students', headers=_basic_auth())
    assert response.status_code == 401


def test_object_types_need_separate_explicit_permission(client, object_api):
    api_client, students, _teachers = object_api
    api_client.can_send_notifications = True
    api_client.allowed_roles = ['student', 'teacher', 'admin']
    api_client.allowed_scopes = ['openid', 'profile']
    db.session.commit()
    assert client.get('/api/external/objects/teachers', headers=_basic_auth()).status_code == 403
    api_client.allowed_object_types = []
    db.session.commit()
    assert client.get('/api/external/objects/students', headers=_basic_auth()).status_code == 403
    api_client.allowed_object_types = ['students', 'missing']
    students.params = {'is_hidden': True}
    db.session.commit()
    assert client.get('/api/external/objects/students', headers=_basic_auth()).status_code == 404
    assert client.get('/api/external/objects/missing', headers=_basic_auth()).status_code == 404


@pytest.mark.parametrize('params', [
    {'limit': '0'}, {'limit': '201'}, {'limit': 'abc'}, {'limit': ''},
    {'after_id': '-1'}, {'after_id': '1.5'}, {'after_id': '2147483648'},
    {'after_id': '9' * 100}, {'q': 'x' * 201},
])
def test_invalid_query_parameters(client, object_api, params):
    response = client.get('/api/external/objects/students', headers=_basic_auth(),
                          query_string=params)
    assert response.status_code == 422, response.get_json()


def test_other_object_types_are_supported_without_student_grade(client, object_api):
    api_client, _students, teachers = object_api
    api_client.allowed_object_types = ['teachers']
    teacher = Object(name='Учитель', type=teachers, attributes={'grade': 7})
    db.session.add(teacher)
    db.session.commit()
    response = client.get('/api/external/objects/teachers', headers=_basic_auth())
    assert response.status_code == 200
    assert response.get_json()['items'] == [{
        'sub': teacher.sso_subject, 'object_id': teacher.id, 'object_type': 'teachers',
        'name': teacher.name, 'grade': None,
    }]


def _admin_headers(user):
    user.role = 'admin'
    db.session.commit()
    return {'Authorization': f'Bearer {create_access_token(identity=str(user.id))}'}


def _client_payload(**overrides):
    return {
        'client_id': 'new-group-service', 'name': 'Новый сервис',
        'redirect_uris': ['https://groups.example.test/callback'],
        **overrides,
    }


def test_admin_configures_and_revokes_object_access(client, object_api, test_user):
    headers = _admin_headers(test_user)
    payload = _client_payload()
    created = client.post('/api/oauth/clients', json=payload, headers=headers)
    assert created.status_code == 201, created.get_json()
    data = created.get_json()
    assert data['allowed_object_types'] == []
    api_headers = _basic_auth(data['client_secret'], data['client_id'])
    assert client.get('/api/external/objects/students', headers=api_headers).status_code == 403

    endpoint = f"/api/oauth/clients/{data['id']}"
    granted = client.put(endpoint, json={**payload, 'allowed_object_types': ['students', 'students']},
                         headers=headers)
    assert granted.status_code == 200, granted.get_json()
    assert granted.get_json()['allowed_object_types'] == ['students']
    assert client.get('/api/external/objects/students', headers=api_headers).status_code == 200
    listed = client.get('/api/oauth/clients', headers=headers).get_json()
    assert next(row for row in listed if row['id'] == data['id'])['allowed_object_types'] == ['students']

    rotated = client.post(f'{endpoint}/rotate-secret', headers=headers)
    assert rotated.status_code == 200
    assert client.get('/api/external/objects/students', headers=api_headers).status_code == 401
    api_headers = _basic_auth(rotated.get_json()['client_secret'], data['client_id'])
    assert client.get('/api/external/objects/students', headers=api_headers).status_code == 200
    assert client.put(endpoint, json=payload, headers=headers).status_code == 200
    assert client.get('/api/external/objects/students', headers=api_headers).status_code == 403


@pytest.mark.parametrize('overrides', [
    {'allowed_object_types': 'students'}, {'allowed_object_types': [1]},
    {'allowed_object_types': None}, {'allowed_object_types': ['unknown']},
    {'allowed_object_types': ['students'], 'is_confidential': False},
])
def test_admin_rejects_invalid_object_access(client, object_api, test_user, overrides):
    response = client.post('/api/oauth/clients', json=_client_payload(**overrides),
                           headers=_admin_headers(test_user))
    assert response.status_code == 422, response.get_json()
    assert response.get_json()['field'] == 'allowed_object_types'
