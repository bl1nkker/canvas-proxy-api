import redis


def create_redis_client(host: str = "127.0.0.1", db=0) -> redis.Redis:
    return redis.Redis(host=host, db=db)
