from datetime import datetime, timezone
import pytest
from sqlalchemy.exc import IntegrityError

from application.infrastructure import celery
from application.models import Notification, Object, ObjectType, TelegramConnection, User
from application.tasks import birthdays
from application.tasks.notifications import send_notification_email, send_notification_telegram
from .fixtures import app, db_session


@pytest.fixture
def birthday_setup(app, db_session, monkeypatch):
    app.config['BASE_URL'] = 'https://school.example.test/'
    monkeypatch.setattr(birthdays, 'school_now', lambda: datetime(2026, 9, 22, 9))
    student_type = ObjectType(name='Ученики', code='students')
    admins = [User(name=f'Админ {i}', email=f'admin{i}@example.test', role='admin')
              for i in range(2)]
    db_session.add_all([student_type, *admins])
    db_session.commit()
    dispatched = []
    monkeypatch.setattr(birthdays, 'enqueue_notification_delivery', dispatched.append)
    return student_type, admins, dispatched


def add_student(db_session, student_type, name='Именинник', birthday='22.09.2010', **kwargs):
    student = Object(type=student_type, name=name, attributes={'birthday': birthday}, **kwargs)
    db_session.add(student)
    db_session.commit()
    return student


def test_only_todays_approved_students_are_sent_to_all_admins(db_session, birthday_setup):
    student_type, admins, dispatched = birthday_setup
    first = add_student(db_session, student_type)
    second = add_student(db_session, student_type, 'Второй', '2011-09-22')
    for birthday in ('21.09.2010', '23.09.2010', '22.10.2010', None, '', 'bad', ['22.09.2010']):
        add_student(db_session, student_type, birthday=birthday)
    add_student(db_session, student_type, is_approved=False)
    add_student(db_session, student_type, deleted_at=datetime.now())
    add_student(db_session, ObjectType(name='Учителя', code='teachers'))
    db_session.add_all([User(email=f'{role}@example.test', role=role)
                        for role in ('student', 'teacher', 'user')])
    db_session.commit()

    birthdays.send_admin_birthday_notifications.run()

    notifications = Notification.query.all()
    assert len(dispatched) == len(notifications) == 4
    assert {item.user_id for item in notifications} == {admin.id for admin in admins}
    assert {item.url for item in notifications} == {
        f'https://school.example.test/students/{student.id}' for student in (first, second)
    }
    assert all(item.title == 'Сегодня день рождения!' for item in notifications)
    assert all('22.09' in item.message and '2010' not in item.message for item in notifications)
    assert all(item.source_client_id is None for item in notifications)


def test_repeated_checks_deliver_each_channel_once(app, db_session, birthday_setup, monkeypatch):
    student_type, admins, dispatched = birthday_setup
    add_student(db_session, student_type)
    db_session.add(TelegramConnection(user_id=admins[0].id, chat_id=1234))
    db_session.commit()
    emails, telegram_messages = [], []
    monkeypatch.setattr('application.tasks.notifications.mail.send', emails.append)
    monkeypatch.setattr('application.tasks.notifications.TelegramBotAPI.send_message',
                        lambda _bot, chat_id, text: telegram_messages.append((chat_id, text)))
    app.config['TELEGRAM_BOT_TOKEN'] = 'test-token'

    birthdays.send_admin_birthday_notifications.run()
    birthdays.send_admin_birthday_notifications.run()  # Delivery is still pending.
    assert Notification.query.count() == 2
    for notification_id in dispatched:
        send_notification_email.run(notification_id)
        send_notification_telegram.run(notification_id)
    assert len(emails) == 2
    assert len(telegram_messages) == 1
    dispatched.clear()
    birthdays.send_admin_birthday_notifications.run()
    assert dispatched == []


