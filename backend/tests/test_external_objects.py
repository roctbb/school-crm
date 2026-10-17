import base64
import importlib
from datetime import datetime, timezone

import pytest
from flask_jwt_extended import create_access_token

from application.infrastructure import bcrypt, db
from application.models import Invitation, Object, ObjectType, OAuthClient, UploadedFile, User
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
            'name': obj.name, 'grade': grade, 'picture': None,
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
@pytest.mark.parametrize('suffix', ['', '/11111111-1111-4111-8111-111111111111/avatar'])
def test_authentication_is_required(client, object_api, headers, suffix):
    response = client.get('/api/external/objects/students' + suffix, headers=headers)
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
        'name': teacher.name, 'grade': None, 'picture': None,
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


@pytest.fixture
def student_avatar(object_api, test_user, tmp_path, monkeypatch):
    api_client, students, _teachers = object_api
    api_client.allowed_scopes = ['openid', 'profile', 'avatar']
    students.available_attributes = [{'code': 'photo', 'name': 'Фото', 'type': 'file'}]
    uploaded_file = UploadedFile(
        user_id=test_user.id, original_filename='photo.png', stored_filename='photo.png',
    )
    db.session.add(uploaded_file)
    db.session.flush()
    folder = tmp_path / f'folder_{uploaded_file.id}'
    folder.mkdir()
    (folder / uploaded_file.stored_filename).write_bytes(b'\x89PNG\r\n\x1a\nphoto contents')
    photo = f'/api/files/folder_{uploaded_file.id}/photo.png'
    student = Object(name='Ученик без аккаунта', type=students, attributes={'photo': photo})
    db.session.add(student)
    db.session.commit()
    for module in ['application.methods.files_methods',
                   'application.blueprints.external_objects_blueprint']:
        monkeypatch.setattr(importlib.import_module(module), 'UPLOAD_FOLDER', str(tmp_path))
    return student, uploaded_file, tmp_path


def _avatar_path(student):
    return f'/api/external/objects/students/{student.sso_subject}/avatar'


def test_avatar_is_available_before_signup_and_stays_at_the_same_url(client, student_avatar):
    student, _uploaded_file, _storage = student_avatar
    assert student.identity_user is None
    roster = client.get('/api/external/objects/students', headers=_basic_auth()).get_json()
    picture = roster['items'][0]['picture']
    assert picture == 'http://localhost:5173' + _avatar_path(student)
    response = client.get(_avatar_path(student), headers=_basic_auth())
    assert response.status_code == 200
    assert response.data == b'\x89PNG\r\n\x1a\nphoto contents'
    assert response.mimetype == 'image/png'
    assert response.headers['Cache-Control'] == 'no-store'
    assert response.headers['Vary'] == 'Authorization'
    assert response.headers['X-Content-Type-Options'] == 'nosniff'

    invite = Invitation(key='student-with-photo', role='student', object=student)
    db.session.add(invite)
    db.session.commit()
    signup = client.post('/api/signup', json={
        'name': 'Новый аккаунт', 'email': 'photo-student@example.test',
        'password': 'securepassword', 'invite': invite.key,
    })
    assert signup.status_code == 201, signup.get_json()
    assert client.get('/api/external/objects/students', headers=_basic_auth()).get_json() == roster
    assert client.get(_avatar_path(student), headers=_basic_auth()).data == response.data


def test_avatar_checks_scope_type_permission_and_client_status_on_every_download(
        client, object_api, student_avatar):
    api_client, _students, _teachers = object_api
    student, _uploaded_file, _storage = student_avatar
    path = _avatar_path(student)
    initial = client.get(path, headers=_basic_auth())
    assert initial.status_code == 200
    cached_headers = {**_basic_auth(), 'If-None-Match': initial.headers['ETag']}

    api_client.allowed_scopes = ['openid', 'profile']
    db.session.commit()
    assert client.get(path, headers=cached_headers).status_code == 403
    assert client.get('/api/external/objects/students', headers=_basic_auth()).get_json()['items'][0]['picture'] is None
    api_client.allowed_scopes = ['openid', 'avatar']
    api_client.allowed_object_types = []
    db.session.commit()
    assert client.get(path, headers=cached_headers).status_code == 403
    api_client.allowed_object_types = ['students']
    api_client.is_active = False
    db.session.commit()
    assert client.get(path, headers=cached_headers).status_code == 401
    api_client.is_active = True
    api_client.is_confidential = False
    db.session.commit()
    assert client.get(path, headers=cached_headers).status_code == 401


