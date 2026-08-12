import hashlib
import hmac

from flask import current_app, request
from flask_limiter.util import get_remote_address


def _request_field_key(field, normalize=False):
    data = request.get_json(silent=True)
    value = data.get(field) if isinstance(data, dict) else None
    if not isinstance(value, str) or not value.strip():
        return f'ip:{get_remote_address()}'

    value = value.strip()
    if normalize:
        value = value.casefold()
    secret = str(current_app.config['SECRET_KEY']).encode('utf-8')
    digest = hmac.new(secret, value.encode('utf-8'), hashlib.sha256).hexdigest()
    return f'{field}:{digest}'


def email_rate_limit_key():
    return _request_field_key('email', normalize=True)


def invite_rate_limit_key():
    return _request_field_key('invite')


def reset_token_rate_limit_key():
    return _request_field_key('reset_token')


def is_unauthorized_response(response):
    """Count failed logins without charging successful school-wide login bursts."""
    return response.status_code == 401
