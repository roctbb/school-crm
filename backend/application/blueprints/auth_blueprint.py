from flask import Blueprint, request, jsonify

from application.emails import send_password_reset_email
from application.methods import register_user, login_user, get_user_by_email, get_user_by_reset_token, reset_password, \
    get_access_token, set_reset_token
from application.presenters.presenters import present_user
from application.helpers.decorators import *
from application.validators import *
from application.infrastructure import limiter

auth_blueprint = Blueprint('auth', __name__)


@auth_blueprint.route('/signup', methods=['POST'])
@limiter.limit("3 per day")
@validate_request_with(validate_signup)
def signup(user_description):
    user = register_user(user_description)
    return present_user(user), 201


@auth_blueprint.route('/login', methods=['POST'])
@limiter.limit("30 per day")
@validate_request_with(validate_login)
def login(credentials):
    token = login_user(credentials)

    return jsonify({
        "access_token": token
    }), 200


@auth_blueprint.route('/me', methods=['GET'])
@requires_user
def profile(user):
    return present_user(user), 200


@auth_blueprint.route('/password/email', methods=['POST'])
@limiter.limit("30 per day")
@validate_request_with(validate_reset_email_request)
def password_email_endpoint(validated_data):
    user = get_user_by_email(validated_data.get('email'))
    set_reset_token(user)
    send_password_reset_email(user)
    return jsonify({"result": "ok"}), 200


@auth_blueprint.route('/password/reset', methods=['POST'])
@limiter.limit("3 per day")
@validate_request_with(validate_reset_request)
def password_reset_endpoint(validate_data):
    user = get_user_by_reset_token(validate_data.get('reset_token'))
    reset_password(user, validate_data.get('password'))
    return jsonify({"access_token": get_access_token(user)}), 200
