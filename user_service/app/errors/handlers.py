from flask import current_app

from app.schemas.custom_response import CustomResponse


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