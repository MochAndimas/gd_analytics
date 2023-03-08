"""Configuration database file"""

import os
from decouple import config


class Config(object):
    """
    sqlite database configuration
    """
    basedir = os.path.abspath(os.path.dirname(__file__))

    # Set up the app secret key
    SECRET_KEY = config('SECRET KEY', default='rcd32011')

    # DB_staging
    SQLALCHEMY_DATABASE_URI = 'mysql://goodDBU:DBgo0dDr3am3r3@34.101.185.240:3306/gdDB_live'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProductionConfig(Config):
    """
    Postgres database configurations
    """
    DEBUG = False

    # Security setup
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = 3600

    # Mysql database
    SQLALCHEMY_DATABASE_URI = '{}://{}:{}@{}:{}/{}'.format(
        config('DB_ENGINE', default='mysql'),
        config('DB_USERNAME', default='goodDBU'),
        config('DB_PASS', default='DBgo0dDr3am3r3'),
        config('DB_HOST', default='34.101.185.240'),
        config('DB_PORT', default=3306),
        config('DB_NAME', default='gdDB_live')
    )


class DebugConfig(Config):
    """
    Debug configuration
    """
    DEBUG = True


# load all needed configurations
config_dict = {
    'Production': ProductionConfig,
    'Debug': DebugConfig
}
