from flask import Blueprint, jsonify

from application.helpers import url
from application.helpers.decorators import requires_roles, requires_user
from application.methods import generate_user_reset_token, get_user_by_id, get_users
from application.presenters import present_admin_user


users_blueprint = Blueprint('users', __name__, url_prefix='/users')


@users_blueprint.route('', methods=['GET'])
@requires_user
@requires_roles(['admin'])
def users_endpoint(_current_user):
    return jsonify([present_admin_user(user) for user in get_users()]), 200


@users_blueprint.route('/<int:user_id>', methods=['GET'])
@requires_user
@requires_roles(['admin'])
def user_endpoint(_current_user, user_id):
    return jsonify(present_admin_user(get_user_by_id(user_id))), 200


@users_blueprint.route('/<int:user_id>/password-reset-link', methods=['POST'])
@requires_user
@requires_roles(['admin'])
def user_password_reset_link_endpoint(_current_user, user_id):
    user = generate_user_reset_token(get_user_by_id(user_id))
    reset_url = url(f'/password/reset?token={user.reset_token}')
    return jsonify({'reset_url': reset_url}), 200
