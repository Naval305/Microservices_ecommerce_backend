import redis

from app.errors.exceptions import TokenReuseDetectedError

redis_client = redis.Redis(host='127.0.0.1', port=6379, decode_responses=True)
USER_ACTIVE_TTL = 60 * 60 * 24  # 24h safety net, not the source of truth


def revoke_all_sessions(user_id):
    user_sessions_key = f"user_sessions:{user_id}"
    jtis = redis_client.smembers(user_sessions_key)  # O(1) lookup, returns only THIS user's jtis

    for jti in jtis:
        key = f"refresh_jti:{jti}"
        if redis_client.exists(key):
            redis_client.hset(key, "revoked", "1")

    redis_client.delete(user_sessions_key)


def revoke_single_session(user_id, jti):
    key = f"refresh_jti:{jti}"
    info = redis_client.hgetall(key)

    # only revoke if this jti actually belongs to the calling user —
    # stops one user from logging out someone else's session by guessing a jti
    if not info or info.get("user_id") != str(user_id):
        return False

    redis_client.hset(key, "revoked", "1")
    redis_client.srem(f"user_sessions:{user_id}", jti)
    return True


def rotate_refresh_token(user, token_info, old_refresh_token_info):
    """
    Store the refresh token information in Redis with an expiration time.
    """
    if old_refresh_token_info:
        # 1. Atomic check-and-update using Lua
        old_key = f"refresh_jti:{old_refresh_token_info['jti']}"
        revoke_script = """
        if redis.call('EXISTS', KEYS[1]) == 1 then
            local was_revoked = redis.call('HGET', KEYS[1], 'revoked')
            redis.call('HSET', KEYS[1], 'revoked', '1')
            return was_revoked
        end
        return false
        """
        result = redis_client.eval(revoke_script, 1, old_key)

        if result == "1":
            # reuse detected — revoke ALL sessions for this user, force re-login
            revoke_all_sessions(user.id)
            raise TokenReuseDetectedError()

    # 2. Store new token information
    key = f"refresh_jti:{token_info['jti']}"
    redis_client.hset(
        key,
        mapping={
            "user_id": str(user.id),
            "revoked": "0",
            "issued_at": token_info['iat'].isoformat()
        },
    )
    redis_client.expireat(key, token_info['exp'])

    user_sessions_key = f"user_sessions:{user.id}"
    redis_client.sadd(user_sessions_key, token_info['jti'])
    redis_client.expireat(user_sessions_key, token_info['exp'])


def set_user_active_status(user_id, is_active: bool):
    redis_client.set(f"user:active:{user_id}", "1" if is_active else "0", ex=USER_ACTIVE_TTL)

def get_cached_user_active_status(user_id):
    val = redis_client.get(f"user:active:{user_id}")
    return None if val is None else val == "1"  # None = cache miss