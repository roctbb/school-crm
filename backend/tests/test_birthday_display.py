import importlib
from datetime import date, datetime

import pytest
from flask_jwt_extended import create_access_token

from application.methods.birthday_methods import birthday_this_week, week_dates
from application.models import BirthdayDisplay, Object, ObjectType, UploadedFile, User
from .fixtures import app, client, db_session

SETTINGS = '/api/settings/birthday-display'
PUBLIC = '/api/public/birthdays'
KEY = 'birthday-test-key'


@pytest.mark.parametrize('today,value,expected', [
    (date(2026, 9, 9), '09.09.2010', date(2026, 9, 9)),
    (date(2026, 9, 9), '2010-09-07', date(2026, 9, 7)),
    (date(2026, 9, 13), '13.09.2010', date(2026, 9, 13)),
    (date(2026, 9, 9), '14.09.2010', None),
    (date(2026, 9, 9), '06.09.2010', None),
    (date(2026, 12, 31), '01.01.2010', date(2027, 1, 1)),
    (date(2027, 1, 1), '31.12.2010', date(2026, 12, 31)),
    (date(2024, 2, 29), '29.02.2012', date(2024, 2, 29)),
    (date(2026, 2, 28), '29.02.2012', None),
    (date(2026, 9, 9), '31.02.2010', None),
    (date(2026, 9, 9), None, None),
    (date(2026, 9, 9), ['09.09.2010'], None),
    (date(2026, 9, 9), '', None),
])
def test_calendar_boundaries(today, value, expected):
    assert birthday_this_week(value, today) == expected
    assert week_dates(today)[0].weekday() == 0
    assert week_dates(today)[-1].weekday() == 6


@pytest.fixture
def display(db_session, monkeypatch):
    blueprint = importlib.import_module('application.blueprints.birthdays_blueprint')
    monkeypatch.setattr(blueprint, 'school_today', lambda: date(2026, 9, 9))
    object_type = ObjectType(name='Ученики', code='students', available_attributes=[
        {'code': 'photo', 'type': 'file'}, {'code': 'birthday', 'type': 'date'},
    ])
    db_session.add_all([object_type, BirthdayDisplay(id=1, key=KEY)])
    db_session.commit()
    return object_type


def add_student(db_session, object_type, name='Ученик', birthday='09.09.2010', **kwargs):
    obj = Object(name=name, type=object_type, attributes={
        'birthday': birthday, 'email': 'private@example.com', 'phone': 'private-phone',
    }, **kwargs)
    db_session.add(obj)
    db_session.commit()
    return obj


def headers(key=KEY):
    return {'X-Birthday-Key': key}


@pytest.mark.parametrize('role,expected', [('admin', 200), ('teacher', 403), ('student', 403)])
def test_settings_require_admin(client, db_session, role, expected):
    user = User(name='User', email=f'{role}@example.com', role=role)
    db_session.add(user)
    db_session.commit()
    auth = {'Authorization': f'Bearer {create_access_token(identity=str(user.id))}'}
    for method in ('get', 'post', 'delete'):
        assert getattr(client, method)(SETTINGS, headers=auth).status_code == expected


def test_settings_and_public_require_respective_credentials(client, display):
    for method in ('get', 'post', 'delete'):
        assert getattr(client, method)(SETTINGS).status_code == 401
    for path in (PUBLIC, f'{PUBLIC}/1/photo'):
        for supplied in ({}, headers('wrong-key'), headers('неверный-ключ')):
            response = client.get(path, headers=supplied)
            assert response.status_code == 403
            assert response.headers['Cache-Control'] == 'no-store'


def test_link_creation_persistence_rotation_and_disabling(client, db_session):
    admin = User(name='Admin', email='admin@example.com', role='admin')
    db_session.add(admin)
    db_session.commit()
    auth = {'Authorization': f'Bearer {create_access_token(identity=str(admin.id))}'}
    assert client.get(SETTINGS, headers=auth).json['enabled'] is False
    first = client.post(SETTINGS, headers=auth).json
    key = first['path'].split('#key=')[1]
    assert len(key) >= 43
    assert client.get(SETTINGS, headers=auth).json == first
    assert client.get(PUBLIC, headers=headers(key)).status_code == 200
    second = client.post(SETTINGS, headers=auth).json
    new_key = second['path'].split('#key=')[1]
    assert new_key != key
    assert client.get(PUBLIC, headers=headers(key)).status_code == 403
    assert client.get(PUBLIC, headers=headers(new_key)).status_code == 200
    assert client.delete(SETTINGS, headers=auth).json['enabled'] is False
    assert client.get(PUBLIC, headers=headers(new_key)).status_code == 403
    assert client.get(SETTINGS, headers=auth).json['path'] is None


