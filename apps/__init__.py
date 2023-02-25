from importlib import import_module
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect


# csrf protecion module
csrf = CSRFProtect()

# database module
db = SQLAlchemy()

# login manager module
login_manager = LoginManager()
login_manager.login_view = 'authentication_blueprint.signin_page'
login_manager.login_message_category = 'info'

# password hashing module
bcrypt = Bcrypt()


def register_extension(app):
    """
    Function to register app extension
    """
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    csrf.init_app(app)


def register_blueprints(app):
    """
    Function to register blueprint
    """
    folder_name = ['authentication', 'dashboard']
    for module_name in folder_name:
        module = import_module('apps.{}.routes'.format(module_name))
        app.register_blueprint(module.blueprint)


def configure_database(app):
    """
    Function to configure database
    """
    @app.before_first_request
    def initialize_database():
        db.create_all()

    @app.teardown_request
    def shutdown_session(exception=None):
        db.session.remove()


def create_app(config):
    """
    Function to create app
    """
    app = Flask(__name__)
    app.config.from_object(config)
    register_extension(app)
    register_blueprints(app)
    configure_database(app)

    return app
