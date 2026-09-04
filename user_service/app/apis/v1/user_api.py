from flask import current_app, g
from flask.views import MethodView
from sqlalchemy import text

from app.blueprints.user_blueprints import blp
from app.extensions.rate_limiter import get_login_email_key, limiter
from app.extensions.redis_connection import redis_client
from app.main import db
from app.schemas.custom_response import CustomResponse
from app.schemas.user_schemas import (
    CreateUserSchema,
    PaginationSchema,
    UserListResponseSchema,
    UserLoginSchema,
)
from app.services.session_service import revoke_all_sessions, revoke_single_session
from app.services.user_service import UserContext
from app.utils.users import (
    attach_refresh_cookie,
    clear_refresh_cookie,
    decode_refresh_token_jti,
    generate_new_access_token,
    generate_tokens,
    login_required,
    validate_user_data,
)


@blp.route("/healthz", methods=["GET"])
class HealthCheck(MethodView):
    @limiter.exempt
    def get(self):
        return {"status": "ok"}, 200


@blp.route("/readyz", methods=["GET"])
class ReadinessCheck(MethodView):
    @limiter.exempt
    def get(self):
        checks = {}

        try:
            db.session.execute(text("SELECT 1"))
            checks["database"] = "ok"
        except Exception:
            current_app.logger.exception("DB readiness check failed")
            checks["database"] = "failed"

        try:
            redis_client.ping()
            checks["redis"] = "ok"
        except Exception:
            current_app.logger.exception("Redis readiness check failed")
            checks["redis"] = "failed"

        # add more dependencies here the same way

        if all(v == "ok" for v in checks.values()):
            return {"status": "ready", "checks": checks}, 200

        return {"status": "not_ready", "checks": checks}, 503


@blp.route("/list", methods=["GET"])
class GetUserList(MethodView):
    @login_required(staff_only=True)
    @blp.arguments(PaginationSchema, location="query")
    @blp.response(200, UserListResponseSchema)
    def get(self, args):
        """Get user list"""
        users = UserContext().get_users(
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
class Registration(MethodView):
    @limiter.limit("10 per minute")
    @blp.arguments(CreateUserSchema)
    def post(self, data):
        """Register a new user"""

        validation_result = validate_user_data(data)
        if validation_result is not None:
            return validation_result

        new_user_id = UserContext().create_user(
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
        self.user_service = user_service or UserContext()

    @limiter.limit("10 per minute")
    @limiter.limit("10 per 15 minutes", key_func=get_login_email_key)
    @blp.arguments(UserLoginSchema)
    def post(self, auth):
        email = auth["email"]
        password = auth["password"]

        user = self.user_service.check_user_existance(email=email)

        if not user or not self.user_service.check_user_password_status(password):
            return CustomResponse.error(
                code="invalid_credentials",
                message="Invalid email or password.",
                status_code=401,
            )

        result = generate_tokens(user)
        resp = CustomResponse.success(data={"access_token": result["access_token"]})
        return attach_refresh_cookie(resp, result["refresh_token"])


@blp.route("/refresh", methods=["POST"])
class RefreshToken(MethodView):
    @limiter.limit("10 per minute")
    def post(self):
        """Refresh access token using refresh token"""
        result = generate_new_access_token()
        resp = CustomResponse.success(data={"access_token": result["access_token"]})
        return attach_refresh_cookie(resp, result["refresh_token"])


@blp.route("/logout", methods=["POST"])
class Logout(MethodView):
    @limiter.limit("10 per minute")
    @login_required()
    def post(self):
        """Logout user by revoking this device's refresh token"""
        jti = decode_refresh_token_jti()
        revoke_single_session(g.user_id, jti)
        resp = CustomResponse.success(message="Logged out successfully")
        return clear_refresh_cookie(resp)


@blp.route("/logout/all", methods=["POST"])
class LogoutAll(MethodView):
    @limiter.limit("10 per minute")
    @login_required()
    def post(self):
        """Logout user from all devices by revoking all refresh tokens"""
        revoke_all_sessions(g.user_id)
        resp = CustomResponse.success(message="Logged out from all devices successfully")
        return clear_refresh_cookie(resp)
