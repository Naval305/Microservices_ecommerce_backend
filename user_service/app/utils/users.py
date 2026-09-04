from collections.abc import Callable, Mapping
from datetime import UTC, datetime, timedelta
from functools import wraps
from typing import Any, ParamSpec, TypeVar
from uuid import uuid4

import jwt
from flask import Response, current_app, g, request

from app.errors.exceptions import (
    EmailAlreadyExistsError,
    InvalidTokenError,
    UnauthorizedError,
    UserNotFoundError,
)
from app.services.session_service import rotate_refresh_token
from app.services.user_service import User, UserContext
from app.services.user_status_service import get_cached_user_active_status, set_user_active_status

P = ParamSpec("P")
R = TypeVar("R")


def validate_user_data(data: Mapping[str, Any]) -> None:
    if UserContext().check_user_existance(data["email"]):
        raise EmailAlreadyExistsError()


def get_auth_header() -> None | str:
    auth_header: str = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None
    return auth_header.split(" ")[-1]


def generate_access_token(user: User) -> str:
    now: datetime = datetime.now(UTC)
    payload: dict[str, Any] = {
        "sub": str(user.id),
        "email": user.email,
        "type": "access",
        "iss": "user-service",
        "aud": "ecommerce-services",
        "iat": now,
        "nbf": now,
        "exp": now + timedelta(minutes=15),
    }
    return jwt.encode(payload, current_app.config["PRIVATE_KEY"], algorithm="RS256")


def generate_refresh_token(
    user: User, old_refresh_token_info: Mapping[str, Any] | None = None
) -> str:
    now: datetime = datetime.now(UTC)
    payload: dict[str, Any] = {
        "sub": str(user.id),
        "type": "refresh",
        "jti": str(uuid4()),  # unique id — lets you revoke this one token later
        "iss": "user-service",
        "aud": "ecommerce-services",
        "iat": now,
        "nbf": now,
        "exp": now + timedelta(days=7),
    }
    token: str = jwt.encode(payload, current_app.config["REFRESH_SECRET_KEY"], algorithm="HS256")
    rotate_refresh_token(user, payload, old_refresh_token_info)
    return token


def generate_tokens(user: User) -> dict[str, str]:
    return {
        "access_token": generate_access_token(user),
        "refresh_token": generate_refresh_token(user),
    }


def authenticate(refresh_token: bool = False) -> dict[str, Any]:
    if refresh_token:
        token: str | None = request.cookies.get("refresh_token")
    else:
        token: str | None = get_auth_header()

    if not token:
        raise InvalidTokenError("Missing or malformed token")

    if refresh_token:
        key: str = current_app.config["REFRESH_SECRET_KEY"]
        algo: list[str] = ["HS256"]
        token_type = "refresh"
    else:
        key: str = current_app.config["PUBLIC_KEY"]
        algo: list[str] = ["RS256"]
        token_type = "access"

    try:
        payload: dict[str, str] = jwt.decode(
            token,
            key,
            algorithms=algo,
            issuer="user-service",
            audience="ecommerce-services",
        )
    except jwt.ExpiredSignatureError:
        raise InvalidTokenError("Token has expired") from None
    except jwt.InvalidTokenError:
        raise InvalidTokenError("Invalid token") from None

    if payload.get("type") != token_type:
        raise InvalidTokenError("Invalid token type")

    return payload


def is_user_active(user_id: int | str) -> bool:
    cached: None | bool = get_cached_user_active_status(user_id)
    if cached is not None:
        return cached
    user: User | None = UserContext(user_id).user
    if not user:
        raise UserNotFoundError()
    set_user_active_status(user_id, user.is_active)
    return user.is_active


def login_required(staff_only: bool = False) -> Callable[[Callable[P, R]], Callable[P, R]]:
    def decorator(f: Callable[P, R]) -> Callable[P, R]:
        @wraps(f)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            payload: dict[str, Any] = authenticate()

            if not is_user_active(payload["sub"]):
                raise UnauthorizedError("Account is deactivated")

            g.user_id = payload["sub"]
            g.user_email = payload["email"]

            if staff_only:
                user: User | None = UserContext(g.user_id).user
                if not user.is_staff:
                    raise UnauthorizedError("Unauthorized: Staff access required")

            return f(*args, **kwargs)

        return wrapper

    return decorator


def generate_new_access_token() -> dict[str, str]:
    payload: dict[str, str] = authenticate(refresh_token=True)  # raises on failure

    user: User | None = UserContext(payload["sub"]).user
    if not user:
        raise UserNotFoundError()

    return {
        "access_token": generate_access_token(user),
        "refresh_token": generate_refresh_token(user, payload),
    }


def decode_refresh_token_jti() -> str:
    try:
        token: str | None = request.cookies.get("refresh_token")
        if not token:
            raise InvalidTokenError("Missing refresh token")
        payload: dict[str, Any] = jwt.decode(
            token,
            current_app.config["REFRESH_SECRET_KEY"],
            algorithms=["HS256"],
            issuer="user-service",
            audience="ecommerce-services",
            options={"verify_exp": False},  # logout should work even if it just expired
        )
    except jwt.InvalidTokenError:
        raise InvalidTokenError("Invalid refresh token") from None

    if payload.get("type") != "refresh":
        raise InvalidTokenError("Invalid token type")

    return payload["jti"]


def attach_refresh_cookie(response: Response, refresh_token: str) -> Response:
    response.set_cookie(
        "refresh_token",
        refresh_token,
        httponly=True,
        secure=True,
        samesite="Strict",
        max_age=7 * 24 * 60 * 60,  # match REFRESH_TOKEN_TTL if you have one in config
        path="/api/users",
    )
    return response


def clear_refresh_cookie(response: Response) -> Response:
    response.delete_cookie("refresh_token", path="/api/users")
    return response
