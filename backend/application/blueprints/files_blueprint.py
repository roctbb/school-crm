import os
from flask import Blueprint, request, jsonify, send_from_directory, make_response
from application.helpers.decorators import requires_user
from application.helpers.exceptions import LogicException
from application.methods import upload_new_file, get_uploaded_file, can_get_uploaded_file
from application.constants import UPLOAD_FOLDER

files_blueprint = Blueprint('files', __name__, url_prefix='/files')


@files_blueprint.route('', methods=['POST'])
@requires_user
def upload_file(user):
    file = request.files.get('file')
    path = upload_new_file(
        user=user,
        file=file
    )
    return jsonify({"path": path}), 200


@files_blueprint.route('/<string:folder>/<path:filename>', methods=['GET'])
@requires_user
def get_file(user, folder, filename):
    uploaded_file = get_uploaded_file(folder, filename)
    if not can_get_uploaded_file(user, uploaded_file):
        raise LogicException("Доступ запрещен", 403)

    file_dir = os.path.join(UPLOAD_FOLDER, folder)
    response = make_response(
        send_from_directory(file_dir, filename, as_attachment=False)
    )
    response.headers["Cache-Control"] = "private, no-store"

    return response
