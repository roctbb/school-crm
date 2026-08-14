import os
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    APP_NAME = os.getenv('APP_NAME', 'Силаэдр CRM').strip() or 'Силаэдр CRM'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key')
    JWT_SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key')
    PORT = os.getenv('PORT', 8081)
    HOST = os.getenv('HOST', "0.0.0.0")
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    DEBUG_QUERIES = os.getenv('DEBUG_QUERIES', 'False').lower() == 'true'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=12)
    AUTH_REFRESH_TOKEN_EXPIRES_DAYS = int(os.getenv('AUTH_REFRESH_TOKEN_EXPIRES_DAYS', 30))
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=AUTH_REFRESH_TOKEN_EXPIRES_DAYS)
    JWT_TOKEN_LOCATION = ['headers', 'cookies']
    JWT_COOKIE_CSRF_PROTECT = True
    JWT_COOKIE_SAMESITE = 'Lax'
    JWT_REFRESH_COOKIE_NAME = 'crm_refresh_token'
    JWT_REFRESH_CSRF_COOKIE_NAME = 'crm_refresh_csrf'
    JWT_REFRESH_CSRF_HEADER_NAME = 'X-CSRF-TOKEN'
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
    TRUSTED_PROXY_COUNT = int(os.getenv('TRUSTED_PROXY_COUNT', 1))
    AUTH_LOGIN_IP_RATE_LIMIT = os.getenv('AUTH_LOGIN_IP_RATE_LIMIT', '2000 per hour')
    AUTH_LOGIN_EMAIL_RATE_LIMIT = os.getenv(
        'AUTH_LOGIN_EMAIL_RATE_LIMIT', '10 per minute; 50 per hour'
    )
    AUTH_SIGNUP_IP_RATE_LIMIT = os.getenv('AUTH_SIGNUP_IP_RATE_LIMIT', '1000 per hour')
    AUTH_SIGNUP_INVITE_RATE_LIMIT = os.getenv(
        'AUTH_SIGNUP_INVITE_RATE_LIMIT', '20 per hour'
    )
    AUTH_PASSWORD_EMAIL_IP_RATE_LIMIT = os.getenv(
        'AUTH_PASSWORD_EMAIL_IP_RATE_LIMIT', '500 per hour'
    )
    AUTH_PASSWORD_EMAIL_RATE_LIMIT = os.getenv(
        'AUTH_PASSWORD_EMAIL_RATE_LIMIT', '3 per hour'
    )
    AUTH_PASSWORD_RESET_IP_RATE_LIMIT = os.getenv(
        'AUTH_PASSWORD_RESET_IP_RATE_LIMIT', '500 per hour'
    )
    AUTH_PASSWORD_RESET_TOKEN_RATE_LIMIT = os.getenv(
        'AUTH_PASSWORD_RESET_TOKEN_RATE_LIMIT', '10 per hour'
    )
    MASTER_PASSWORD = os.getenv('MASTER_PASSWORD')
    EXTERNAL_URL = os.getenv('EXTERNAL_URL', '')
    BASE_URL = os.getenv('APP_URL', 'http://localhost:5173')
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '')
    OIDC_ISSUER = os.getenv('OIDC_ISSUER')
    OIDC_KEY_PATH = os.getenv(
        'OIDC_KEY_PATH',
        os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'storage', 'oidc_signing_key.pem')),
    )
    OIDC_AUTH_CODE_EXPIRES = int(os.getenv('OIDC_AUTH_CODE_EXPIRES', 300))
    OIDC_ACCESS_TOKEN_EXPIRES = int(os.getenv('OIDC_ACCESS_TOKEN_EXPIRES', 900))
    OIDC_ID_TOKEN_EXPIRES = int(os.getenv('OIDC_ID_TOKEN_EXPIRES', 900))
    OIDC_REFRESH_TOKEN_EXPIRES = int(os.getenv('OIDC_REFRESH_TOKEN_EXPIRES', 2592000))
    OAUTH2_TOKEN_EXPIRES_IN = {
        'authorization_code': OIDC_ACCESS_TOKEN_EXPIRES,
        'refresh_token': OIDC_ACCESS_TOKEN_EXPIRES,
    }
    OAUTH2_REFRESH_TOKEN_GENERATOR = True
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    TELEGRAM_BOT_USERNAME = os.getenv('TELEGRAM_BOT_USERNAME', '').lstrip('@')
    TELEGRAM_PROXY_URL = os.getenv('TELEGRAM_PROXY_URL')
    TELEGRAM_LINK_TOKEN_EXPIRES = int(os.getenv('TELEGRAM_LINK_TOKEN_EXPIRES', 600))
    TELEGRAM_POLL_TIMEOUT = int(os.getenv('TELEGRAM_POLL_TIMEOUT', 30))

class DevelopmentConfig(Config):
    """Development configuration"""
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'postgresql+psycopg2://dev_user:dev_password@localhost:5432/dev_db'
    )
    DEBUG = True
    BASE_URL = os.getenv('APP_URL', "http://localhost:5173")
    CORS_ORIGINS = os.getenv(
        'CORS_ORIGINS', 'http://localhost:5173,http://127.0.0.1:5173'
    )


class ProductionConfig(Config):
    """Production configuration"""
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    CELERY_BACKEND = os.getenv('CELERY_BACKEND', "redis://redis:6379/1")
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', "redis://redis:6379/0")
    RATELIMIT_STORAGE_URI = os.getenv('RATELIMIT_STORAGE_URI', 'redis://redis:6379/2')
    DEBUG = False
    BASE_URL = os.getenv('APP_URL', "https://lk.silaeder.ru")
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', BASE_URL)


class TestingConfig(Config):
    """Testing configuration"""
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'TEST_DATABASE_URL',
        'postgresql+psycopg2://test_user:test_password@localhost:5432/test_db'
    )
    DEBUG = True
    TESTING = True
    RATELIMIT_STORAGE_URI = 'memory://'
    OIDC_KEY_PATH = os.getenv('TEST_OIDC_KEY_PATH', '/tmp/school_crm_test_oidc_signing_key.pem')
    TELEGRAM_BOT_USERNAME = os.getenv('TEST_TELEGRAM_BOT_USERNAME', 'school_crm_test_bot')


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
