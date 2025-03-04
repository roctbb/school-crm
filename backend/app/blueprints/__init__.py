from flask import Blueprint
from .auth_blueprint import auth_blueprint
from .files_blueprint import files_blueprint
from .health_blueprint import *
from .objects_blueprint import *
from .forms_blueprint import *
from .import_blueprint import *

api_blueprint = Blueprint('api', __name__, url_prefix='/api')
api_blueprint.register_blueprint(auth_blueprint)
api_blueprint.register_blueprint(health_blueprint)
api_blueprint.register_blueprint(objects_blueprint)
api_blueprint.register_blueprint(files_blueprint)
api_blueprint.register_blueprint(forms_blueprint)
api_blueprint.register_blueprint(import_blueprint)
