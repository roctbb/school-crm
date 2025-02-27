from flask import Blueprint
from .auth_blueprint import auth_blueprint
from .health_blueprint import *

api_blueprint = Blueprint('api', __name__, url_prefix='/api')
api_blueprint.register_blueprint(auth_blueprint)
api_blueprint.register_blueprint(health_blueprint)