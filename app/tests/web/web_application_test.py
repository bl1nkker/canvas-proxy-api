import pytest
from fastapi.testclient import TestClient

from web.main import app


class WebApplicationTest:
    @pytest.fixture
    def client(self) -> TestClient:
        with TestClient(app, raise_server_exceptions=False) as c:
            yield c
