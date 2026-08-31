from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_smorest import Api
from marshmallow import ValidationError
from werkzeug.exceptions import HTTPException

from app.errors.handlers import (
    handle_email_already_exists,
    handle_http_exception,
    handle_unexpected_error,
    handle_validation_error,
)
from config.config import app_config
from app.errors.exceptions import EmailAlreadyExistsError


db = SQLAlchemy()
migrate = Migrate()


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object(app_config)
    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    migrate.init_app(app, db)

    api = Api(app)
    app.register_error_handler(HTTPException, handle_http_exception)
    app.register_error_handler(ValidationError, handle_validation_error)
    app.register_error_handler(EmailAlreadyExistsError, handle_email_already_exists)
    app.register_error_handler(Exception, handle_unexpected_error)

    from .blueprints.user_blueprints import register_routes

    register_routes(api)

    return app
