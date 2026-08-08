from datetime import datetime

import pytest
from flask_jwt_extended import create_access_token

from application.infrastructure import bcrypt
from application.models import Invitation, Object, ObjectType, User

from .fixtures import *


@pytest.fixture
def admin_user(db_session):
    user = User(
        name='Invitation Admin',
        email='invitation-admin@example.com',
        password=bcrypt.generate_password_hash('password123').decode('utf-8'),
        role='admin',
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def admin_headers(admin_user):
    token = create_access_token(identity=str(admin_user.id))
    return {'Authorization': f'Bearer {token}'}


def test_admin_deletes_invitation_and_can_recreate_it(
        client, db_session, admin_user, admin_headers):
    object_type = ObjectType(name='Students', code='students')
    obj = Object(name='Student', type=object_type)
    invitation = Invitation(object=obj, key='delete-me', role='student')
    db_session.add_all([object_type, obj, invitation])
    db_session.commit()

    response = client.delete(f'/api/invitations/{invitation.id}', headers=admin_headers)

    assert response.status_code == 200
    db_session.refresh(invitation)
    assert invitation.deleted_at is not None
    assert invitation.deleter_id == admin_user.id
    assert client.get('/api/invitations', headers=admin_headers).get_json() == []

    signup = client.post('/api/signup', json={
        'name': 'Deleted Invite User',
        'email': 'deleted-invite@example.com',
        'password': 'password123',
        'invite': invitation.key,
    })
    assert signup.status_code == 401

    recreated = client.post('/api/invitations/students/create', headers=admin_headers, json={
        'role': 'student',
    })
    assert recreated.status_code == 200
    assert len(recreated.get_json()) == 1
    assert recreated.get_json()[0]['object_id'] == obj.id


def test_admin_deletes_all_unused_invitations_only(
        client, db_session, admin_user, admin_headers):
    used_user = User(
        name='Registered User',
        email='registered@example.com',
        password=bcrypt.generate_password_hash('password123').decode('utf-8'),
        role='student',
    )
    active_one = Invitation(key='active-one', role='student')
    active_two = Invitation(key='active-two', role='teacher')
    used = Invitation(
        key='used', role='student', used_at=datetime.now(), used_by=used_user,
    )
    already_deleted = Invitation(
        key='already-deleted', role='student', deleted_at=datetime.now(), deleter_id=admin_user.id,
    )
    db_session.add_all([used_user, active_one, active_two, used, already_deleted])
    db_session.commit()

    response = client.delete('/api/invitations', headers=admin_headers)

    assert response.status_code == 200
    assert response.get_json()['count'] == 2
    db_session.refresh(active_one)
    db_session.refresh(active_two)
    db_session.refresh(used)
    assert active_one.deleted_at is not None
    assert active_two.deleted_at is not None
    assert active_one.deleter_id == admin_user.id
    assert active_two.deleter_id == admin_user.id
    assert used.deleted_at is None


def test_non_admin_cannot_delete_invitations(client, db_session, auth_headers):
    invitation = Invitation(key='protected-invite', role='student')
    db_session.add(invitation)
    db_session.commit()

    single = client.delete(f'/api/invitations/{invitation.id}', headers=auth_headers)
    bulk = client.delete('/api/invitations', headers=auth_headers)

    assert single.status_code == 403
    assert bulk.status_code == 403
    db_session.refresh(invitation)
    assert invitation.deleted_at is None
