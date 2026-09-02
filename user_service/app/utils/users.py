from datetime import datetime, timedelta, timezone
from functools import wraps
from uuid import uuid4

import jwt
from flask import current_app, g, request

from app.errors.exceptions import EmailAlreadyExistsError
from app.services.user_service import UserService
from app.utils.redis_utility import rotate_refresh_token


def validate_user_data(data):
    if UserService().check_user_existance(data["email"]):
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
    token = get_auth_header()
    if not token:
        return {"message": "Missing or malformed token"}, 401

    try:
        if refresh_token:
            key = current_app.config["REFRESH_SECRET_KEY"]
            algo = ["HS256"]
            token_type = "refresh"
        else:
            key = current_app.config["PUBLIC_KEY"]
            algo = ["RS256"]
            token_type = "access"

        payload = jwt.decode(
            token,
            key,
            algorithms=algo,
            issuer="user-service",
            audience="ecommerce-services",
        )
        if payload.get("type") != token_type:
            return {"message": "Invalid token type"}, 401

        return payload, 200
    except jwt.ExpiredSignatureError:
        return {"message": "Token has expired"}, 401
    except jwt.InvalidTokenError:
        return {"message": "Invalid token"}, 401

def login_required(staff_only=False):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            result, status = authenticate()
                
            if status != 200:
                return result, status

            g.user_id = result["sub"]
            g.user_email = result["email"]

            if staff_only and not UserService().is_staff(g.user_id):
                return {"message": "Unauthorized"}, 403

            return f(*args, **kwargs)
        return wrapper
    return decorator


def generate_new_access_token():
    result, status = authenticate(refresh_token=True)

    if status != 200:
        return result, status

    user = UserService().get_user_by_id(result["sub"])

    if not user:
        return {"message": "User not found"}, 404

    return {"access_token": generate_access_token(user), "refresh_token": generate_refresh_token(user, result)}, 200