def test_public_payload_is_limited_sorted_and_filters_students(client, db_session, display):
    add_student(db_session, display, 'Воскресенье', '13.09.2012')
    today = add_student(db_session, display, 'Сегодня')
    add_student(db_session, display, 'Понедельник', '07.09.2008')
    add_student(db_session, display, 'Следующая неделя', '14.09.2008')
    add_student(db_session, display, 'Удалён', deleted_at=datetime.now())
    add_student(db_session, display, 'Не подтверждён', is_approved=False)
    add_student(db_session, display, 'Нет даты', birthday=None)
    event_type = ObjectType(name='События', code='events')
    add_student(db_session, event_type, 'Не ученик')
    response = client.get(PUBLIC, headers=headers())
    assert response.status_code == 200
    assert response.headers['Cache-Control'] == 'no-store'
    assert response.headers['X-Robots-Tag'] == 'noindex, nofollow, noarchive'
    assert response.json['week_start'] == '2026-09-07'
    assert response.json['week_end'] == '2026-09-13'
    assert [obj['name'] for obj in response.json['students']] == ['Сегодня', 'Понедельник', 'Воскресенье']
    assert response.json['students'][0] == {
        'id': today.id, 'name': 'Сегодня', 'date': '2026-09-09', 'is_today': True, 'photo_path': None,
    }
    assert b'private' not in response.data
    assert b'2010' not in response.data
    assert KEY.encode() not in response.data


def test_empty_week(client, display):
    assert client.get(PUBLIC, headers=headers()).json['students'] == []


def test_only_current_eligible_photo_is_available(client, db_session, display, tmp_path, monkeypatch):
    blueprint = importlib.import_module('application.blueprints.birthdays_blueprint')
    monkeypatch.setattr(blueprint, 'UPLOAD_FOLDER', str(tmp_path))
    uploader = User(name='Admin', email='photo@example.com', role='admin')
    db_session.add(uploader)
    db_session.commit()
    old = UploadedFile(user_id=uploader.id, original_filename='old.jpg', stored_filename='old.jpg')
    new = UploadedFile(user_id=uploader.id, original_filename='new.jpg', stored_filename='new.jpg')
    db_session.add_all([old, new])
    db_session.commit()
    folder = tmp_path / f'folder_{new.id}'
    folder.mkdir()
    (folder / 'new.jpg').write_bytes(b'current-photo')
    student = add_student(db_session, display)
    student.attributes = {**student.attributes, 'photo': [
        f'/files/folder_{old.id}/old.jpg', f'/api/files/folder_{new.id}/new.jpg',
    ]}
    db_session.commit()
    path = f'{PUBLIC}/{student.id}/photo'
    response = client.get(path, headers=headers())
    assert response.status_code == 200
    assert response.data == b'current-photo'
    assert response.headers['Content-Type'].startswith('image/jpeg')
    assert response.headers['Cache-Control'] == 'no-store'
    assert client.get(path).status_code == 403
    assert client.get(f'/api/files/folder_{old.id}/old.jpg', headers=headers()).status_code == 401

    for changes in ({'birthday': '14.09.2010'}, {'photo': '/files/folder_1/secret.pdf'},
                    {'photo': '/files/folder_1/../../secret.jpg'}):
        student.attributes = {'birthday': '09.09.2010', 'photo': f'/files/folder_{new.id}/new.jpg', **changes}
        db_session.commit()
        assert client.get(path, headers=headers()).status_code == 404

    student.attributes = {'birthday': '09.09.2010', 'photo': f'/files/folder_{new.id}/new.jpg'}
    for flag in ('is_private', 'is_secret', 'is_hidden'):
        display.available_attributes = [{'code': 'photo', 'type': 'file', flag: True}]
        db_session.commit()
        assert client.get(path, headers=headers()).status_code == 404
        assert client.get(PUBLIC, headers=headers()).json['students'][0]['photo_path'] is None

    display.available_attributes = [{'code': 'photo', 'type': 'file'}]
    student.deleted_at = datetime.now()
    db_session.commit()
    assert client.get(path, headers=headers()).status_code == 404


def test_school_timezone(app, monkeypatch):
    methods = importlib.import_module('application.methods.birthday_methods')
    class FixedDatetime(datetime):
        @classmethod
        def now(cls, tz):
            from datetime import timezone
            return datetime(2026, 9, 13, 22, tzinfo=timezone.utc).astimezone(tz)
    monkeypatch.setattr(methods, 'datetime', FixedDatetime)
    app.config['SCHOOL_TIMEZONE'] = 'Europe/Moscow'
    assert methods.school_today() == date(2026, 9, 14)
    app.config['SCHOOL_TIMEZONE'] = 'UTC'
    assert methods.school_today() == date(2026, 9, 13)
