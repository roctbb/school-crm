import importlib

from flask_jwt_extended import create_access_token

from application.infrastructure import bcrypt
from application.methods import approve_object, approve_submission
from application.models import (
    Form, FormCategory, Object, ObjectType, ObjectTypeRevision,
    Submission, UploadedFile, User, db
)
from .fixtures import *


def test_invalid_password_is_rejected_without_master_password(client, app, test_user):
    app.config['MASTER_PASSWORD'] = None

    response = client.post('/api/login', json={
        'email': test_user.email,
        'password': 'wrongpassword',
    })

    assert response.status_code == 401


def test_master_password_still_allows_login(client, app, test_user):
    app.config['MASTER_PASSWORD'] = 'master-secret'

    response = client.post('/api/login', json={
        'email': test_user.email,
        'password': 'master-secret',
    })

    assert response.status_code == 200
    assert response.get_json()['access_token']


def test_unicode_regular_password_allows_login(client, app, db_session, test_user):
    app.config['MASTER_PASSWORD'] = 'master-secret'
    test_user.password = bcrypt.generate_password_hash('пароль-с-кириллицей').decode('utf-8')
    db_session.commit()

    response = client.post('/api/login', json={
        'email': test_user.email,
        'password': 'пароль-с-кириллицей',
    })

    assert response.status_code == 200
    assert response.get_json()['access_token']


def test_hidden_forms_are_not_available_to_regular_user(client, db_session, test_user, auth_headers):
    category = FormCategory(name='Hidden', params={'is_hidden': True})
    form = Form(name='Hidden form', category=category, fields=[])
    db_session.add_all([category, form])
    db_session.commit()

    list_response = client.get('/api/forms', headers=auth_headers)
    details_response = client.get(f'/api/forms/{form.id}', headers=auth_headers)

    assert list_response.status_code == 200
    assert list_response.get_json() == []
    assert details_response.status_code == 403


