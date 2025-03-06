from unittest.mock import patch

import pytest

from tests.base_test import BaseTest
from tests.fixtures import sample_data
from tests.web.web_application_test import WebApplicationTest


class TestCanvasCourseRouter(BaseTest, WebApplicationTest):

    def test_list_courses(
        self,
        client,
        create_canvas_course,
        create_canvas_user,
        cleanup_all,
    ):
        canvas_user = create_canvas_user()
        for i in range(5):
            create_canvas_course(
                long_name=f"test-long_name{i}",
                canvas_course_id=i,
                canvas_user=canvas_user,
            )
        response = client.get("/api/canvas-courses/v1")
        assert response.status_code == 200

        data = response.json()
        assert data["page"] == 1
        assert data["page_size"] == 10
        assert data["total"] == 5
        assert len(data["items"]) == 5

    def test_list_courses_filtered_by_user(
        self,
        client,
        create_canvas_course,
        create_canvas_user,
        cleanup_all,
    ):
        canvas_user = create_canvas_user()
        for i in range(2):
            create_canvas_course(
                long_name=f"test{i}",
                canvas_user=canvas_user,
                canvas_course_id=i,
            )

        another_user = create_canvas_user(
            username="another@.com",
            canvas_id="canvas_id_228",
        )
        for i in range(5):
            create_canvas_course(
                long_name=f"another_test{i}",
                canvas_user=another_user,
                canvas_course_id=i + 5,
            )
        response = client.get(f"/api/canvas-courses/v1?canvas_user_id={canvas_user.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["page_size"] == 10
        assert data["total"] == 2
        for course in data["items"]:
            assert course["owner_username"] == canvas_user.username

    @pytest.mark.asyncio
    @patch("aiohttp.ClientSession.get")
    async def test_load_courses(
        self,
        mock_get,
        client,
        canvas_course_ok_response,
        create_canvas_user,
        cleanup_all,
    ):
        mock_get.return_value = canvas_course_ok_response
        canvas_user = create_canvas_user()
        response = client.post(
            f"/api/canvas-courses/v1/load/users/{canvas_user.web_id}",
            cookies=sample_data.canvas_auth_data,
        )
        assert response.status_code == 201
        data = response.json()
        assert len(data) == 2
