import re
from datetime import datetime, timedelta
from urllib.parse import unquote, urlsplit
from zoneinfo import ZoneInfo

from flask import current_app
from application.models import Object, ObjectType


def school_now():
    return datetime.now(ZoneInfo(current_app.config['SCHOOL_TIMEZONE']))


def school_today():
    return school_now().date()


def week_dates(today):
    monday = today - timedelta(days=today.weekday())
    return [monday + timedelta(days=offset) for offset in range(7)]


def birthday_this_week(value, today):
    if not isinstance(value, str):
        return None
    for date_format in ('%d.%m.%Y', '%Y-%m-%d'):
        try:
            birthday = datetime.strptime(value.strip(), date_format).date()
            break
        except ValueError:
            continue
    else:
        return None
    # Compare real calendar days, including weeks spanning two years.
    # February 29 is celebrated on its actual date in leap years.
    return next((day for day in week_dates(today)
                 if (day.month, day.day) == (birthday.month, birthday.day)), None)


def display_students():
    return Object.query.join(ObjectType, Object.type_id == ObjectType.id).filter(
        ObjectType.code == 'students',
        Object.deleted_at.is_(None),
        Object.is_approved.is_(True),
    )


def current_photo_reference(obj):
    definition = next((attribute for attribute in (obj.type.available_attributes or [])
                       if attribute.get('code') == 'photo' and attribute.get('type') == 'file'), None)
    if not definition or any(definition.get(flag) for flag in ('is_secret', 'is_hidden', 'is_private')):
        return None
    value = (obj.attributes or {}).get('photo')
    values = value if isinstance(value, list) else [value]
    candidate = next((item for item in reversed(values) if isinstance(item, str) and item.strip()), None)
    if not candidate:
        return None
    try:
        path = unquote(urlsplit(candidate).path)
    except ValueError:
        return None
    match = re.fullmatch(r'(?:/api)?/files/(folder_[1-9]\d*)/([^/\\]+\.(?:png|jpe?g|gif|webp))', path, re.I)
    return match.groups() if match else None
