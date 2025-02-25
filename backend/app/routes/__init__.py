from flask import Blueprint
from app.routes.auth import auth_blueprint
from app.routes.users import users_blueprint
from app.routes.forms import forms_blueprint
from app.routes.entities import entities_blueprint
from app.routes.comments import comments_blueprint
from app.routes.groups import groups_blueprint
from app.routes.events import events_blueprint
from app.routes.health import health_blueprint

# Основной Blueprint API
api = Blueprint('api', __name__)

# Регистрация маршрутов
api.register_blueprint(auth_blueprint, url_prefix='/auth')
api.register_blueprint(users_blueprint, url_prefix='/users')
api.register_blueprint(forms_blueprint, url_prefix='/forms')
api.register_blueprint(entities_blueprint, url_prefix='/entities')
api.register_blueprint(comments_blueprint, url_prefix='/comments')
api.register_blueprint(groups_blueprint, url_prefix='/groups')
api.register_blueprint(events_blueprint, url_prefix='/events')
api.register_blueprint(health_blueprint, url_prefix='/status')
