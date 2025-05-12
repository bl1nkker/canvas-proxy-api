import pytest

from tests.base_test import BaseTest
from tests.fixtures import sample_data
from tests.web.web_application_test import WebApplicationTest


class TestAssignmentRouter(BaseTest, WebApplicationTest):
    @pytest.mark.asyncio
    async def test_create_assignment(
        self,
        client,
        create_canvas_user,
        create_canvas_course,
        create_assignment_group,
        mock_aiohttp_get,
        mock_aiohttp_post,
        cleanup_all,
    ):
        canvas_user = create_canvas_user(username="user")
        course = create_canvas_course(canvas_user=canvas_user)
        assignment_group = create_assignment_group(course=course, name="Test Group")
        response = client.post(
            "/api/assignments/v1/",
            json={
                "course_id": course.id,
                "assignment_group_id": assignment_group.id,
            },
            cookies=sample_data.canvas_auth_data,
        )
        assert response.status_code == 201
        data = response.json()
        assert data == {
            "assignment_group_id": 1,
            "canvas_assignment_id": 73376,
            "id": 1,
            "name": "test from python finally",
            "web_id": "web-id-5",
        }

    def test_list_assignments(
        self,
        client,
        create_canvas_user,
        create_canvas_course,
        create_assignment_group,
        create_assignment,
        cleanup_all,
    ):
        canvas_user = create_canvas_user(username="user")
        course = create_canvas_course(canvas_user=canvas_user)
        assignment_group = create_assignment_group(course=course, name="Test Group")
        for i in range(5):
            create_assignment(
                assignment_group=assignment_group, name=f"target assignment {i}"
            )
        response = client.get("/api/assignments/v1/")
        assert response.status_code == 201
        data = response.json()
        assert data["page"] == 1
        assert data["page_size"] == 10
        assert data["total"] == 5
        assert len(data["items"]) == 5

    def test_list_assignments_filtered_by_assignment_group_id(
        self,
        client,
        create_canvas_user,
        create_canvas_course,
        create_assignment_group,
        create_assignment,
        cleanup_all,
    ):
        canvas_user = create_canvas_user(username="user")
        course = create_canvas_course(canvas_user=canvas_user)
        assignment_group = create_assignment_group(course=course, name="Test Group")
        another_assignment_group = create_assignment_group(
            course=course, name="Another Test Group"
        )
        for i in range(5):
            create_assignment(
                assignment_group=assignment_group, name=f"target assignment {i}"
            )
        for i in range(10):
            create_assignment(
                assignment_group=another_assignment_group,
                name=f"another target assignment {i}",
            )
        response = client.get(
            f"/api/assignments/v1/?assignment_group_id={assignment_group.id}"
        )
        assert response.status_code == 201
        data = response.json()
        assert data["page"] == 1
        assert data["page_size"] == 10
        assert data["total"] == 5
        assert len(data["items"]) == 5
