from app.extensions.redis_connection import redis_client


USER_ACTIVE_TTL = 60 * 60 * 24  # 24h safety net, not the source of truth


def set_user_active_status(user_id, is_active: bool):
    redis_client.set(f"user:active:{user_id}", "1" if is_active else "0", ex=USER_ACTIVE_TTL)

def get_cached_user_active_status(user_id):
    val = redis_client.get(f"user:active:{user_id}")
    return None if val is None else val == "1"  # None = cache miss