from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

from app.decorators import validate_request
from app.presenters import present_forms, present_form

forms_blueprint = Blueprint('forms', __name__)
