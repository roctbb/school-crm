from flask import current_app
from sqlalchemy.exc import IntegrityError

from application.infrastructure import celery, db
from application.methods.birthday_methods import birthday_this_week, display_students, school_now
from application.methods.notification_methods import notification_payload_hash
from application.models import Notification, Object, TelegramConnection, User
from application.tasks.notifications import enqueue_notification_delivery


def _birthday_notification(admin, student, today):
    # Include the year so the same student is announced again next year.
    system_key = f'birthday:{today.isoformat()}:{student.id}:{admin.id}'
    existing = Notification.query.filter_by(system_key=system_key).first()
    if existing:
        return existing

    title = 'Сегодня день рождения!'
    message = f'Сегодня, {today:%d.%m}, день рождения у ученика: {student.name}.'
    url = f'{current_app.config["BASE_URL"].rstrip("/")}/students/{student.id}'
    notification = Notification(
        user_id=admin.id,
        system_key=system_key,
        source_name='Дни рождения',
        title=title,
        message=message,
        url=url,
        payload_hash=notification_payload_hash(str(admin.id), title, message, url),
    )
    db.session.add(notification)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        # Another worker may have created the same notification concurrently.
        existing = Notification.query.filter_by(system_key=system_key).first()
        if existing is None:
            raise
        return existing
    return notification


@celery.task
def send_admin_birthday_notifications():
    now = school_now()
    if now.hour < 9:
        return
    today = now.date()
    students = [student for student in display_students().order_by(Object.id).all()
                if birthday_this_week((student.attributes or {}).get('birthday'), today) == today]
    if not students:
        return

    admins = User.query.filter_by(role='admin').all()
    telegram_users = {user_id for (user_id,) in db.session.query(TelegramConnection.user_id).all()}
    for admin in admins:
        for student in students:
            notification = _birthday_notification(admin, student, today)
            if (not notification.email_sent_at
                    or (admin.id in telegram_users and not notification.telegram_sent_at)):
                # Requeue unfinished deliveries, including a previous broker failure.
                # Delivery tasks lock the row and skip channels already sent.
                enqueue_notification_delivery(notification.id)
