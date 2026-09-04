from flask_jwt_extended import create_access_token

from application.infrastructure import bcrypt
from application.models import Object, ObjectType, User
from application.presenters import present_object
from .fixtures import *


def _headers(user):
    token = create_access_token(identity=str(user.id))
    return {'Authorization': f'Bearer {token}'}


def test_admin_lists_users_with_identity_object(client, db_session):
    admin = User(name='Admin', email='admin@example.test', password='hash', role='admin')
    student = User(name='Student', email='student@example.test', password='hash', role='student')
    object_type = ObjectType(name='Ученики', code='students')
    student_object = Object(name='Иван Иванов', type=object_type)
    student.identity_object = student_object
    db_session.add_all([admin, student, object_type, student_object])
    db_session.commit()

    response = client.get('/api/users', headers=_headers(admin))

    assert response.status_code == 200
    payload = response.get_json()
    presented_student = next(user for user in payload if user['id'] == student.id)
    assert presented_student['identity_object'] == {
        'id': student_object.id,
        'name': student_object.name,
        'type': object_type.code,
    }
    assert 'reset_token' not in presented_student

    assert present_object(student_object, admin)['identity_user']['id'] == student.id
    assert present_object(student_object, student)['identity_user'] is None


def test_non_admin_cannot_list_users_or_generate_reset_link(client, test_user, auth_headers):
    list_response = client.get('/api/users', headers=auth_headers)
    reset_response = client.post(
        f'/api/users/{test_user.id}/password-reset-link', headers=auth_headers,
    )

    assert list_response.status_code == 403
    assert reset_response.status_code == 403


def test_admin_generates_rotating_password_reset_link(client, app, db_session):
    admin = User(name='Admin', email='admin@example.test', password='hash', role='admin')
    user = User(
        name='Student',
        email='student@example.test',
        password=bcrypt.generate_password_hash('password123').decode('utf-8'),
        role='student',
    )
    db_session.add_all([admin, user])
    db_session.commit()

    first = client.post(
        f'/api/users/{user.id}/password-reset-link', headers=_headers(admin),
    )
    first_url = first.get_json()['reset_url']
    first_token = first_url.rsplit('=', 1)[1]
    second = client.post(
        f'/api/users/{user.id}/password-reset-link', headers=_headers(admin),
    )
    second_url = second.get_json()['reset_url']

    assert first.status_code == 200
    assert second.status_code == 200
    assert first_url.startswith(f"{app.config['BASE_URL']}/password/reset?token=")
    assert second_url != first_url
    assert user.reset_token != first_token


def test_admin_user_endpoints_return_not_found(client, db_session):
    admin = User(name='Admin', email='admin@example.test', password='hash', role='admin')
    db_session.add(admin)
    db_session.commit()

    details = client.get('/api/users/999999', headers=_headers(admin))
    reset = client.post('/api/users/999999/password-reset-link', headers=_headers(admin))

    assert details.status_code == 404
    assert reset.status_code == 404
