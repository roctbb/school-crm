from flask_jwt_extended import create_access_token

from application.infrastructure import bcrypt
from application.models import Object, ObjectType, User
from .fixtures import *


def create_relationship(db_session):
    parent_type = ObjectType(name='Groups', code='groups')
    child_type = ObjectType(name='Students', code='students')
    parent = Object(name='7C class', type=parent_type)
    child = Object(name='Student', type=child_type)
    parent.children.append(child)
    db_session.add_all([parent_type, child_type, parent, child])
    db_session.commit()
    return parent, child


def test_admin_can_remove_single_object_relationship(client, db_session):
    admin = User(
        name='Admin',
        email='admin@example.com',
        password=bcrypt.generate_password_hash('password123').decode('utf-8'),
        role='admin',
    )
    db_session.add(admin)
    parent, child = create_relationship(db_session)
    token = create_access_token(identity=str(admin.id))

    response = client.delete(
        f'/api/objects/{parent.id}/children/{child.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == 200
    assert response.get_json() == {
        'deleted': True,
        'parent_id': parent.id,
        'child_id': child.id,
    }
    db_session.expire_all()
    assert db_session.get(Object, parent.id).children == []
    assert db_session.get(Object, child.id).parents == []


def test_user_without_parent_edit_access_cannot_remove_relationship(
    client, db_session, test_user, auth_headers
):
    parent, child = create_relationship(db_session)

    response = client.delete(
        f'/api/objects/{parent.id}/children/{child.id}',
        headers=auth_headers,
    )

    assert response.status_code == 403
    db_session.expire_all()
    assert [item.id for item in db_session.get(Object, parent.id).children] == [child.id]


def test_removing_missing_relationship_returns_not_found(client, db_session):
    admin = User(
        name='Admin',
        email='admin@example.com',
        password=bcrypt.generate_password_hash('password123').decode('utf-8'),
        role='admin',
    )
    parent_type = ObjectType(name='Groups', code='groups')
    child_type = ObjectType(name='Students', code='students')
    parent = Object(name='7C class', type=parent_type)
    child = Object(name='Student', type=child_type)
    db_session.add_all([admin, parent_type, child_type, parent, child])
    db_session.commit()
    token = create_access_token(identity=str(admin.id))

    response = client.delete(
        f'/api/objects/{parent.id}/children/{child.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == 404
    assert response.get_json()['message'] == 'Связь между объектами не найдена'
