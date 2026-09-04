from flask import current_app
from werkzeug.exceptions import HTTPException

from app.schemas.custom_response import CustomResponse


def _error_code(error):
    return error.name.lower().replace(" ", "_")


def handle_http_exception(error: HTTPException):
    data = getattr(error, "data", {}) or {}
    errors = data.get("errors") or data.get("messages")
    message = data.get("message") or error.description
    code = "validation_error" if errors else _error_code(error)

    response = CustomResponse.error(
        code=code,
        message=message,
        status_code=error.code,
        errors=errors,
    )
    response.headers.extend(data.get("headers", {}))
    return response


def handle_validation_error(error):
    return CustomResponse.error(
        code="validation_error",
        message="Invalid request data.",
        status_code=422,
        errors=getattr(error, "messages", None),
    )


def handle_unexpected_error(error):
    current_app.logger.exception("Unhandled application exception")

    return CustomResponse.error(
        code="internal_server_error",
        message="An unexpected error occurred.",
        status_code=500,
    )


def handle_email_already_exists(error):
    return CustomResponse.error(
        code="email_already_exists",
        message="An account with this email already exists.",
        status_code=409,
    )


def handle_token_reuse(error):
    return CustomResponse.error(
        code="session_compromised",
        message="Your session was compromised. Please log in again.",
        status_code=401,
    )


def handle_invalid_token(error):
    return CustomResponse.error(
        code="invalid_token",
        message=str(error),
        status_code=401,
    )


def handle_unauthorized(error):
    return CustomResponse.error(
        code="unauthorized",
        message="You are not authorized to access this resource.",
        status_code=401,
    )

def handle_user_not_found(error):
    return CustomResponse.error(
        code="user_not_found",
        message="The requested user was not found.",
        status_code=401,
    )