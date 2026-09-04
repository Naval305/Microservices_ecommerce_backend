import redis

redis_client = redis.Redis()  # unconfigured placeholder


def init_redis(app):
    redis_client.connection_pool = redis.ConnectionPool.from_url(
        app.config["REDIS_URL"], decode_responses=True
    )