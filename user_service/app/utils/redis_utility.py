import redis

from app.errors.exceptions import TokenReuseDetectedError

r = redis.Redis(host='127.0.0.1', port=6379, decode_responses=True)


def revoke_all_sessions(user_id):
    user_sessions_key = f"user_sessions:{user_id}"
    jtis = r.smembers(user_sessions_key)  # O(1) lookup, returns only THIS user's jtis

    for jti in jtis:
        key = f"refresh_jti:{jti}"
        if r.exists(key):
            r.hset(key, "revoked", "1")

    r.delete(user_sessions_key)


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
        result = r.eval(revoke_script, 1, old_key)

        if result == "1":
            # reuse detected — revoke ALL sessions for this user, force re-login
            revoke_all_sessions(user.id)
            raise TokenReuseDetectedError()

    # 2. Store new token information
    key = f"refresh_jti:{token_info['jti']}"
    r.hset(
        key,
        mapping={
            "user_id": str(user.id),
            "revoked": "0",
            "issued_at": token_info['iat'].isoformat()
        },
    )
    r.expireat(key, token_info['exp'])

    user_sessions_key = f"user_sessions:{user.id}"
    r.sadd(user_sessions_key, token_info['jti'])
    r.expireat(user_sessions_key, token_info['exp'])
