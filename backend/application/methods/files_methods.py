import os
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
from application import db
from application.constants import ALLOWED_EXTENSIONS, UPLOAD_FOLDER
from application.helpers.decorators import transaction
from application.models import UploadedFile
from application.helpers.exceptions import LogicException
from flask import current_app


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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
