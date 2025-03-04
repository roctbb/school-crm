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

class DevelopmentConfig(Config):
    """Development configuration"""
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'postgresql+psycopg2://dev_user:dev_password@localhost:5432/dev_db'
    )
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration"""
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    DEBUG = False


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
