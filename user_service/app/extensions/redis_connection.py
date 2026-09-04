import logging

import redis

from app.errors.exceptions import RedisUnavailableError

logger = logging.getLogger(__name__)

# Real placeholder client — becomes usable once init_redis() attaches a pool.
redis_client = redis.Redis()


def init_redis(app):
    """Build the connection pool from Config, the same way RabbitMQ settings are read.

    Uses REDIS_HOST/PORT/DB/PASSWORD (via REDIS_URL) plus explicit socket
    timeouts and a bounded pool size, so a hung/unreachable Redis fails fast
    instead of blocking a request thread indefinitely.
    """
    pool = redis.ConnectionPool.from_url(
        app.config["REDIS_URL"],
        decode_responses=True,
        socket_connect_timeout=app.config.get("REDIS_SOCKET_CONNECT_TIMEOUT", 2),
        socket_timeout=app.config.get("REDIS_SOCKET_TIMEOUT", 2),
        max_connections=app.config.get("REDIS_MAX_CONNECTIONS", 20),
        health_check_interval=30,
    )
    redis_client.connection_pool = pool

    try:
        redis_client.ping()
    except redis.exceptions.RedisError:
        # Don't crash app startup over a Redis blip — /health already reports
        # this, and callers wrap their own redis_client calls.
        app.logger.warning("Redis is not reachable at startup; continuing without it.")


def safe_redis_call(func, *args, **kwargs):
    """Run a redis_client call, converting connection/timeout errors into
    RedisUnavailableError instead of letting them surface as raw 500s.

    Usage: safe_redis_call(redis_client.get, key)
    """
    try:
        return func(*args, **kwargs)
    except redis.exceptions.RedisError as exc:
        logger.warning("Redis call failed: %s", exc)
        raise RedisUnavailableError("Redis is temporarily unavailable") from exc
