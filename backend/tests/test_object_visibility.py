import pytest
from flask_jwt_extended import create_access_token

from application.models import Object, ObjectType, User
from .fixtures import app, client, db_session


def auth(db_session, role):
    user = User(name=role, email=f'{role}@example.test', role=role)
    db_session.add(user)
    db_session.commit()
    return user, {'Authorization': f'Bearer {create_access_token(identity=str(user.id))}'}


@pytest.fixture
def records(db_session):
    kind = ObjectType(name='Ученики', code='students')
    visible = Object(name='Видимый', type=kind)
    hidden = Object(name='Скрытый', type=kind, is_hidden=True)
    visible.children.append(hidden)
    db_session.add_all([kind, visible, hidden])
    db_session.commit()
    return visible, hidden


@pytest.mark.parametrize('role', ['admin', 'teacher', 'student'])
@pytest.mark.parametrize('path', ['/api/objects', '/api/objects/students'])
def test_lists_hide_records_and_relationships_by_default(client, db_session, records, role, path):
    _, headers = auth(db_session, role)
    visible, hidden = records
    result = client.get(path, headers=headers)
    assert result.status_code == 200
    assert [item['id'] for item in result.json] == [visible.id]
    assert result.json[0]['is_hidden'] is False
    assert result.json[0]['children'] == []
    result = client.get(path + '?include_hidden=true', headers=headers)
    if role == 'admin':
        assert result.status_code == 200
        assert {item['id'] for item in result.json} == {visible.id, hidden.id}
        parent = next(item for item in result.json if item['id'] == visible.id)
        assert parent['children'][0]['id'] == hidden.id
        assert parent['children'][0]['is_hidden'] is True
    else:
        assert result.status_code == 403


def test_admin_can_hide_edit_and_unhide_without_losing_data(client, db_session, records):
    _, headers = auth(db_session, 'admin')
    visible, hidden = records
    path = f'/api/objects/{visible.id}'
    response = client.put(path, headers=headers, json={'name': visible.name, 'is_hidden': True})
    assert response.status_code == 200
    assert response.json['is_hidden'] is True
    assert response.json['children'][0]['id'] == hidden.id
    response = client.put(path, headers=headers, json={'name': 'Новое имя'})
    assert response.status_code == 200
    assert response.json['is_hidden'] is True
    response = client.put(path, headers=headers, json={'name': 'Новое имя', 'is_hidden': False})
    assert response.status_code == 200
    assert response.json['is_hidden'] is False
    db_session.expire_all()
    assert visible.children == [hidden]
    assert visible.deleted_at is None


@pytest.mark.parametrize('role', ['teacher', 'student'])
def test_nonadmin_cannot_toggle_even_owned_records(client, db_session, records, role):
    user, headers = auth(db_session, role)
    visible, hidden = records
    visible.owners.append(user)
    hidden.owners.append(user)
    db_session.commit()
    for record, flag in [(visible, True), (hidden, False)]:
        response = client.put(f'/api/objects/{record.id}', headers=headers,
                              json={'name': 'Attempted change', 'is_hidden': flag})
        assert response.status_code == 403
    db_session.expire_all()
    assert visible.name == 'Видимый'
    assert visible.is_hidden is False
    assert hidden.is_hidden is True
    assert visible.is_approved is True  # Rejection must not deapprove the card.


@pytest.mark.parametrize('flag', ['true', 1, None, []])
def test_visibility_requires_boolean(client, db_session, records, flag):
    _, headers = auth(db_session, 'admin')
    response = client.put(f'/api/objects/{records[0].id}', headers=headers,
                          json={'name': 'Name', 'is_hidden': flag})
    assert response.status_code == 422


@pytest.mark.parametrize('role,flag,status', [('admin', True, 201), ('teacher', True, 403), ('teacher', False, 201)])
def test_creation_visibility(client, db_session, records, role, flag, status):
    _, headers = auth(db_session, role)
    response = client.post('/api/objects/students/create', headers=headers,
                           json={'name': 'New student', 'is_hidden': flag})
    assert response.status_code == status
    if status == 201:
        assert response.json['is_hidden'] is flag


def test_visible_only_editor_preserves_hidden_relationships(client, db_session, records):
    _, headers = auth(db_session, 'teacher')
    visible, hidden = records
    response = client.put(f'/api/objects/{visible.id}/children', headers=headers, json={'children': []})
    assert response.status_code == 200
    assert response.json == []
    db_session.expire_all()
    assert visible.children == [hidden]
    other = Object(name='Other', type=visible.type)
    db_session.add(other)
    db_session.commit()
    response = client.put(f'/api/objects/{other.id}/children', headers=headers, json={'children': [hidden.id]})
    assert response.status_code == 403
    assert other.children == []


def test_admin_can_remove_hidden_relationship(client, db_session, records):
    _, headers = auth(db_session, 'admin')
    response = client.put(f'/api/objects/{records[0].id}/children', headers=headers, json={'children': []})
    assert response.status_code == 200
    db_session.expire_all()
    assert records[0].children == []


def test_migration_keeps_existing_records_visible(db_session, records):
    import importlib.util
    from pathlib import Path
    from alembic.migration import MigrationContext
    from alembic.operations import Operations
    from sqlalchemy import text

    path = Path(__file__).parents[1] / 'migrations/versions/a10710c0de01_add_object_visibility.py'
    spec = importlib.util.spec_from_file_location('visibility_migration', path)
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    connection = db_session.connection()
    connection.execute(text('ALTER TABLE objects DROP COLUMN is_hidden'))
    with Operations.context(MigrationContext.configure(connection)):
        migration.upgrade()
    assert connection.execute(text('SELECT is_hidden FROM objects')).scalars().all() == [False, False]
    db_session.commit()
