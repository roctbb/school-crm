import secrets
import time

from flask import Blueprint, current_app, request, jsonify
from flask_jwt_extended import decode_token, get_jwt, get_jwt_identity, jwt_required

from application.emails import send_password_reset_email
from application.methods import register_user, login_user, get_user_by_email, get_user_by_reset_token, reset_password, \
    set_reset_token, change_password, create_login_session, rotate_login_session, revoke_login_session
from application.presenters.presenters import present_user
from application.helpers.decorators import *
from application.helpers.rate_limit import (
    email_rate_limit_key,
    invite_rate_limit_key,
    is_unauthorized_response,
    reset_token_rate_limit_key,
)
from application.validators import *
from application.infrastructure import limiter

auth_blueprint = Blueprint('auth', __name__)


def _set_refresh_cookies(response, refresh_token, claims, persistent):
    cookie_options = {
        'secure': request.is_secure,
        'samesite': 'Lax',
    }
    if persistent:
        cookie_options['max_age'] = max(0, int(claims['exp']) - int(time.time()))
    response.set_cookie(
        current_app.config['JWT_REFRESH_COOKIE_NAME'],
        refresh_token,
        httponly=True,
        path='/api',
        **cookie_options,
    )
    response.set_cookie(
        current_app.config['JWT_REFRESH_CSRF_COOKIE_NAME'],
        claims['csrf'],
        httponly=False,
        path='/',
        **cookie_options,
    )


def _clear_refresh_cookies(response):
    response.delete_cookie(
        current_app.config['JWT_REFRESH_COOKIE_NAME'],
        path='/api',
        secure=request.is_secure,
        samesite='Lax',
    )
    response.delete_cookie(
        current_app.config['JWT_REFRESH_CSRF_COOKIE_NAME'],
        path='/',
        secure=request.is_secure,
        samesite='Lax',
    )


def _revoke_refresh_cookie_if_valid(csrf_token=None):
    refresh_token = request.cookies.get(current_app.config['JWT_REFRESH_COOKIE_NAME'])
    if not refresh_token:
        return False
    try:
        claims = decode_token(refresh_token, allow_expired=True)
    except Exception:
        return False
    if claims.get('type') != 'refresh' or not claims.get('jti'):
        return False
    if csrf_token is not None and not secrets.compare_digest(
            claims.get('csrf', ''), csrf_token):
        return False
    return revoke_login_session(claims['jti'], claims.get('sub'))


@auth_blueprint.route('/signup', methods=['POST'])
@limiter.limit(lambda: current_app.config['AUTH_SIGNUP_IP_RATE_LIMIT'])
@limiter.limit(
    lambda: current_app.config['AUTH_SIGNUP_INVITE_RATE_LIMIT'],
    key_func=invite_rate_limit_key,
)
@validate_request_with(validate_signup)
def signup(user_description):
    user = register_user(user_description)
    return present_user(user), 201


@auth_blueprint.route('/login', methods=['POST'])
@limiter.limit(
    lambda: current_app.config['AUTH_LOGIN_IP_RATE_LIMIT'],
    deduct_when=is_unauthorized_response,
)
@limiter.limit(
    lambda: current_app.config['AUTH_LOGIN_EMAIL_RATE_LIMIT'],
    key_func=email_rate_limit_key,
    deduct_when=is_unauthorized_response,
)
@validate_request_with(validate_login)
def login(credentials):
    user = login_user(credentials)
    _revoke_refresh_cookie_if_valid()
    session, refresh_token, refresh_claims = create_login_session(
        user, credentials.get('remember_me', False)
    )

    response = jsonify(session)
    _set_refresh_cookies(
        response,
        refresh_token,
        refresh_claims,
        credentials.get('remember_me', False),
    )
    return response, 200


