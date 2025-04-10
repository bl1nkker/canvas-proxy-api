from unittest.mock import AsyncMock, patch

import pytest

from src.dto import auth_dto
from src.enums.attendance_status import AttendanceStatus
from src.enums.attendance_value import AttendanceValue
from src.errors.types import CanvasAPIError, NotFoundError
from tests.base_test import BaseTest
from tests.fixtures import sample_data


class TestCanvasAssignmentService(BaseTest):
    @pytest.fixture
    def canvas_assignment_secure_params_response(self):
        mock_response = AsyncMock()
        mock_response.__aenter__.return_value = mock_response
        mock_response.__aexit__.return_value = None
        mock_response.text.return_value = (
            sample_data.canvas_assignment_secure_params_response
        )
        return mock_response

    @pytest.fixture
    def canvas_assignment_response(self):
        mock_response = AsyncMock()
        mock_response.__aenter__.return_value = mock_response
        mock_response.__aexit__.return_value = None
        mock_response.json.return_value = sample_data.canvas_create_assignment_response
        return mock_response

    @pytest.fixture
    def canvas_assignment_groups_response(self):
        mock_response = AsyncMock()
        mock_response.__aenter__.return_value = mock_response
        mock_response.__aexit__.return_value = None
        mock_response.json.return_value = (
            sample_data.canvas_get_assignment_groups_response
        )
        return mock_response

    @pytest.fixture
    def canvas_assignment_groups_empty_response(self):
        mock_response = AsyncMock()
        mock_response.__aenter__.return_value = mock_response
        mock_response.__aexit__.return_value = None
        mock_response.json.return_value = []
        return mock_response

    @pytest.mark.asyncio
    @patch("aiohttp.ClientSession.get")
    @patch("aiohttp.ClientSession.post")
    async def test_create_assignment(
        self,
        mock_post,
        mock_get,
        canvas_assignment_service,
        create_canvas_user,
        create_canvas_course,
        assignment_repo,
        canvas_assignment_secure_params_response,
        canvas_assignment_response,
        create_assignment_group,
        cleanup_all,
    ):
        mock_get.return_value = canvas_assignment_secure_params_response
        mock_post.return_value = canvas_assignment_response
        canvas_user = create_canvas_user(username="user")
        course = create_canvas_course(canvas_user=canvas_user)
        assignment_group = create_assignment_group(course=course, name="Test Group")
        canvas_auth_data = auth_dto.CanvasAuthData(**sample_data.canvas_auth_data)
        assignment = await canvas_assignment_service.create_assignment(
            web_id=course.web_id,
            assignment_group_web_id=assignment_group.web_id,
            canvas_auth_data=canvas_auth_data,
        )
        assert assignment.name == "test from python finally"
        assert assignment.assignment_group_id == assignment_group.id
        assert assignment.canvas_assignment_id == 73376
        with assignment_repo.session():
            assignments = assignment_repo.list_all()
            assert len(assignments) == 1
            assert assignments[0].name == "test from python finally"
            assert assignments[0].assignment_group_id == assignment_group.id
            assert assignments[0].canvas_assignment_id == 73376

    @pytest.mark.asyncio
    @patch("aiohttp.ClientSession.get")
    @patch("aiohttp.ClientSession.post")
    async def test_create_assignment_should_create_attendance_for_each_enrollment(
        self,
        mock_post,
        mock_get,
        canvas_assignment_service,
        create_canvas_user,
        create_canvas_course,
        create_student,
        create_enrollment,
        attendance_repo,
        canvas_assignment_secure_params_response,
        canvas_assignment_response,
        create_assignment_group,
        cleanup_all,
    ):
        mock_get.return_value = canvas_assignment_secure_params_response
        mock_post.return_value = canvas_assignment_response
        canvas_user = create_canvas_user(username="user")
        course = create_canvas_course(canvas_user=canvas_user)
        assignment_group = create_assignment_group(course=course, name="Test Group")
        for _ in range(5):
            student = create_student()
            create_enrollment(course=course, student=student)

        canvas_auth_data = auth_dto.CanvasAuthData(**sample_data.canvas_auth_data)
        assignment = await canvas_assignment_service.create_assignment(
            web_id=course.web_id,
            assignment_group_web_id=assignment_group.web_id,
            canvas_auth_data=canvas_auth_data,
        )
        with attendance_repo.session():
            attendances = attendance_repo.list_all()
            assert len(attendances) == 5
            for att in attendances:
                assert att.assignment.web_id == assignment.web_id
                assert att.status == AttendanceStatus.COMPLETED
                assert att.value == AttendanceValue.INCOMPLETE

    @pytest.mark.asyncio
    async def test_create_assignment_should_raise_on_invalid_course(
        self,
        canvas_assignment_service,
        create_canvas_user,
        create_canvas_course,
        create_assignment_group,
        cleanup_all,
    ):
        canvas_user = create_canvas_user(username="user")
        course = create_canvas_course(canvas_user=canvas_user)
        assignment_group = create_assignment_group(course=course, name="Test Group")
        canvas_auth_data = auth_dto.CanvasAuthData(**sample_data.canvas_auth_data)
        with pytest.raises(NotFoundError) as exc:
            await canvas_assignment_service.create_assignment(
                web_id="unknown-web-id",
                assignment_group_web_id=assignment_group.web_id,
                canvas_auth_data=canvas_auth_data,
            )
        assert exc.value.message == "_err_message_course_not_found:unknown-web-id"

    @pytest.mark.asyncio
    @patch("aiohttp.ClientSession.get")
    async def test_get_attendance_assignment_group_should_create_assignment_group(
        self,
        mock_get,
        canvas_assignment_service,
        create_canvas_user,
        create_canvas_course,
        canvas_assignment_groups_response,
        assignment_group_repo,
        cleanup_all,
    ):
        mock_get.return_value = canvas_assignment_groups_response
        canvas_user = create_canvas_user(username="user")
        course = create_canvas_course(canvas_user=canvas_user)
        canvas_auth_data = auth_dto.CanvasAuthData(**sample_data.canvas_auth_data)
        await canvas_assignment_service.get_attendance_assignment_group(
            web_id=course.web_id, canvas_auth_data=canvas_auth_data
        )
        with assignment_group_repo.session():
            assignment_groups = assignment_group_repo.list_all()
            assert len(assignment_groups) == 1
            assert assignment_groups[0].course_id == course.id
            assert assignment_groups[0].name == "Сабаққа қатысу/Посещаемость"
            assert assignment_groups[0].group_weight == 0
            assert assignment_groups[0].course_id == course.id
            assert assignment_groups[0].canvas_assignment_group_id == 14761

    @pytest.mark.asyncio
    @patch("aiohttp.ClientSession.get")
    async def test_get_attendance_assignment_group_should_not_create_assignment_group_when_assignment_group_exists(
        self,
        mock_get,
        canvas_assignment_service,
        create_canvas_user,
        create_canvas_course,
        canvas_assignment_groups_response,
        assignment_group_repo,
        create_assignment_group,
        cleanup_all,
    ):
        mock_get.return_value = canvas_assignment_groups_response
        canvas_user = create_canvas_user(username="user")
        course = create_canvas_course(canvas_user=canvas_user)
        create_assignment_group(
            course=course,
            name="Сабаққа қатысу/Посещаемость",
            canvas_assignment_group_id=14761,
        )
        with assignment_group_repo.session():
            assignment_groups = assignment_group_repo.list_all()
            assert len(assignment_groups) == 1

        canvas_auth_data = auth_dto.CanvasAuthData(**sample_data.canvas_auth_data)
        await canvas_assignment_service.get_attendance_assignment_group(
            web_id=course.web_id, canvas_auth_data=canvas_auth_data
        )
        with assignment_group_repo.session():
            assignment_groups = assignment_group_repo.list_all()
            assert len(assignment_groups) == 1
            assert assignment_groups[0].course_id == course.id
            assert assignment_groups[0].name == "Сабаққа қатысу/Посещаемость"
            assert assignment_groups[0].group_weight == 10
            assert assignment_groups[0].course_id == course.id
            assert assignment_groups[0].canvas_assignment_group_id == 14761

    @pytest.mark.asyncio
    @patch("aiohttp.ClientSession.get")
    async def test_get_attendance_assignment_group_should_create_assignments(
        self,
        mock_get,
        canvas_assignment_service,
        create_canvas_user,
        create_canvas_course,
        canvas_assignment_groups_response,
        assignment_repo,
        cleanup_all,
    ):
        mock_get.return_value = canvas_assignment_groups_response
        canvas_user = create_canvas_user(username="user")
        course = create_canvas_course(canvas_user=canvas_user)
        canvas_auth_data = auth_dto.CanvasAuthData(**sample_data.canvas_auth_data)
        await canvas_assignment_service.get_attendance_assignment_group(
            web_id=course.web_id, canvas_auth_data=canvas_auth_data
        )
        with assignment_repo.session():
            assignments = assignment_repo.list_all()
            assert len(assignments) == 2
            for assignment in assignments:
                assert assignment.canvas_assignment_id in set([67301, 68220])
                assert assignment.assignment_group_id == 1
                assert assignment.name is not None

    @pytest.mark.asyncio
    @patch("aiohttp.ClientSession.get")
    async def test_get_attendance_assignment_group_should_not_create_assignments_when_assignment_exists(
        self,
        mock_get,
        canvas_assignment_service,
        create_canvas_user,
        create_canvas_course,
        canvas_assignment_groups_response,
        assignment_repo,
        create_assignment_group,
        create_assignment,
        cleanup_all,
    ):
        mock_get.return_value = canvas_assignment_groups_response
        canvas_user = create_canvas_user(username="user")
        course = create_canvas_course(canvas_user=canvas_user)
        assignment_group = create_assignment_group(
            course=course,
            name="Сабаққа қатысу/Посещаемость",
            canvas_assignment_group_id=14761,
        )
        assignment = create_assignment(
            assignment_group=assignment_group,
            name="target assignment",
            canvas_assignment_id=67301,
        )
        canvas_auth_data = auth_dto.CanvasAuthData(**sample_data.canvas_auth_data)
        await canvas_assignment_service.get_attendance_assignment_group(
            web_id=course.web_id, canvas_auth_data=canvas_auth_data
        )
        with assignment_repo.session():
            assignments = assignment_repo.list_all()
            assert len(assignments) == 2
            for assignment in assignments:
                assert assignment.canvas_assignment_id in set([67301, 68220])
                assert assignment.assignment_group_id == 1
                assert assignment.name is not None

    @pytest.mark.asyncio
    @patch("aiohttp.ClientSession.get")
    async def test_get_attendance_assignment_group_should_return_valid_dto(
        self,
        mock_get,
        canvas_assignment_service,
        create_canvas_user,
        create_canvas_course,
        canvas_assignment_groups_response,
        cleanup_all,
    ):
        mock_get.return_value = canvas_assignment_groups_response
        canvas_user = create_canvas_user(username="user")
        course = create_canvas_course(canvas_user=canvas_user)
        canvas_auth_data = auth_dto.CanvasAuthData(**sample_data.canvas_auth_data)
        result = await canvas_assignment_service.get_attendance_assignment_group(
            web_id=course.web_id, canvas_auth_data=canvas_auth_data
        )
        assert result.model_dump() == {
            "id": 1,
            "web_id": "web-id-4",
            "group_weight": 0,
            "name": "Сабаққа қатысу/Посещаемость",
            "canvas_assignment_group_id": 14761,
            "assignments": [
                {
                    "id": 1,
                    "web_id": "web-id-5",
                    "canvas_assignment_id": 67301,
                    "name": "Att-W1-1",
                    "assignment_group_id": 1,
                },
                {
                    "id": 2,
                    "web_id": "web-id-6",
                    "canvas_assignment_id": 68220,
                    "name": "Att-w2-2",
                    "assignment_group_id": 1,
                },
            ],
        }

    @pytest.mark.asyncio
    @patch("aiohttp.ClientSession.get")
    async def test_get_attendance_assignment_group_should_raise_when_no_assignment_groups_from_canvas(
        self,
        mock_get,
        canvas_assignment_service,
        create_canvas_user,
        create_canvas_course,
        canvas_assignment_groups_empty_response,
        cleanup_all,
    ):
        mock_get.return_value = canvas_assignment_groups_empty_response
        canvas_user = create_canvas_user(username="user")
        course = create_canvas_course(canvas_user=canvas_user)
        canvas_auth_data = auth_dto.CanvasAuthData(**sample_data.canvas_auth_data)
        with pytest.raises(CanvasAPIError) as exc:
            await canvas_assignment_service.get_attendance_assignment_group(
                web_id=course.web_id, canvas_auth_data=canvas_auth_data
            )

        assert (
            exc.value.message
            == "_err_message_no_attendance_assignment_groups_for_this_course:web-id-3"
        )
