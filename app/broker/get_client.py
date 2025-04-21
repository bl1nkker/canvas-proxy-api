from broker.config import get_broker_config
from broker.create_client import create_redis_client


def get_broker_client():
    redis_config = get_broker_config()
    redis_client = create_redis_client(redis_config.host, redis_config.database)
    try:
        yield redis_client
    finally:
        redis_client.close()
