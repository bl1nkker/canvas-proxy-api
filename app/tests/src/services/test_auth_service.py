from unittest.mock import call, patch

import pytest

from src.dto import auth_dto
from src.errors.types import InvalidCredentialsError, NotFoundError
from tests.base_test import BaseTest


class TestAuthService(BaseTest):

    @pytest.mark.asyncio
    @patch("aiohttp.ClientSession.get")
    @patch("aiohttp.ClientSession.post")
    async def test_get_canvas_auth_data(
        self,
        mock_post,
        mock_get,
        canvas_ok_response,
        create_canvas_user,
        auth_service,
        cleanup_all,
    ):
        create_canvas_user(username="test@gmail.com", password="test-pwd")
        dto = auth_dto.LoginRequest(username="test@gmail.com", password="test-pwd")
        mock_get.return_value = canvas_ok_response
        mock_post.return_value = canvas_ok_response
        auth_data = await auth_service.get_canvas_auth_data(dto=dto)
        assert auth_data.dict(by_alias=True) == {
            "canvas_auth_data": {
                "_csrf_token": "6D2%2FyVAKZOxBRl6qZW",
                "_legacy_normandy_session": "pG-loNiNeyypme8vr5TO",
                "_normandy_session": "pG-loNiNeyypme8vr5TO",
                "log_session_id": "9f8187d804aaf1d15913",
            },
            "username": "test@gmail.com",
            "web_id": "web-id-1",
        }

        actual_calls = [c for c in mock_get.call_args_list if c[0]]

        expected_calls = [
            call(
                "https://canvas.narxoz.kz/login/canvas",
                cookies={
                    "_csrf_token": "6D2%2FyVAKZOxBRl6qZW",
                    "_legacy_normandy_session": "pG-loNiNeyypme8vr5TO",
                    "_normandy_session": "pG-loNiNeyypme8vr5TO",
                    "log_session_id": "9f8187d804aaf1d15913",
                },
            ),
            call(
                "https://canvas.narxoz.kz/login/canvas",
                cookies={
                    "_csrf_token": "6D2%2FyVAKZOxBRl6qZW",
                    "_legacy_normandy_session": "pG-loNiNeyypme8vr5TO",
                    "_normandy_session": "pG-loNiNeyypme8vr5TO",
                    "log_session_id": "9f8187d804aaf1d15913",
                },
            ),
        ]

        assert actual_calls == expected_calls, f"Unexpected calls: {actual_calls}"

        mock_post.assert_called_once_with(
            "https://canvas.narxoz.kz/login/canvas",
            data={
                "authenticity_token": "6D2/yVAKZOxBRl6qZW",
                "pseudonym_session[unique_id]": "canvas_test@gmail.com",
                "pseudonym_session[password]": "test-pwd",
            },
            cookies={
                "_csrf_token": "6D2%2FyVAKZOxBRl6qZW",
                "_legacy_normandy_session": "pG-loNiNeyypme8vr5TO",
                "_normandy_session": "pG-loNiNeyypme8vr5TO",
                "log_session_id": "9f8187d804aaf1d15913",
            },
        )

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "login_request",
        [
            auth_dto.LoginRequest(username="incorrect@gmail.com", password="test-pwd"),
            auth_dto.LoginRequest(username="test@gmail.com", password="incorrect-pwd"),
        ],
    )
    async def test_get_canvas_auth_data_should_raise_on_invalid_credentials(
        self,
        login_request,
        create_canvas_user,
        auth_service,
        cleanup_all,
    ):
        create_canvas_user(username="test@gmail.com", password="test-pwd")
        with pytest.raises(InvalidCredentialsError):
            await auth_service.get_canvas_auth_data(dto=login_request)

    @pytest.mark.asyncio
    async def test_get_canvas_auth_data_should_raise_when_canvas_user_not_found(
        self,
        create_user,
        auth_service,
        cleanup_all,
    ):
        create_user(username="test@gmail.com", password="test-pwd")
        dto = auth_dto.LoginRequest(username="test@gmail.com", password="test-pwd")
        with pytest.raises(NotFoundError):
            await auth_service.get_canvas_auth_data(dto=dto)
