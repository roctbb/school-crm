from flask_limiter.util import get_remote_address
from application.mail_delivery import TimeoutMail
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_limiter import Limiter
from flask_jwt_extended import JWTManager
from celery import Celery

db = SQLAlchemy()
jwt = JWTManager()
bcrypt = Bcrypt()
mail = TimeoutMail()
celery = Celery(
    "school_crm_app",
    result_expires=600,
    include=["application.tasks"]  # Модуль с задачами
)
limiter = Limiter(get_remote_address)
