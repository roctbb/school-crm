# файлик с Blueprint (пример)
import os
from flask import Blueprint, request, jsonify, send_from_directory
from application.helpers.decorators import requires_user, requires_roles, validate_request_with
from application.methods import upload_new_file, get_invitations, create_invitations_for
from application.presenters.presenters import present_invitation
from application.validators import validate_invitations_request

invitations_blueprint = Blueprint('invitations', __name__, url_prefix='/invitations')


@invitations_blueprint.route('', methods=['GET'])
@requires_user
@requires_roles(['admin'])
def get_invitations_endpoint(user):
    return jsonify([present_invitation(invite) for invite in get_invitations()]), 200


@invitations_blueprint.route('/<string:type_code>/create', methods=['POST'])
@requires_user
@requires_roles(['admin'])
@validate_request_with(validate_invitations_request)
def create_invitations_endpoint(validated_data, user, type_code):
    return jsonify(
        [present_invitation(invite) for invite in create_invitations_for(type_code, validated_data.get('role'))]), 200
