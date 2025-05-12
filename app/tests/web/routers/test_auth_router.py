from http.cookies import SimpleCookie
from unittest.mock import patch

import pytest

from src.dto import auth_dto
from src.services.source_data_load_queue_service import SourceDataLoadQueueService
from tests.base_test import BaseTest
from tests.fixtures import sample_data
from tests.web.web_application_test import WebApplicationTest


class TestAuthRouter(BaseTest, WebApplicationTest):

    @pytest.mark.asyncio
    @patch("aiohttp.ClientSession.get")
    @patch("aiohttp.ClientSession.post")
    async def test_login(
        self,
        mock_post,
        mock_get,
        client,
        canvas_ok_response,
        create_canvas_user,
        cleanup_all,
    ):
        mock_get.return_value = canvas_ok_response
        mock_post.return_value = canvas_ok_response
        create_canvas_user(username="test@gmail.com", password="test-pwd")
        dto = auth_dto.LoginRequest(username="test@gmail.com", password="test-pwd")
        response = client.post("/api/auth/v1/signin", json=dto.model_dump())
        assert response.status_code == 200

        data = response.json()
        assert data == {
            "username": "test@gmail.com",
            "web_id": "web-id-1",
            "canvas_user": {
                "web_id": "web-id-2",
                "id": 1,
                "username": "canvas_test@gmail.com",
            },
        }

        assert "set-cookie" in response.headers
        raw_cookie = response.headers["set-cookie"]
        cookies = {
            key: morsel.value for key, morsel in SimpleCookie(raw_cookie).items()
        }
        assert cookies == sample_data.canvas_auth_data

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "login_request",
        [
            auth_dto.LoginRequest(username="incorrect@gmail.com", password="test-pwd"),
            auth_dto.LoginRequest(username="test@gmail.com", password="incorrect-pwd"),
        ],
    )
    async def test_login_should_raise_on_invalid_credentials(
        self,
        client,
        login_request,
        create_canvas_user,
        cleanup_all,
    ):
        create_canvas_user(username="test@gmail.com", password="test-pwd")
        response = client.post("/api/auth/v1/signin", json=login_request.dict())
        assert response.status_code == 401
        data = response.json()
        assert data["message"] == "_error_msg_invalid_credentials"

    @pytest.mark.asyncio
    async def test_login_should_raise_when_canvas_user_not_found(
        self,
        client,
        create_user,
        cleanup_all,
    ):
        dto = auth_dto.LoginRequest(username="test@gmail.com", password="test-pwd")
        create_user(username="test@gmail.com", password="test-pwd")
        response = client.post("/api/auth/v1/signin", json=dto.model_dump())
        assert response.status_code == 404
        data = response.json()
        assert data["message"] == "_error_msg_canvas_user_not_found:test@gmail.com"

    @pytest.mark.asyncio
    @patch("aiohttp.ClientSession.get")
    @patch("aiohttp.ClientSession.post")
    @patch.object(
        SourceDataLoadQueueService,
        "load_canvas_data",
        return_value="job-id-1",
    )
    async def test_create_user(
        self,
        mock_job,
        mock_post,
        mock_get,
        client,
        canvas_ok_response,
        patch_shortuuid,
        cleanup_all,
    ):
        mock_get.return_value = canvas_ok_response
        mock_post.return_value = canvas_ok_response
        dto = auth_dto.LoginRequest(username="test@gmail.com", password="test-pwd")
        response = client.post("/api/auth/v1/signup", json=dto.dict())
        assert response.status_code == 200

        data = response.json()
        assert data["username"] == "test@gmail.com"
        assert data["web_id"] == "web-id-1"
        assert data["canvas_user"]["web_id"] == "web-id-2"
        assert data["canvas_user"]["username"] == "test@gmail.com"

        assert "set-cookie" in response.headers
        raw_cookie = response.headers["set-cookie"]
        cookies = {
            key: morsel.value for key, morsel in SimpleCookie(raw_cookie).items()
        }
        assert cookies == sample_data.canvas_auth_data

    @patch.object(
        SourceDataLoadQueueService,
        "load_canvas_data",
        return_value="job-id-1",
    )
    @pytest.mark.asyncio
    async def test_create_user_should_raise_on_same_user(
        self,
        mock_job,
        client,
        create_canvas_user,
        cleanup_all,
    ):
        create_canvas_user(username="test@gmail.com", password="test-pwd")
        dto = auth_dto.LoginRequest(username="test@gmail.com", password="test-pwd")
        response = client.post("/api/auth/v1/signup", json=dto.model_dump())
        assert response.status_code == 400
        data = response.json()
        assert (
            data["message"]
            == "_error_msg_user_with_username_already_exists:test@gmail.com"
        )
