from flask import Blueprint, request, jsonify
from app.methods import register_user, login_user
from app.presenters.presenters import present_user
from app.helpers.decorators import validate_request_with, requires_user
from app.validators import *

auth_blueprint = Blueprint('auth', __name__)


@auth_blueprint.route('/signup', methods=['POST'])
@validate_request_with(validate_signup)
def signup(user_description):
    user = register_user(user_description)
    return present_user(user), 201


@auth_blueprint.route('/login', methods=['POST'])
@validate_request_with(validate_login)
def login(credentials):
    token = login_user(credentials)

    return jsonify({
        "access_token": token
    }), 200


@auth_blueprint.route('/me', methods=['GET'])
@requires_user
def profile(user):
    return present_user(user)
