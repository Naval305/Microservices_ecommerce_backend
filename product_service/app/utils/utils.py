import json
import time
from functools import wraps

from fastapi import HTTPException, Request

from app.utils.redis_config import RedisService, init_sync_redis
from app.schemas.custom_response import CustomResponse


redis_ins = RedisService()


def check_authentication(auth_details):
    print(auth_details)
    if (
        not auth_details
        or auth_details == b"null"
        or auth_details == b"false"
        or type(json.loads(auth_details)) != dict
        or "identity" not in json.loads(auth_details).keys()
    ):
        return False
    return json.loads(auth_details)


def get_authentication():
    redis = init_sync_redis()
    for i in range(1, 4):
        verified = redis.get("verified")
        if not verified or verified == b"" or verified == "None" or verified == "":
            time.sleep(i / 10)
        else:
            break
    redis.set(
        "verified",
        "",
        60,
    )
    return check_authentication(verified)


def cache(timeout: int):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            key = kwargs["request"].url.path
            cached_value = await redis_ins.get(key, timeout, True)
            print(cached_value)
            if cached_value is not None and cached_value != "null":
                return CustomResponse(data=json.loads(cached_value))

            result = await func(*args, **kwargs)
            if hasattr(result, "body"):
                data = json.dumps(json.loads(result.body).get("data"))
            else:
                result["_id"] = str(result["_id"])
                data = json.dumps(json.loads(result))
            kwargs["background_tasks"].add_task(
                redis_ins.set,
                key,
                data,
                timeout,
            )
            return result

        return wrapper

    return decorator