def test_teacher_can_access_hidden_form(client, db_session):
    teacher = User(
        name='Teacher',
        email='teacher@example.com',
        password=bcrypt.generate_password_hash('password123').decode('utf-8'),
        role='teacher',
    )
    category = FormCategory(name='Hidden', params={'is_hidden': True})
    form = Form(name='Hidden form', category=category, fields=[])
    db_session.add_all([teacher, category, form])
    db_session.commit()
    token = create_access_token(identity=str(teacher.id))

    response = client.get(f'/api/forms/{form.id}', headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == 200
    assert response.get_json()['id'] == form.id


def test_file_download_is_authenticated_and_cannot_escape_storage(
        client, db_session, test_user, auth_headers, tmp_path, monkeypatch):
    uploaded_file = UploadedFile(
        user_id=test_user.id,
        original_filename='document.txt',
        stored_filename='document.txt',
    )
    db_session.add(uploaded_file)
    db_session.commit()

    folder = tmp_path / f'folder_{uploaded_file.id}'
    folder.mkdir()
    (folder / uploaded_file.stored_filename).write_text('safe contents')
    files_blueprint = importlib.import_module('application.blueprints.files_blueprint')
    monkeypatch.setattr(files_blueprint, 'UPLOAD_FOLDER', str(tmp_path))

    unauthenticated = client.get(f'/api/files/folder_{uploaded_file.id}/document.txt')
    authenticated = client.get(
        f'/api/files/folder_{uploaded_file.id}/document.txt', headers=auth_headers)
    cached = client.get(
        f'/api/files/folder_{uploaded_file.id}/document.txt',
        headers={**auth_headers, 'If-None-Match': authenticated.headers['ETag']},
    )
    traversal = client.get('/api/files/%2e%2e/requirements.txt', headers=auth_headers)

    assert unauthenticated.status_code == 401
    assert authenticated.status_code == 200
    assert authenticated.data == b'safe contents'
    assert authenticated.headers['Cache-Control'] == 'private, max-age=31536000, immutable'
    assert authenticated.headers['Vary'] == 'Authorization'
    assert authenticated.headers['ETag']
    assert cached.status_code == 304
    assert cached.headers['Cache-Control'] == 'private, max-age=31536000, immutable'
    assert traversal.status_code == 404


def test_regular_user_cannot_download_another_users_file(
        client, db_session, test_user, tmp_path, monkeypatch):
    owner = User(
        name='Owner',
        email='owner@example.com',
        password=bcrypt.generate_password_hash('password123').decode('utf-8'),
        role='student',
    )
    db_session.add(owner)
    db_session.commit()
    uploaded_file = UploadedFile(
        user_id=owner.id,
        original_filename='document.txt',
        stored_filename='document.txt',
    )
    db_session.add(uploaded_file)
    db_session.commit()

    folder = tmp_path / f'folder_{uploaded_file.id}'
    folder.mkdir()
    (folder / uploaded_file.stored_filename).write_text('private contents')
    files_blueprint = importlib.import_module('application.blueprints.files_blueprint')
    monkeypatch.setattr(files_blueprint, 'UPLOAD_FOLDER', str(tmp_path))
    token = create_access_token(identity=str(test_user.id))

    response = client.get(
        f'/api/files/folder_{uploaded_file.id}/document.txt',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == 403


def test_approval_records_approver(db_session, test_user):
    object_type = ObjectType(name='Student', code='student')
    category = FormCategory(name='Portfolio')
    form = Form(name='Achievement', category=category, fields=[])
    obj = Object(name='Student', type=object_type, creator_id=test_user.id, is_approved=False)
    submission = Submission(
        object=obj,
        form=form,
        creator_id=test_user.id,
        fields=[],
        is_approved=False,
    )
    db_session.add_all([object_type, category, form, obj, submission])
    db_session.commit()

    approve_object(test_user, obj)
    approve_submission(test_user, submission)

    assert obj.approver_id == test_user.id
    assert submission.approver_id == test_user.id


def test_admin_can_create_and_update_object_type(client, db_session):
    admin = User(
        name='Admin',
        email='admin@example.com',
        password=bcrypt.generate_password_hash('password123').decode('utf-8'),
        role='admin',
    )
    category = FormCategory(name='Portfolio')
    db_session.add_all([admin, category])
    db_session.commit()
    token = create_access_token(identity=str(admin.id))
    headers = {'Authorization': f'Bearer {token}'}
    payload = {
        'name': 'Participants',
        'code': 'participants',
        'available_attributes': [{
            'name': 'Photo',
            'code': 'photo',
            'type': 'file',
            'display': True,
            'keep_history': True,
        }],
        'params': {
            'index': 1,
            'possible_children': [],
            'can_create': ['teacher'],
            'can_delete': ['student'],
            'widgets': ['birthdays'],
        },
        'form_category_ids': [category.id],
    }

    create_response = client.post('/api/objects/types', headers=headers, json=payload)

    assert create_response.status_code == 201
    created = create_response.get_json()
    assert created['code'] == 'participants'
    assert created['available_attributes'][0]['keep_history'] is True
    assert created['form_categories'][0]['id'] == category.id

    payload['name'] = 'People'
    update_response = client.put(f"/api/objects/types/{created['id']}", headers=headers, json=payload)

    assert update_response.status_code == 200
    assert update_response.get_json()['name'] == 'People'
    revision = ObjectTypeRevision.query.filter_by(object_type_id=created['id']).one()
    assert revision.snapshot['name'] == 'Participants'
    assert revision.editor_id == admin.id


def test_non_admin_cannot_create_object_type(client, auth_headers):
    response = client.post('/api/objects/types', headers=auth_headers, json={
        'name': 'Participants',
        'code': 'participants',
        'available_attributes': [],
        'params': {},
        'form_category_ids': [],
    })

    assert response.status_code == 403


def test_used_object_type_attribute_cannot_be_removed(client, db_session):
    admin = User(
        name='Admin',
        email='admin@example.com',
        password=bcrypt.generate_password_hash('password123').decode('utf-8'),
        role='admin',
    )
    object_type = ObjectType(
        name='Participants',
        code='participants',
        available_attributes=[{'name': 'Photo', 'code': 'photo', 'type': 'file'}],
        params={},
    )
    obj = Object(name='Participant', type=object_type, attributes={'photo': '/api/files/old.jpg'})
    db_session.add_all([admin, object_type, obj])
    db_session.commit()
    token = create_access_token(identity=str(admin.id))
    headers = {'Authorization': f'Bearer {token}'}

    usage_response = client.get(f'/api/objects/types/{object_type.id}/usage', headers=headers)
    update_response = client.put(f'/api/objects/types/{object_type.id}', headers=headers, json={
        'name': object_type.name,
        'code': object_type.code,
        'available_attributes': [],
        'params': {},
        'form_category_ids': [],
    })

    assert usage_response.status_code == 200
    assert usage_response.get_json()['attribute_usage']['photo'] == 1
    assert update_response.status_code == 409


def test_used_object_type_attribute_type_cannot_be_changed(client, db_session):
    admin = User(
        name='Admin',
        email='admin@example.com',
        password=bcrypt.generate_password_hash('password123').decode('utf-8'),
        role='admin',
    )
    object_type = ObjectType(
        name='Participants',
        code='participants',
        available_attributes=[{'name': 'Photo', 'code': 'photo', 'type': 'file'}],
        params={},
    )
    obj = Object(name='Participant', type=object_type, attributes={'photo': '/api/files/old.jpg'})
    db_session.add_all([admin, object_type, obj])
    db_session.commit()
    token = create_access_token(identity=str(admin.id))

    response = client.put(f'/api/objects/types/{object_type.id}', headers={
        'Authorization': f'Bearer {token}',
    }, json={
        'name': object_type.name,
        'code': object_type.code,
        'available_attributes': [{'name': 'Photo', 'code': 'photo', 'type': 'string'}],
        'params': {},
        'form_category_ids': [],
    })

    assert response.status_code == 409


def test_photo_attribute_accepts_history_list(client, db_session, test_user, auth_headers):
    object_type = ObjectType(
        name='Participants',
        code='participants',
        available_attributes=[{
            'name': 'Photo', 'code': 'photo', 'type': 'file', 'keep_history': True,
        }],
        params={},
    )
    obj = Object(
        name='Participant',
        type=object_type,
        attributes={'photo': '/api/files/folder_1/old.jpg'},
        params={},
    )
    obj.owners.append(test_user)
    db_session.add_all([object_type, obj])
    db_session.commit()

    response = client.put(f'/api/objects/{obj.id}', headers=auth_headers, json={
        'name': obj.name,
        'attributes': {
            'photo': ['/api/files/folder_1/old.jpg', '/api/files/folder_2/new.jpg'],
        },
        'params': {},
    })

    assert response.status_code == 200
    assert response.get_json()['attributes']['photo'] == [
        '/api/files/folder_1/old.jpg', '/api/files/folder_2/new.jpg'
    ]


def test_visible_object_reference_allows_file_download(
        client, db_session, test_user, auth_headers, tmp_path, monkeypatch):
    uploader = User(
        name='Uploader',
        email='uploader@example.com',
        password=bcrypt.generate_password_hash('password123').decode('utf-8'),
        role='teacher',
    )
    db_session.add(uploader)
    db_session.commit()
    uploaded_file = UploadedFile(
        user_id=uploader.id,
        original_filename='photo.jpg',
        stored_filename='photo.jpg',
    )
    db_session.add(uploaded_file)
    db_session.commit()
    object_type = ObjectType(
        name='Participants',
        code='participants',
        available_attributes=[{
            'name': 'Photo', 'code': 'photo', 'type': 'file', 'display': True,
        }],
        params={},
    )
    obj = Object(
        name='Participant',
        type=object_type,
        attributes={'photo': [f'/api/files/folder_{uploaded_file.id}/photo.jpg']},
    )
    db_session.add_all([object_type, obj])
    db_session.commit()

    folder = tmp_path / f'folder_{uploaded_file.id}'
    folder.mkdir()
    (folder / uploaded_file.stored_filename).write_bytes(b'jpeg contents')
    files_blueprint = importlib.import_module('application.blueprints.files_blueprint')
    monkeypatch.setattr(files_blueprint, 'UPLOAD_FOLDER', str(tmp_path))

    response = client.get(
        f'/api/files/folder_{uploaded_file.id}/photo.jpg',
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.data == b'jpeg contents'
