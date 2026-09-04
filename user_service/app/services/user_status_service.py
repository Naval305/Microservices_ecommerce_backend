import logging

import redis

from app.extensions.redis_connection import redis_client

logger = logging.getLogger(__name__)
USER_ACTIVE_TTL = 60 * 60 * 24  # 24h safety net, not the source of truth


def set_user_active_status(user_id, is_active: bool):
    try:
        redis_client.set(f"user:active:{user_id}", "1" if is_active else "0", ex=USER_ACTIVE_TTL)
    except redis.exceptions.RedisError as exc:
        logger.warning(
            "Redis unavailable while caching active status for user %s: %s", user_id, exc
        )


def get_cached_user_active_status(user_id):
    try:
        val = redis_client.get(f"user:active:{user_id}")
    except redis.exceptions.RedisError as exc:
        logger.warning(
            "Redis unavailable while reading cached active status for user %s: %s", user_id, exc
        )
        return None  # treat as cache miss, caller falls back to DB
    return None if val is None else val == "1"  # None = cache miss
