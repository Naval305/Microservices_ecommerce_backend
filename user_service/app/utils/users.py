from datetime import datetime, timedelta, timezone
from functools import wraps
from uuid import uuid4

import jwt
from flask import current_app, g, request

from app.errors.exceptions import EmailAlreadyExistsError, InvalidTokenError, UnauthorizedError, UserNotFoundError
from app.services.user_service import UserContext
from app.utils.redis_utility import rotate_refresh_token
from app.utils.redis_utility import get_cached_user_active_status, set_user_active_status


def validate_user_data(data):
    if UserContext().check_user_existance(data["email"]):
        raise EmailAlreadyExistsError()

    return None


def get_auth_header():
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None
    return auth_header.split(" ")[-1]


def generate_access_token(user):
    now = datetime.now(timezone.utc)
    payload = {
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


def generate_refresh_token(user, old_refresh_token_info=None):
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user.id),
        "type": "refresh",
        "jti": str(uuid4()),   # unique id — lets you revoke this one token later
        "iss": "user-service",
        "aud": "ecommerce-services",
        "iat": now,
        "nbf": now,
        "exp": now + timedelta(days=7),
    }
    token = jwt.encode(payload, current_app.config["REFRESH_SECRET_KEY"], algorithm="HS256")
    rotate_refresh_token(user, payload, old_refresh_token_info)
    return token


def generate_tokens(user):
    return {
        "access_token": generate_access_token(user),
        "refresh_token": generate_refresh_token(user),
    }


def authenticate(refresh_token=False):
    if refresh_token:
        token = request.cookies.get("refresh_token")
    else:
        token = get_auth_header()

    if not token:
        raise InvalidTokenError("Missing or malformed token")

    if refresh_token:
        key = current_app.config["REFRESH_SECRET_KEY"]
        algo = ["HS256"]
        token_type = "refresh"
    else:
        key = current_app.config["PUBLIC_KEY"]
        algo = ["RS256"]
        token_type = "access"

    try:
        payload = jwt.decode(
            token, key, algorithms=algo,
            issuer="user-service", audience="ecommerce-services",
        )
    except jwt.ExpiredSignatureError:
        raise InvalidTokenError("Token has expired")
    except jwt.InvalidTokenError:
        raise InvalidTokenError("Invalid token")

    if payload.get("type") != token_type:
        raise InvalidTokenError("Invalid token type")

    return payload


def is_user_active(user_id):
    cached = get_cached_user_active_status(user_id)
    if cached is not None:
        return cached
    user = UserContext(user_id).user
    if not user:
        raise UserNotFoundError()
    set_user_active_status(user_id, user.is_active)
    return user.is_active


def login_required(staff_only=False):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            payload = authenticate()

            if not is_user_active(payload["sub"]):
                raise UnauthorizedError("Account is deactivated")

            g.user_id = payload["sub"]
            g.user_email = payload["email"]

            if staff_only:
                user = UserContext(g.user_id).user
                if not user.is_staff:
                    raise UnauthorizedError("Unauthorized: Staff access required")

            return f(*args, **kwargs)
        return wrapper
    return decorator


def generate_new_access_token():
    payload = authenticate(refresh_token=True)   # raises on failure

    user = UserContext(payload["sub"]).user
    if not user:
        raise UserNotFoundError()

    return {
        "access_token": generate_access_token(user),
        "refresh_token": generate_refresh_token(user, payload),
    }


def decode_refresh_token_jti():
    try:
        token = request.cookies.get("refresh_token")
        if not token:
            raise InvalidTokenError("Missing refresh token")
        payload = jwt.decode(
            token, current_app.config["REFRESH_SECRET_KEY"], algorithms=["HS256"],
            issuer="user-service", audience="ecommerce-services",
            options={"verify_exp": False},  # logout should work even if it just expired
        )
    except jwt.InvalidTokenError:
        raise InvalidTokenError("Invalid refresh token")

    if payload.get("type") != "refresh":
        raise InvalidTokenError("Invalid token type")

    return payload["jti"]


def attach_refresh_cookie(response, refresh_token):
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


def clear_refresh_cookie(response):
    response.delete_cookie("refresh_token", path="/api/users")
    return response