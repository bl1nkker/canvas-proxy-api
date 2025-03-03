import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool

from db.config import DbConfig, get_db_config
from db.session import Session


class DbTest:
    @pytest.fixture(scope="class", autouse=True)
    def clear_config_cache_for_tests(self):
        from utils import clear_config_cache

        clear_config_cache()

    @pytest.fixture(scope="class", autouse=True)
    def set_python_env(self):
        os.environ["PYTHON_ENV"] = "test"

    @pytest.fixture(scope="class")
    def db_config(self, set_python_env) -> DbConfig:
        return get_db_config()

    @pytest.fixture(scope="class")
    def db_engine(self, db_config):
        return create_engine(db_config.app_url(), poolclass=NullPool)

    @pytest.fixture(scope="class", autouse=True)
    def db_init(self, db_engine):
        Session.configure(bind=db_engine)
        yield
        db_engine.dispose()

    @pytest.fixture
    def db_session(self, db_init):
        session = Session()
        yield session
        session.close()
