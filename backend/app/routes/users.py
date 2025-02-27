from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from app.models.user import User, Role
from app.database import db

users_blueprint = Blueprint('users', __name__)


