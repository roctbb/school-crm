import os
import re
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
from application import db
from application.constants import ALLOWED_EXTENSIONS, UPLOAD_FOLDER
from application.helpers.decorators import transaction
from application.models import Object, UploadedFile
from application.methods.access_methods import can_get_object, has_teacher_access
from application.helpers.exceptions import LogicException


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_uploaded_file(folder, filename):
    match = re.fullmatch(r"folder_([1-9]\d*)", folder)
    if not match:
        raise LogicException("Файл не найден", 404)

    uploaded_file = db.session.get(UploadedFile, int(match.group(1)))
    if not uploaded_file or uploaded_file.stored_filename != filename:
        raise LogicException("Файл не найден", 404)

    return uploaded_file


def can_get_uploaded_file(user, uploaded_file):
    if uploaded_file.user_id == user.id or has_teacher_access(user):
        return True

    file_path = f"/files/folder_{uploaded_file.id}/{uploaded_file.stored_filename}"
    referenced_objects = Object.query.filter(
        Object.deleted_at.is_(None),
        db.cast(Object.attributes, db.Text).contains(file_path),
    ).all()
    for obj in referenced_objects:
        if not obj.is_approved or not can_get_object(user, obj):
            continue

        for attribute in obj.type.available_attributes or []:
            if attribute.get('type') != 'file':
                continue
            value = (obj.attributes or {}).get(attribute.get('code'))
            values = value if isinstance(value, list) else [value]
            is_referenced = any(
                isinstance(candidate, str) and candidate.split('?', 1)[0].endswith(file_path)
                for candidate in values
            )
            if not is_referenced:
                continue
            if attribute.get('is_secret') or attribute.get('is_hidden'):
                continue
            if attribute.get('is_private') and user not in obj.owners:
                continue
            return True

    return False


@transaction
def upload_new_file(user, file):
    if not file:
        raise LogicException("Нет файла в запросе", 400)

    if file.filename == '':
        raise LogicException("Файл не выбран", 400)

    if not allowed_file(file.filename):
        raise LogicException("Недопустимый формат файла", 400)

    original_filename = secure_filename(file.filename)

    new_uploaded_file = UploadedFile(
        user_id=user.id,
        original_filename=original_filename
    )
    db.session.add(new_uploaded_file)
    db.session.commit()

    folder_name = f"folder_{new_uploaded_file.id}"
    file_dir = os.path.join(UPLOAD_FOLDER, folder_name)
    os.makedirs(file_dir, exist_ok=True)

    stored_filename = original_filename

    filepath = os.path.join(file_dir, stored_filename)
    file.save(filepath)

    new_uploaded_file.stored_filename = stored_filename
    db.session.commit()

    return f"/files/{folder_name}/{stored_filename}"