@auth_blueprint.route('/refresh', methods=['POST'])
@jwt_required(refresh=True, locations=['cookies'])
def refresh_session_endpoint():
    refresh_claims = get_jwt()
    # Старые refresh-токены выдавались только постоянным сессиям и не
    # содержали этот claim, поэтому отсутствие значения означает True.
    persistent = bool(refresh_claims.get('persistent', True))
    session, refresh_token, refresh_claims = rotate_login_session(
        get_jwt_identity(),
        refresh_claims['jti'],
        persistent,
    )
    if not session:
        response = jsonify({
            'message': 'Сессия уже была обновлена или отозвана. Войдите снова.',
        })
        _clear_refresh_cookies(response)
        return response, 401

    response = jsonify(session)
    _set_refresh_cookies(response, refresh_token, refresh_claims, persistent)
    return response, 200


@auth_blueprint.route('/logout', methods=['POST'])
def logout_session_endpoint():
    refresh_token = request.cookies.get(current_app.config['JWT_REFRESH_COOKIE_NAME'])
    csrf_cookie = request.cookies.get(current_app.config['JWT_REFRESH_CSRF_COOKIE_NAME'])
    csrf_header = request.headers.get(current_app.config['JWT_REFRESH_CSRF_HEADER_NAME'])
    if refresh_token and csrf_cookie and csrf_header and secrets.compare_digest(csrf_cookie, csrf_header):
        _revoke_refresh_cookie_if_valid(csrf_header)

    response = jsonify({'result': 'ok'})
    _clear_refresh_cookies(response)
    return response, 200


@auth_blueprint.route('/me', methods=['GET'])
@requires_user
def profile(user):
    return present_user(user), 200


@auth_blueprint.route('/password/change', methods=['POST'])
@requires_user
@limiter.limit(
    lambda: current_app.config['AUTH_PASSWORD_CHANGE_RATE_LIMIT'],
    key_func=lambda: f'user:{get_jwt_identity()}',
)
@validate_request_with(validate_change_password_request)
def password_change_endpoint(validated_data, user):
    persistent = False
    refresh_token = request.cookies.get(current_app.config['JWT_REFRESH_COOKIE_NAME'])
    if refresh_token:
        try:
            refresh_claims = decode_token(refresh_token)
            persistent = (
                refresh_claims.get('type') == 'refresh'
                and refresh_claims.get('sub') == str(user.id)
                and bool(refresh_claims.get('persistent', True))
            )
        except Exception:
            persistent = False

    change_password(
        user,
        validated_data['current_password'],
        validated_data['new_password'],
    )
    session, refresh_token, refresh_claims = create_login_session(user, persistent)
    response = jsonify({**session, 'result': 'ok'})
    _set_refresh_cookies(response, refresh_token, refresh_claims, persistent)
    return response, 200


@auth_blueprint.route('/password/email', methods=['POST'])
@limiter.limit(lambda: current_app.config['AUTH_PASSWORD_EMAIL_IP_RATE_LIMIT'])
@limiter.limit(
    lambda: current_app.config['AUTH_PASSWORD_EMAIL_RATE_LIMIT'],
    key_func=email_rate_limit_key,
)
@validate_request_with(validate_reset_email_request)
def password_email_endpoint(validated_data):
    user = get_user_by_email(validated_data.get('email'))
    set_reset_token(user)
    send_password_reset_email(user)
    return jsonify({"result": "ok"}), 200


@auth_blueprint.route('/password/reset', methods=['POST'])
@limiter.limit(lambda: current_app.config['AUTH_PASSWORD_RESET_IP_RATE_LIMIT'])
@limiter.limit(
    lambda: current_app.config['AUTH_PASSWORD_RESET_TOKEN_RATE_LIMIT'],
    key_func=reset_token_rate_limit_key,
)
@validate_request_with(validate_reset_request)
def password_reset_endpoint(validate_data):
    user = get_user_by_reset_token(validate_data.get('reset_token'))
    user = reset_password(user, validate_data.get('password'))
    session, refresh_token, refresh_claims = create_login_session(user, False)
    response = jsonify(session)
    _set_refresh_cookies(response, refresh_token, refresh_claims, False)
    return response, 200
