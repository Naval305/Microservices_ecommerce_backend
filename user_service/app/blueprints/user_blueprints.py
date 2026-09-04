from flask_smorest import Api, Blueprint

blp = Blueprint("users", __name__, url_prefix="/api/users", description="User Operations")
from app.apis.v1.user_api import *


def register_routes(api: Api) -> None:
    api.register_blueprint(blp)
