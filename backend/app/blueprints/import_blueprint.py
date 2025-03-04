# файлик с Blueprint (пример)
import os
from flask import Blueprint, request, jsonify, send_from_directory
from app.helpers.decorators import requires_user
from app.methods import upload_new_file
from app.constants import UPLOAD_FOLDER
from app.methods.import_methods import import_data

import_blueprint = Blueprint('import', __name__, url_prefix='/import')


@import_blueprint.route('/objects', methods=['POST'])
@requires_user
def import_endpoint(user):
    import_data(user, request.files.get('file'))

    return jsonify({"result": "ok"}), 200
