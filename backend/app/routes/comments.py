from flask import Blueprint, jsonify, request

from app.decorators import validate_request
from app.presenters import present_comment
from app.validators import validate_comment

comments_blueprint = Blueprint('comments', __name__)
