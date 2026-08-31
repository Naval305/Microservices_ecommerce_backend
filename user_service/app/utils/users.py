from datetime import datetime, timedelta, timezone
from functools import wraps
import json
from uuid import uuid4

import jwt
from flask import current_app, g, request

from app.services.user_service import UserService


def validate_user_data(data):
    if UserService().check_user_existance(data["email"]):
        return {"message": "Email address already in use"}, 409

    return None


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


def generate_refresh_token(user):
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user.id),
        "type": "refresh",
        "jti": str(uuid4()),   # unique id — lets you revoke this one token later
        "iss": "user-service",
        "iat": now,
        "nbf": now,
        "exp": now + timedelta(days=7),
    }
    return jwt.encode(payload, current_app.config["REFRESH_SECRET_KEY"], algorithm="HS256")


def generate_tokens(user):
    return {
        "access_token": generate_access_token(user),
        "refresh_token": generate_refresh_token(user),
    }


def authenticate():
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return {"message": "Missing or malformed token"}, 401

    token = auth_header.split(" ")[-1]

    try:
        payload = jwt.decode(
            token,
            current_app.config["PUBLIC_KEY"],
            algorithms=["RS256"],
            issuer="user-service",
            audience="ecommerce-services",
        )
        if payload.get("type") != "access":
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

            if staff_only and not UserService().is_staff(g.user_email):
                return {"message": "Unauthorized"}, 403

            return f(*args, **kwargs)
        return wrapper
    return decorator
