import pytest

from src.enums.attendance_status import AttendanceStatus
from tests.base_test import BaseTest


class TestSourceDataLoadService(BaseTest):

    @pytest.mark.asyncio
    async def test_load_data_from_canvas_should_load_courses(
        self,
        source_data_load_service,
        create_user,
        create_canvas_user,
        canvas_course_repo,
        mock_aiohttp_get,
        mock_aiohttp_post,
        cleanup_all,
    ):
        user = create_user()
        canvas_user = create_canvas_user(user=user)
        await source_data_load_service.load_data_from_canvas(user_id=user.id)
        with canvas_course_repo.session():
            courses = canvas_course_repo.list_all()
            assert len(courses) == 2
            for course in courses:
                assert course.canvas_user == canvas_user

    @pytest.mark.asyncio
    async def test_load_data_from_canvas_should_not_create_existing_courses(
        self,
        mock_aiohttp_get,
        mock_aiohttp_post,
        source_data_load_service,
        create_user,
        create_canvas_user,
        create_canvas_course,
        canvas_course_repo,
        cleanup_all,
    ):
        user = create_user()
        canvas_user = create_canvas_user(user=user)
        course = create_canvas_course(canvas_user=canvas_user, canvas_course_id=2998)
        await source_data_load_service.load_data_from_canvas(user_id=user.id)
        with canvas_course_repo.session():
            courses = canvas_course_repo.list_all()
            assert len(courses) == 2
            for course in courses:
                assert course.canvas_user == canvas_user

    @pytest.mark.asyncio
    async def test_load_data_from_canvas_should_load_students(
        self,
        source_data_load_service,
        create_user,
        create_canvas_user,
        student_repo,
        mock_aiohttp_get,
        mock_aiohttp_post,
        cleanup_all,
    ):
        user = create_user()
        create_canvas_user(user=user)
        await source_data_load_service.load_data_from_canvas(user_id=user.id)
        with student_repo.session():
            students = student_repo.list_all()
            assert len(students) == 2

    @pytest.mark.asyncio
    async def test_load_data_from_canvas_should_not_create_existing_students(
        self,
        source_data_load_service,
        create_user,
        create_canvas_user,
        student_repo,
        create_student,
        mock_aiohttp_get,
        mock_aiohttp_post,
        cleanup_all,
    ):
        user = create_user()
        create_canvas_user(user=user)
        create_student(canvas_user_id=18728)
        await source_data_load_service.load_data_from_canvas(user_id=user.id)
        with student_repo.session():
            students = student_repo.list_all()
            assert len(students) == 2

    @pytest.mark.asyncio
    async def test_load_data_from_canvas_should_create_enrollment_for_each_student(
        self,
        source_data_load_service,
        create_user,
        create_canvas_user,
        enrollment_repo,
        mock_aiohttp_get,
        mock_aiohttp_post,
        cleanup_all,
    ):
        user = create_user()
        create_canvas_user(user=user)
        await source_data_load_service.load_data_from_canvas(user_id=user.id)
        with enrollment_repo.session():
            enrollments = enrollment_repo.list_all()
            assert len(enrollments) == 2

    @pytest.mark.asyncio
    async def test_load_data_from_canvas_should_create_enrollment_for_existing_students(
        self,
        source_data_load_service,
        create_user,
        create_canvas_user,
        enrollment_repo,
        create_student,
        mock_aiohttp_get,
        mock_aiohttp_post,
        cleanup_all,
    ):
        user = create_user()
        create_canvas_user(user=user)
        create_student(canvas_user_id=18728)
        await source_data_load_service.load_data_from_canvas(user_id=user.id)
        with enrollment_repo.session():
            enrollments = enrollment_repo.list_all()
            assert len(enrollments) == 2

    @pytest.mark.asyncio
    async def test_load_data_from_canvas_should_not_create_existing_enrollments(
        self,
        source_data_load_service,
        create_user,
        create_canvas_user,
        enrollment_repo,
        create_canvas_course,
        create_enrollment,
        create_student,
        mock_aiohttp_get,
        mock_aiohttp_post,
        cleanup_all,
    ):
        user = create_user()
        canvas_user = create_canvas_user(user=user)
        course = create_canvas_course(canvas_user=canvas_user, canvas_course_id=2997)
        student = create_student(canvas_user_id=18728)
        create_enrollment(course=course, student=student)
        await source_data_load_service.load_data_from_canvas(user_id=user.id)
        with enrollment_repo.session():
            enrollments = enrollment_repo.list_all()
            assert len(enrollments) == 2

    @pytest.mark.asyncio
    async def test_load_data_from_canvas_should_load_attendance_assignment_group_for_each_course(
        self,
        source_data_load_service,
        create_user,
        create_canvas_user,
        assignment_group_repo,
        create_canvas_course,
        mock_aiohttp_get,
        mock_aiohttp_post,
        cleanup_all,
    ):
        user = create_user()
        canvas_user = create_canvas_user(user=user)
        course = create_canvas_course(canvas_user=canvas_user, canvas_course_id=2997)
        await source_data_load_service.load_data_from_canvas(user_id=user.id)
        with assignment_group_repo.session():
            assignment_groups = assignment_group_repo.list_all()
            assert len(assignment_groups) == 1
            assert assignment_groups[0].course_id == course.id
            assert assignment_groups[0].name == "Сабаққа қатысу/Посещаемость"
            assert assignment_groups[0].group_weight == 0
            assert assignment_groups[0].course_id == course.id
            assert assignment_groups[0].canvas_assignment_group_id == 14761

    @pytest.mark.asyncio
    async def test_load_data_from_canvas_should_not_create_existing_attendance_assignment_group(
        self,
        source_data_load_service,
        create_user,
        create_canvas_user,
        assignment_group_repo,
        create_canvas_course,
        create_assignment_group,
        mock_aiohttp_get,
        mock_aiohttp_post,
        cleanup_all,
    ):
        user = create_user()
        canvas_user = create_canvas_user(user=user)
        course = create_canvas_course(canvas_user=canvas_user, canvas_course_id=2997)
        create_assignment_group(
            course=course,
            name="Сабаққа қатысу/Посещаемость",
            canvas_assignment_group_id=14761,
        )
        await source_data_load_service.load_data_from_canvas(user_id=user.id)
        with assignment_group_repo.session():
            assignment_groups = assignment_group_repo.list_all()
            assert len(assignment_groups) == 1
            assert assignment_groups[0].course_id == course.id
            assert assignment_groups[0].name == "Сабаққа қатысу/Посещаемость"
            assert assignment_groups[0].group_weight == 10
            assert assignment_groups[0].course_id == course.id
            assert assignment_groups[0].canvas_assignment_group_id == 14761

    @pytest.mark.asyncio
    async def test_load_data_from_canvas_should_load_assignments(
        self,
        source_data_load_service,
        create_user,
        create_canvas_user,
        assignment_repo,
        mock_aiohttp_get,
        mock_aiohttp_post,
        cleanup_all,
    ):
        user = create_user()
        create_canvas_user(user=user)
        await source_data_load_service.load_data_from_canvas(user_id=user.id)
        with assignment_repo.session():
            assignments = assignment_repo.list_all()
            assert len(assignments) == 2
            for assignment in assignments:
                assert assignment.canvas_assignment_id in set([67301, 68220])
                assert assignment.assignment_group_id == 1
                assert assignment.name is not None

    @pytest.mark.asyncio
    async def test_load_data_from_canvas_should_not_create_existing_assignments(
        self,
        source_data_load_service,
        create_user,
        create_canvas_user,
        create_canvas_course,
        create_assignment_group,
        create_assignment,
        assignment_repo,
        mock_aiohttp_get,
        mock_aiohttp_post,
        cleanup_all,
    ):
        user = create_user()
        canvas_user = create_canvas_user(user=user)
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
        await source_data_load_service.load_data_from_canvas(user_id=user.id)
        with assignment_repo.session():
            assignments = assignment_repo.list_all()
            assert len(assignments) == 2
            for assignment in assignments:
                assert assignment.canvas_assignment_id in set([67301, 68220])
                assert assignment.assignment_group_id == 1
                assert assignment.name is not None

    @pytest.mark.asyncio
    async def test_load_data_from_canvas_should_load_attendances_for_each_assignment(
        self,
        source_data_load_service,
        create_user,
        create_canvas_user,
        attendance_repo,
        mock_aiohttp_get,
        mock_aiohttp_post,
        cleanup_all,
    ):
        user = create_user()
        create_canvas_user(user=user)
        await source_data_load_service.load_data_from_canvas(user_id=user.id)
        with attendance_repo.session():
            atts = attendance_repo.list_all()
            assert len(atts) == 4
            for att in atts:
                assert att.status == AttendanceStatus.COMPLETED
                assert att.value is not None

    def test_load_data_from_canvas_should_not_create_existing_attendances(
        self,
    ):
        pass
