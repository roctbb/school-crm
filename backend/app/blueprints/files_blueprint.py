# файлик с Blueprint (пример)
import os
from flask import Blueprint, request, jsonify, send_from_directory
from app.helpers.decorators import requires_user
from app.methods import upload_new_file
from app.constants import UPLOAD_FOLDER

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
def get_file(folder, filename):
    file_dir = os.path.join(UPLOAD_FOLDER, folder)
    return send_from_directory(file_dir, filename, as_attachment=False)
