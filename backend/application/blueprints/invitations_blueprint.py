from flask import Blueprint, jsonify
from application.helpers.decorators import requires_user, requires_roles, validate_request_with
from application.methods import (
    create_invitations_for,
    delete_all_unused_invitations,
    delete_invitation,
    get_invitations,
    get_unused_invitation_by_id,
)
from application.presenters.presenters import present_invitation
from application.validators import validate_invitations_request

invitations_blueprint = Blueprint('invitations', __name__, url_prefix='/invitations')


@invitations_blueprint.route('', methods=['GET'])
@requires_user
@requires_roles(['admin'])
def get_invitations_endpoint(user):
    return jsonify([present_invitation(invite) for invite in get_invitations()]), 200


@invitations_blueprint.route('/<int:invitation_id>', methods=['DELETE'])
@requires_user
@requires_roles(['admin'])
def delete_invitation_endpoint(user, invitation_id):
    invitation = get_unused_invitation_by_id(invitation_id)
    delete_invitation(user, invitation)
    return jsonify({'deleted': True, 'id': invitation_id}), 200


@invitations_blueprint.route('', methods=['DELETE'])
@requires_user
@requires_roles(['admin'])
def delete_all_invitations_endpoint(user):
    deleted_count = delete_all_unused_invitations(user)
    return jsonify({'deleted': True, 'count': deleted_count}), 200


@invitations_blueprint.route('/<string:type_code>/create', methods=['POST'])
@requires_user
@requires_roles(['admin'])
@validate_request_with(validate_invitations_request)
def create_invitations_endpoint(validated_data, user, type_code):
    return jsonify(
        [present_invitation(invite) for invite in create_invitations_for(type_code, validated_data.get('role'))]), 200
