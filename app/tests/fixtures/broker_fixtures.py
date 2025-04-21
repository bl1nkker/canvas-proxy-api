import os

import pytest

from broker.config import RedisConfig, get_broker_config
from broker.context import redis_client_var
from broker.create_client import create_redis_client


class BrokerTest:
    @pytest.fixture(scope="class", autouse=True)
    def set_python_env(self):
        os.environ["PYTHON_ENV"] = "test"

    @pytest.fixture(scope="class")
    def broker_config(self, set_python_env) -> RedisConfig:
        return get_broker_config()

    @pytest.fixture
    def broker_client(self, broker_config):
        return create_redis_client(host=broker_config.host, db=broker_config.database)

    @pytest.fixture(autouse=True)
    def broker_client_var(self, broker_client):
        token = redis_client_var.set(broker_client)
        yield
        redis_client_var.reset(token)
