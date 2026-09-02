from flask import current_app
from flask.views import MethodView
from sqlalchemy import text

from app.main import db
from app.blueprints.user_blueprints import blp
from app.interfaces.user_interface import BaseApiView
from app.schemas.custom_response import CustomResponse
from app.utils.users import generate_tokens, login_required, generate_new_access_token, validate_user_data
from app.services.user_service import UserService
from app.schemas.user_schemas import CreateUserSchema, PaginationSchema, UserListResponseSchema, UserLoginSchema


@blp.route("/healthz", methods=["GET"])
class HealthCheck(BaseApiView):

    def get(self):
        return {"status": "ok"}, 200


@blp.route("/readyz", methods=["GET"])
class ReadinessCheck(BaseApiView):

    def get(self):
        try:
            db.session.execute(text("SELECT 1"))
            return {"status": "ready"}, 200
        except Exception:
            current_app.logger.exception("Readiness check failed")
            return {"status": "not_ready"}, 503


@blp.route("/list", methods=["GET"])
class GetUserList(BaseApiView):

    @login_required(staff_only=True)
    @blp.arguments(PaginationSchema, location="query")
    @blp.response(200, UserListResponseSchema)
    def get(self, args):
        """Get user list"""
        users = UserService().get_users(
            page=args["page"],
            per_page=args["per_page"],
        )
        return {
            "data": users.items,
            "pagination": {
                "page": users.page,
                "per_page": users.per_page,
                "total": users.total,
                "pages": users.pages,
            },
        }


@blp.route("/registration", methods=["POST"])
class Registration(BaseApiView):

    @blp.arguments(CreateUserSchema)
    def post(self, data):
        """Register a new user"""

        validation_result = validate_user_data(data)
        if validation_result is not None:
            return validation_result

        new_user_id = UserService().create_user(
            data["first_name"], data["last_name"], data["email"], data["password"]
        )
        current_app.logger.info("User created")
        return CustomResponse.success(
            message="User created successfully",
            data={"user_id": new_user_id},
            status_code=201,
        )


@blp.route("/login", methods=["POST"])
class Login(MethodView):

    def __init__(self, user_service=None) -> None:
        self.user_service = user_service or UserService()

    @blp.arguments(UserLoginSchema)
    def post(self, auth):
        email = auth["email"]
        password = auth["password"]

        user = self.user_service.check_user_existance(email=email)

        if user is None or not self.user_service.check_user_password(user, password):
            return CustomResponse.error(
                code="invalid_credentials",
                message="Invalid email or password.",
                status_code=401,
            )

        result = generate_tokens(user)
        return CustomResponse.success(data=result)

@blp.route("/refresh", methods=["POST"])
class RefreshToken(MethodView):

    def post(self):
        """Refresh access token using refresh token"""

        result, status = generate_new_access_token()

        if status != 200:
            return CustomResponse.error(
                code="invalid_refresh_token",
                message="Invalid or expired refresh token.",
                status_code=401,
            )

        return CustomResponse.success(data=result)