def test_broker_failure_is_recovered_without_creating_duplicates(db_session, birthday_setup, monkeypatch):
    student_type, admins, dispatched = birthday_setup
    add_student(db_session, student_type)

    def unavailable(_notification_id):
        raise ConnectionError('broker unavailable')

    monkeypatch.setattr(birthdays, 'enqueue_notification_delivery', unavailable)
    with pytest.raises(ConnectionError):
        birthdays.send_admin_birthday_notifications.run()
    first_id = Notification.query.one().id
    monkeypatch.setattr(birthdays, 'enqueue_notification_delivery', dispatched.append)
    birthdays.send_admin_birthday_notifications.run()
    assert first_id in dispatched
    assert len(dispatched) == Notification.query.count() == len(admins)


@pytest.mark.parametrize('now,birthday,expected', [
    (datetime(2026, 9, 22, 8, 59), '22.09.2010', 0),
    (datetime(2026, 9, 22, 9), '22.09.2010', 2),
    (datetime(2026, 9, 22, 23, 59), '22.09.2010', 2),
    (datetime(2026, 9, 23, 9), '22.09.2010', 0),
    (datetime(2024, 2, 29, 9), '29.02.2012', 2),
    (datetime(2026, 2, 28, 9), '29.02.2012', 0),
    (datetime(2026, 3, 1, 9), '29.02.2012', 0),
    (datetime(2027, 1, 1, 9), '01.01.2010', 2),
])
def test_local_time_and_calendar_boundaries(db_session, birthday_setup, monkeypatch, now, birthday, expected):
    student_type, _, dispatched = birthday_setup
    add_student(db_session, student_type, birthday=birthday)
    monkeypatch.setattr(birthdays, 'school_now', lambda: now)
    birthdays.send_admin_birthday_notifications.run()
    assert len(dispatched) == Notification.query.count() == expected


def test_next_year_and_new_student_are_not_suppressed(db_session, birthday_setup, monkeypatch):
    student_type, _, dispatched = birthday_setup
    add_student(db_session, student_type)
    birthdays.send_admin_birthday_notifications.run()
    for item in Notification.query.all():
        item.email_sent_at = datetime.now()
    db_session.commit()
    dispatched.clear()
    add_student(db_session, student_type, 'Добавлен днём')
    birthdays.send_admin_birthday_notifications.run()
    assert len(dispatched) == 2
    assert Notification.query.count() == 4
    monkeypatch.setattr(birthdays, 'school_now', lambda: datetime(2027, 9, 22, 9))
    birthdays.send_admin_birthday_notifications.run()
    assert Notification.query.count() == 8


def test_empty_day_creates_no_notifications(db_session, birthday_setup):
    birthdays.send_admin_birthday_notifications.run()
    assert Notification.query.count() == 0
    assert birthday_setup[2] == []


def test_system_key_is_unique_in_database(db_session, birthday_setup):
    student_type, admins, _ = birthday_setup
    student = add_student(db_session, student_type)
    today = datetime(2026, 9, 22).date()
    notification = birthdays._birthday_notification(admins[0], student, today)
    assert birthdays._birthday_notification(admins[0], student, today).id == notification.id
    db_session.add(Notification(
        user_id=admins[0].id, system_key=notification.system_key,
        source_name='Дни рождения', title='Duplicate', message='Duplicate', payload_hash='0' * 64,
    ))
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()
    assert Notification.query.count() == 1


def test_task_uses_school_timezone(app, db_session, birthday_setup, monkeypatch):
    student_type, _, dispatched = birthday_setup
    add_student(db_session, student_type, birthday='23.09.2010')
    from application.methods import birthday_methods

    class FixedDatetime(datetime):
        @classmethod
        def now(cls, tz):
            return datetime(2026, 9, 22, 23, tzinfo=timezone.utc).astimezone(tz)

    monkeypatch.setattr(birthday_methods, 'datetime', FixedDatetime)
    monkeypatch.setattr(birthdays, 'school_now', birthday_methods.school_now)
    app.config['SCHOOL_TIMEZONE'] = 'Asia/Vladivostok'
    birthdays.send_admin_birthday_notifications.run()
    assert len(dispatched) == 2


def test_periodic_task_is_registered(app):
    schedule = celery.conf.beat_schedule['admin-birthday-notifications']
    assert schedule['schedule'] == 300.0
    assert celery.tasks[schedule['task']].name == birthdays.send_admin_birthday_notifications.name
