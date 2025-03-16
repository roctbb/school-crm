# файлик с Blueprint (пример)
import os
from flask import Blueprint, request, jsonify, send_from_directory
from app.helpers.decorators import requires_user, requires_roles
from app.methods import upload_new_file
from app.constants import UPLOAD_FOLDER
from app.methods.import_methods import import_objects, import_submissions

import_blueprint = Blueprint('import', __name__, url_prefix='/import')


@import_blueprint.route('/objects', methods=['POST'])
@requires_user
@requires_roles(['admin'])
def import_endpoint(user):
    import_objects(user, request.files.get('file'))

    return jsonify({"result": "ok"}), 200


@import_blueprint.route('/submissions', methods=['POST'])
@requires_user
@requires_roles(['admin'])
def import_submissions_endpoint(user):
    import_submissions(user, request.files.get('file'))

    return jsonify({"result": "ok"}), 200
