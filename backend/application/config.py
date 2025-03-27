import os
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key')
    JWT_SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key')
    PORT = os.getenv('PORT', 8081)
    HOST = os.getenv('HOST', "0.0.0.0")
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    DEBUG_QUERIES = os.getenv('DEBUG_QUERIES', 'False').lower() == 'true'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=12)
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.mailtrap.io')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 2525))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True').lower() in ('true', '1')
    MAIL_USE_SSL = os.getenv('MAIL_USE_SSL', 'False').lower() in ('true', '1')
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@lk.silaeder.ru')
    CELERY_BACKEND = os.getenv('CELERY_BACKEND', "redis://localhost:6379/1")
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', "redis://localhost:6379/0")
    RATELIMIT_STORAGE_URI = os.getenv('RATELIMIT_STORAGE_URI', 'redis://localhost:6379/2')

class DevelopmentConfig(Config):
    """Development configuration"""
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'postgresql+psycopg2://dev_user:dev_password@localhost:5432/dev_db'
    )
    DEBUG = True
    BASE_URL = os.getenv('APP_URL', "http://localhost:5173")


class ProductionConfig(Config):
    """Production configuration"""
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    CELERY_BACKEND = os.getenv('CELERY_BACKEND', "redis://redis:6379/1")
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', "redis://redis:6379/0")
    RATELIMIT_STORAGE_URI = os.getenv('RATELIMIT_STORAGE_URI', 'redis://redis:6379/2')
    DEBUG = False
    BASE_URL = os.getenv('APP_URL', "https://lk.silaeder.ru")


class TestingConfig(Config):
    """Testing configuration"""
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'TEST_DATABASE_URL',
        'postgresql+psycopg2://test_user:test_password@localhost:5432/test_db'
    )
    DEBUG = True
    TESTING = True


# Выбор конфигурации на основе переменной окружения
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(config_name=None):
    """Возвращает текущую конфигурацию"""
    config_name = config_name or os.getenv('FLASK_ENV', 'default')
    return config.get(config_name, DevelopmentConfig)