@pytest.mark.parametrize('definition', [
    {'code': 'photo', 'type': 'file', 'is_hidden': True},
    {'code': 'photo', 'type': 'file', 'is_secret': True},
    {'code': 'photo', 'type': 'file', 'is_private': True},
    {'code': 'photo', 'type': 'string'},
    {'code': 'document', 'type': 'file'},
])
def test_avatar_respects_photo_field_visibility(client, object_api, student_avatar, definition):
    _api_client, students, _teachers = object_api
    student, _uploaded_file, _storage = student_avatar
    students.available_attributes = [definition]
    db.session.commit()
    assert client.get(_avatar_path(student), headers=_basic_auth()).status_code == 404
    items = client.get('/api/external/objects/students', headers=_basic_auth()).get_json()['items']
    assert items[0]['picture'] is None


@pytest.mark.parametrize('hidden', ['object', 'deleted', 'type'])
def test_hidden_or_deleted_objects_cannot_disclose_avatars(client, object_api, student_avatar, hidden):
    _api_client, students, _teachers = object_api
    student, _uploaded_file, _storage = student_avatar
    if hidden == 'object':
        student.is_hidden = True
    elif hidden == 'deleted':
        student.deleted_at = datetime.now(timezone.utc).replace(tzinfo=None)
    else:
        students.params = {'is_hidden': True}
    db.session.commit()
    assert client.get(_avatar_path(student), headers=_basic_auth()).status_code == 404


@pytest.mark.parametrize('photo', [None, '', 'https://[invalid', '/api/files/folder_99999/missing.png',
                                   '/api/files/folder_1/wrong-name.png',
                                   '/api/files/folder_2147483648/photo.png',
                                   '/api/files/folder_' + '9' * 5000 + '/photo.png'])
def test_missing_or_invalid_photos_return_null_and_404(client, student_avatar, photo):
    student, _uploaded_file, _storage = student_avatar
    student.attributes = {'photo': photo}
    db.session.commit()
    assert client.get(_avatar_path(student), headers=_basic_auth()).status_code == 404
    assert client.get('/api/external/objects/students', headers=_basic_auth()).get_json()['items'][0]['picture'] is None


def test_avatar_only_serves_the_current_photo_and_cannot_escape_its_folder(client, student_avatar):
    student, uploaded_file, storage = student_avatar
    second = UploadedFile(user_id=uploaded_file.user_id,
                          original_filename='new.png', stored_filename='new.png')
    db.session.add(second)
    db.session.flush()
    second_folder = storage / f'folder_{second.id}'
    second_folder.mkdir()
    (second_folder / second.stored_filename).write_bytes(b'new photo')
    student.attributes = {'photo': [student.attributes['photo'],
                                  f'/files/folder_{second.id}/{second.stored_filename}']}
    db.session.commit()
    assert client.get(_avatar_path(student), headers=_basic_auth()).data == b'new photo'
    (second_folder / second.stored_filename).unlink()
    assert client.get(_avatar_path(student), headers=_basic_auth()).data.endswith(b'photo contents')

    (storage / 'outside.png').write_bytes(b'must not be disclosed')
    uploaded_file.stored_filename = '../outside.png'
    student.attributes = {'photo': f'/api/files/folder_{uploaded_file.id}/../outside.png'}
    db.session.commit()
    assert client.get(_avatar_path(student), headers=_basic_auth()).status_code == 404


def test_avatar_subject_is_scoped_to_the_requested_type(client, object_api, student_avatar):
    api_client, _students, teachers = object_api
    student, _uploaded_file, _storage = student_avatar
    api_client.allowed_object_types = ['students', 'teachers']
    teacher = Object(name='Учитель', type=teachers, attributes=student.attributes)
    db.session.add(teacher)
    db.session.commit()
    assert client.get(f'/api/external/objects/teachers/{student.sso_subject}/avatar',
                      headers=_basic_auth()).status_code == 404
    assert client.get(f'/api/external/objects/students/{teacher.sso_subject}/avatar',
                      headers=_basic_auth()).status_code == 404


def test_private_photo_remains_available_to_its_owner_through_oidc(
        client, object_api, student_avatar, test_user):
    from application.methods.files_methods import get_user_avatar_file

    _api_client, students, _teachers = object_api
    student, uploaded_file, _storage = student_avatar
    students.available_attributes = [{'code': 'photo', 'type': 'file', 'is_private': True}]
    test_user.identity_object = student
    db.session.commit()
    assert get_user_avatar_file(test_user).id == uploaded_file.id
    assert client.get(_avatar_path(student), headers=_basic_auth()).status_code == 404
