import os
import secrets

from flask import Blueprint, current_app, jsonify, request, send_from_directory
from sqlalchemy.dialects.postgresql import insert

from application.constants import UPLOAD_FOLDER
from application.helpers.decorators import requires_roles, requires_user, transaction
from application.helpers.exceptions import LogicException
from application.infrastructure import db
from application.models import BirthdayDisplay, Object
from application.methods.birthday_methods import (
    birthday_this_week, current_photo_reference, display_students, school_today, week_dates,
)
from application.methods.files_methods import get_uploaded_file

birthdays_blueprint = Blueprint('birthdays', __name__)


@birthdays_blueprint.after_request
def private_response(response):
    response.headers['Cache-Control'] = 'no-store'
    response.headers['Referrer-Policy'] = 'no-referrer'
    response.headers['X-Robots-Tag'] = 'noindex, nofollow, noarchive'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response


def settings_payload():
    settings = db.session.get(BirthdayDisplay, 1)
    key = settings.key if settings else None
    return {'enabled': bool(key), 'path': f'/public/birthdays#key={key}' if key else None,
            'timezone': current_app.config['SCHOOL_TIMEZONE']}


@birthdays_blueprint.route('/settings/birthday-display', methods=['GET'])
@requires_user
@requires_roles(['admin'])
def get_settings(user):
    return jsonify(settings_payload())


@birthdays_blueprint.route('/settings/birthday-display', methods=['POST'])
@requires_user
@requires_roles(['admin'])
@transaction
def create_link(user):
    key = secrets.token_urlsafe(32)
    db.session.execute(insert(BirthdayDisplay).values(id=1, key=key).on_conflict_do_update(
        index_elements=['id'], set_={'key': key},
    ))
    db.session.expire_all()
    return jsonify(settings_payload())


@birthdays_blueprint.route('/settings/birthday-display', methods=['DELETE'])
@requires_user
@requires_roles(['admin'])
@transaction
def disable_link(user):
    db.session.query(BirthdayDisplay).filter_by(id=1).update({'key': None})
    return jsonify(settings_payload())


def require_display_key():
    supplied = request.headers.get('X-Birthday-Key', '')
    settings = db.session.get(BirthdayDisplay, 1)
    if not settings or not settings.key or not secrets.compare_digest(
        supplied.encode('utf-8'), settings.key.encode('utf-8')
    ):
        raise LogicException('Ссылка недействительна или отключена. Обратитесь к администратору.', 403)


@birthdays_blueprint.route('/public/birthdays', methods=['GET'])
def get_birthdays():
    require_display_key()
    today = school_today()
    days = week_dates(today)
    students = []
    for obj in display_students().all():
        birthday = birthday_this_week((obj.attributes or {}).get('birthday'), today)
        if birthday:
            students.append({
                'id': obj.id, 'name': obj.name, 'date': birthday.isoformat(),
                'is_today': birthday == today,
                'photo_path': f'/public/birthdays/{obj.id}/photo' if current_photo_reference(obj) else None,
            })
    students.sort(key=lambda item: (not item['is_today'], item['date'], item['name'], item['id']))
    return jsonify({'today': today.isoformat(), 'week_start': days[0].isoformat(),
                    'week_end': days[-1].isoformat(), 'timezone': current_app.config['SCHOOL_TIMEZONE'],
                    'students': students})


@birthdays_blueprint.route('/public/birthdays/<int:object_id>/photo', methods=['GET'])
def get_birthday_photo(object_id):
    require_display_key()
    obj = display_students().filter(Object.id == object_id).first()
    if not obj or not birthday_this_week((obj.attributes or {}).get('birthday'), school_today()):
        raise LogicException('Фотография не найдена', 404)
    reference = current_photo_reference(obj)
    if not reference:
        raise LogicException('Фотография не найдена', 404)
    folder, filename = reference
    uploaded_file = get_uploaded_file(folder, filename)
    return send_from_directory(os.path.join(UPLOAD_FOLDER, folder), uploaded_file.stored_filename)
