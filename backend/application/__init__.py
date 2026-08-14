from flask import Flask, jsonify
from flask_limiter import Limiter
from flask_mail import Mail
from flask_migrate import Migrate
from werkzeug.exceptions import HTTPException

from application.helpers.error_handlers import setup_handlers
from application.infrastructure import db, jwt, bcrypt, mail, limiter, celery
from application.models import *
from application.config import get_config
from application.helpers.exceptions import LogicException
from application.blueprints import api_blueprint
from application.blueprints.oidc_blueprint import oidc_public_blueprint
from application.oidc import init_oidc
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix


def create_app(config_name=None):
    app = Flask(__name__)

    # Загрузка конфигурации из config.py
    app.config.from_object(get_config(config_name))
    # Backend доступен только через доверенные reverse proxy. Помимо внешней
    # HTTPS-схемы восстанавливаем адрес клиента для аварийных IP-лимитов.
    app.wsgi_app = ProxyFix(
        app.wsgi_app,
        x_for=app.config['TRUSTED_PROXY_COUNT'],
        x_proto=1,
    )
    if not app.config.get('OIDC_ISSUER'):
        app.config['OIDC_ISSUER'] = app.config['BASE_URL'].rstrip('/')

    if app.config['DEBUG_QUERIES']:
        import logging

        logging.basicConfig()
        logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

    setup_handlers(app)
    jwt.init_app(app)

    @jwt.expired_token_loader
    def expired_token_callback(_jwt_header, _jwt_payload):
        return jsonify({'message': 'Срок действия сессии истёк. Войдите снова.'}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(_reason):
        return jsonify({'message': 'Сессия недействительна. Войдите снова.'}), 401

    @jwt.unauthorized_loader
    def missing_token_callback(_reason):
        return jsonify({'message': 'Требуется вход в систему.'}), 401

    bcrypt.init_app(app)

    # Инициализация базы данных и инструментов миграции
    db.init_app(app)
    Migrate(app, db)
    init_oidc(app)

    # Настройка CORS
    cors_origins = [
        origin.strip()
        for origin in (app.config.get('CORS_ORIGINS') or app.config['BASE_URL']).split(',')
        if origin.strip()
    ]
    CORS(app, origins=cors_origins, supports_credentials=True)

    app.register_blueprint(api_blueprint)
    app.register_blueprint(oidc_public_blueprint)
    mail.init_app(app)

    celery.conf.update(app.config)
    celery.conf.broker_url = app.config['CELERY_BROKER_URL']
    celery.conf.result_backend = app.config['CELERY_BACKEND']

    limiter.init_app(app)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask

    return app, celery
