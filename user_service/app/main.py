from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_smorest import Api

from app.errors.handlers import handle_email_already_exists, handle_unexpected_error
from config.config import app_config
from app.errors.exceptions import EmailAlreadyExistsError


db = SQLAlchemy()
migrate = Migrate()


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object(app_config)
    app.register_error_handler(Exception, handle_unexpected_error)
    app.register_error_handler(
        EmailAlreadyExistsError,
        handle_email_already_exists,
    )

    db.init_app(app)
    migrate.init_app(app, db)

    api = Api(app)

    from .blueprints.user_blueprints import register_routes

    register_routes(api)

    return app
