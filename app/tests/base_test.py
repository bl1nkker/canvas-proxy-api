import uuid
from http.cookies import SimpleCookie
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import shortuuid
from sqlalchemy.sql import text

from app_config import AppConfig, get_app_config
from db.base_repo import BaseRepo
from src.enums.attendance_status import AttendanceStatus
from src.enums.attendance_value import AttendanceValue
from src.models import CanvasUser, FileRecord, User
from src.models.assignment import Assignment
from src.models.assignment_group import AssignmentGroup
from src.models.attendance import Attendance
from src.models.canvas_course import CanvasCourse
from src.models.enrollment import Enrollment
from src.models.recognition_history import RecognitionHistory
from src.models.student import Student
from src.models.student_vector import StudentVector
from src.repositories.assignment_group_repo import AssignmentGroupRepo
from src.repositories.assignment_repo import AssignmentRepo
from src.repositories.attendance_repo import AttendanceRepo
from src.repositories.canvas_course_repo import CanvasCourseRepo
from src.repositories.canvas_user_repo import CanvasUserRepo
from src.repositories.enrollment_repo import EnrollmentRepo
from src.repositories.file_fs_repo import FileFsRepo
from src.repositories.file_record_repo import FileRecordRepo
from src.repositories.recognition_history_repo import RecognitionHistoryRepo
from src.repositories.student_repo import StudentRepo
from src.repositories.student_vector_repo import StudentVectorRepo
from src.repositories.user_repo import UserRepo
from src.services.assignment_service import AssignmentService
from src.services.attendance_process_service import AttendanceProcessService
from src.services.attendance_service import AttendanceService
from src.services.auth_service import AuthService
from src.services.canvas_course_service import CanvasCourseService
from src.services.recognition_history_service import RecognitionHistoryService
from src.services.source_data_load_queue_service import SourceDataLoadQueueService
from src.services.source_data_load_service import SourceDataLoadService
from src.services.student_service import StudentService
from src.services.upload_service import UploadService
from tests.fixtures import sample_data
from tests.fixtures.broker_fixtures import BrokerTest
from tests.fixtures.db_fixtures import DbTest
from tests.fixtures.file_fixtures import FileFixtures


class BaseTest(DbTest, FileFixtures, BrokerTest):

    @pytest.fixture
    def app_config(self) -> AppConfig:
        return get_app_config()

    @pytest.fixture
    def base_repo(self, db_session):
        return BaseRepo(db_session)

    @pytest.fixture
    def file_record_repo(self, db_session):
        return FileRecordRepo(db_session)

    @pytest.fixture
    def canvas_course_repo(self, db_session):
        return CanvasCourseRepo(db_session)

    @pytest.fixture
    def file_fs_repo(self):
        return FileFsRepo()

    @pytest.fixture
    def user_repo(self, db_session):
        return UserRepo(db_session)

    @pytest.fixture
    def canvas_user_repo(self, db_session):
        return CanvasUserRepo(db_session)

    @pytest.fixture
    def enrollment_repo(self, db_session):
        return EnrollmentRepo(db_session)

    @pytest.fixture
    def student_repo(self, db_session):
        return StudentRepo(db_session)

    @pytest.fixture
    def attendance_repo(self, db_session):
        return AttendanceRepo(db_session)

    @pytest.fixture
    def assignment_repo(self, db_session):
        return AssignmentRepo(db_session)

    @pytest.fixture
    def assignment_group_repo(self, db_session):
        return AssignmentGroupRepo(db_session)

    @pytest.fixture
    def student_vector_repo(self, db_session):
        return StudentVectorRepo(db_session)

    @pytest.fixture
    def recognition_history_repo(self, db_session):
        return RecognitionHistoryRepo(db_session)

    @pytest.fixture
    def source_data_load_queue_service(self, broker_client):
        return SourceDataLoadQueueService(redis_client=broker_client)

    @pytest.fixture
    def recognition_history_service(self, recognition_history_repo):
        return RecognitionHistoryService(
            recognition_history_repo=recognition_history_repo
        )

    @pytest.fixture
    def auth_service(self, user_repo, canvas_user_repo, source_data_load_queue_service):
        return AuthService(
            user_repo=user_repo,
            canvas_user_repo=canvas_user_repo,
            source_data_load_queue_service=source_data_load_queue_service,
        )

    @pytest.fixture
    def student_service(
        self,
        student_repo,
        enrollment_repo,
        canvas_course_repo,
        student_vector_repo,
        upload_service,
        recognition_history_service,
    ):
        return StudentService(
            student_repo=student_repo,
            enrollment_repo=enrollment_repo,
            canvas_course_repo=canvas_course_repo,
            student_vector_repo=student_vector_repo,
            upload_service=upload_service,
            recognition_history_service=recognition_history_service,
        )

    @pytest.fixture
    def source_data_load_service(
        self,
        user_repo,
        canvas_user_repo,
        canvas_course_repo,
        student_repo,
        enrollment_repo,
        assignment_group_repo,
        assignment_repo,
        attendance_repo,
    ):
        return SourceDataLoadService(
            user_repo=user_repo,
            enrollment_repo=enrollment_repo,
            student_repo=student_repo,
            canvas_user_repo=canvas_user_repo,
            canvas_course_repo=canvas_course_repo,
            assignment_group_repo=assignment_group_repo,
            assignment_repo=assignment_repo,
            attendance_repo=attendance_repo,
        )

    @pytest.fixture
    def canvas_course_service(self, canvas_course_repo, canvas_user_repo):
        return CanvasCourseService(
            canvas_course_repo=canvas_course_repo, canvas_user_repo=canvas_user_repo
        )

    @pytest.fixture
    def upload_service(self, file_record_repo, file_fs_repo):
        return UploadService(
            file_fs_repo=file_fs_repo, file_record_repo=file_record_repo
        )

    @pytest.fixture
    def attendance_service(
        self,
        attendance_repo,
        student_repo,
        assignment_repo,
        canvas_course_repo,
        student_service,
    ):
        return AttendanceService(
            attendance_repo=attendance_repo,
            student_repo=student_repo,
            assignment_repo=assignment_repo,
            canvas_course_repo=canvas_course_repo,
            student_service=student_service,
        )

    @pytest.fixture
    def attendance_process_service(
        self, attendance_repo, student_repo, auth_service, canvas_course_repo
    ):
        return AttendanceProcessService(
            student_repo=student_repo,
            attendance_repo=attendance_repo,
            auth_service=auth_service,
            canvas_course_repo=canvas_course_repo,
        )

    @pytest.fixture
    def assignment_service(
        self,
        attendance_service,
        canvas_course_repo,
        assignment_repo,
        assignment_group_repo,
    ):
        return AssignmentService(
            assignment_group_repo=assignment_group_repo,
            attendance_service=attendance_service,
            canvas_course_repo=canvas_course_repo,
            assignment_repo=assignment_repo,
        )

    @pytest.fixture
    def patch_uuid(self, monkeypatch):
        def uuid_gen():
            i = 1
            while True:
                yield i
                i += 1

        gen = uuid_gen()
        monkeypatch.setattr(uuid, "uuid4", lambda: f"some-uuid-{next(gen)}")

    @pytest.fixture
    def patch_shortuuid(self, monkeypatch):
        def web_id_gen():
            i = 1
            while True:
                yield f"web-id-{i}"
                i += 1

        gen = web_id_gen()

        def web_id():
            return next(gen)

        monkeypatch.setattr(shortuuid, "uuid", web_id)

    @pytest.fixture
    def cleanup_all(self, base_repo):
        # order matters
        models = [
            Enrollment,
            Attendance,
            RecognitionHistory,
            Assignment,
            AssignmentGroup,
            StudentVector,
            Student,
            CanvasUser,
            CanvasCourse,
            User,
            FileRecord,
        ]
        yield
        with base_repo.session() as session:
            for mdl in models:
                session.query(mdl).delete()
                stmt = text(
                    f"ALTER SEQUENCE app.{mdl.__tablename__}_id_seq RESTART WITH 1"
                )
                session.execute(stmt)

    @pytest.fixture
    def sample_user(self, patch_shortuuid) -> User:
        def _gen(username: str = "test@gmail.com", password="test-pwd"):
            user = User(username=username, web_id=shortuuid.uuid())
            user.set_password(password=password)
            return user

        return _gen

    @pytest.fixture
    def create_user(self, sample_user, user_repo) -> User:
        def _gen(username="test@gmail.com", password="test-pwd"):
            user = sample_user(username=username, password=password)
            with user_repo.session():
                user = user_repo.save_or_update(user)
            return user

        return _gen

    @pytest.fixture
    def sample_canvas_user(self, create_user, patch_shortuuid):
        def _gen(
            username="test@gmail.com",
            password="test-pwd",
            canvas_id="canvas-id-1",
            user=None,
        ):
            if user is None:
                user = create_user(username=username, password=password)
            canvas_user = CanvasUser(
                user_id=user.id,
                canvas_id=canvas_id,
                username=f"canvas_{user.username}",
                web_id=shortuuid.uuid(),
            )
            canvas_user.set_password(password=password)
            return canvas_user

        return _gen

    @pytest.fixture
    def create_canvas_user(self, sample_canvas_user, canvas_user_repo) -> CanvasUser:
        def _gen(
            username="test@gmail.com",
            password="test-pwd",
            user=None,
            canvas_id=1,
        ):
            user = sample_canvas_user(
                username=username, password=password, canvas_id=canvas_id, user=user
            )
            with canvas_user_repo.session():
                user = canvas_user_repo.save_or_update(user)
            return user

        return _gen

    @pytest.fixture
    def sample_canvas_course(self, patch_shortuuid):
        def _gen(
            canvas_user,
            long_name="test-long_name",
            canvas_course_id=228337,
        ):
            course = CanvasCourse(
                web_id=shortuuid.uuid(),
                long_name=long_name,
                short_name="test-short_name",
                original_name="test-original_name",
                course_code="code-123",
                canvas_course_id=canvas_course_id,
                canvas_user_id=canvas_user.id,
            )
            return course

        return _gen

    @pytest.fixture
    def create_canvas_course(
        self, sample_canvas_course, canvas_course_repo, create_canvas_user
    ) -> CanvasCourse:
        def _gen(
            canvas_user,
            long_name="test-long_name",
            canvas_course_id=228337,
        ):
            course = sample_canvas_course(
                long_name=long_name,
                canvas_course_id=canvas_course_id,
                canvas_user=canvas_user,
            )
            with canvas_course_repo.session():
                course = canvas_course_repo.save_or_update(course)
            return course

        return _gen

    @pytest.fixture
    def sample_enrollment(self, patch_shortuuid):
        def _gen(student, course):
            enrollment = Enrollment(
                web_id=shortuuid.uuid(), student_id=student.id, course_id=course.id
            )
            return enrollment

        return _gen

    @pytest.fixture
    def create_enrollment(self, sample_enrollment, enrollment_repo) -> CanvasCourse:
        def _gen(course, student):
            enrollment = sample_enrollment(course=course, student=student)
            with enrollment_repo.session():
                enrollment = enrollment_repo.save_or_update(enrollment)
            return enrollment

        return _gen

    @pytest.fixture
    def sample_student(self, patch_shortuuid):
        def _gen(
            firstname="Test",
            lastname="Testname",
            email="test@gmail.com",
            canvas_user_id=1,
        ):
            student = Student(
                web_id=shortuuid.uuid(),
                name=f"{firstname} {lastname}",
                email=email,
                canvas_user_id=canvas_user_id,
            )
            return student

        return _gen

    @pytest.fixture
    def create_student(self, sample_student, student_repo) -> CanvasCourse:
        def _gen(
            firstname="Test",
            lastname="Testname",
            email="test@gmail.com",
            canvas_user_id=1,
        ):
            student = sample_student(
                firstname=firstname,
                lastname=lastname,
                email=email,
                canvas_user_id=canvas_user_id,
            )
            with student_repo.session():
                student = student_repo.save_or_update(student)
            return student

        return _gen

    @pytest.fixture
    def sample_student_vector(self, patch_shortuuid):
        def _gen(student, embedding=[1.1] * 512):
            student = StudentVector(
                web_id=shortuuid.uuid(), student_id=student.id, embedding=embedding
            )
            return student

        return _gen

    @pytest.fixture
    def create_student_vector(
        self, sample_student_vector, student_vector_repo
    ) -> CanvasCourse:
        def _gen(student, embedding=[1.1] * 512):
            vector = sample_student_vector(student=student, embedding=embedding)
            with student_vector_repo.session():
                vector = student_vector_repo.save_or_update(vector)
            return vector

        return _gen

    @pytest.fixture
    def sample_recognition_history(self, patch_shortuuid):
        def _gen(
            student,
            image_file_json=None,
            recognition_details_json=None,
        ):
            student = RecognitionHistory(
                web_id=shortuuid.uuid(),
                student_id=student.id,
                image_file_json=image_file_json,
                recognition_details_json=recognition_details_json,
            )
            return student

        return _gen

    @pytest.fixture
    def create_recognition_history(
        self, sample_recognition_history, recognition_history_repo
    ) -> CanvasCourse:
        def _gen(
            student,
            image_file_json=None,
            recognition_details_json=None,
        ):
            vector = sample_recognition_history(
                student=student,
                image_file_json=image_file_json,
                recognition_details_json=recognition_details_json,
            )
            with recognition_history_repo.session():
                vector = recognition_history_repo.save_or_update(vector)
            return vector

        return _gen

    @pytest.fixture
    def sample_attendance(self, patch_shortuuid):
        def _gen(
            student,
            assignment,
            status=AttendanceStatus.INITIATED,
            value=AttendanceValue.COMPLETE,
        ):
            att = Attendance(
                web_id=shortuuid.uuid(),
                student_id=student.id,
                assignment_id=assignment.id,
                status=status,
                value=value,
                failed=False,
            )
            return att

        return _gen

    @pytest.fixture
    def create_attendance(self, sample_attendance, attendance_repo) -> CanvasCourse:
        def _gen(
            student,
            assignment,
            status=AttendanceStatus.INITIATED,
            value=AttendanceValue.COMPLETE,
        ):
            att = sample_attendance(
                student=student,
                assignment=assignment,
                status=status,
                value=value,
            )
            with attendance_repo.session():
                att = attendance_repo.save_or_update(att)
            return att

        return _gen

    @pytest.fixture
    def sample_assignment(self, patch_shortuuid):
        def _gen(name, assignment_group, canvas_assignment_id=1):
            assignment = Assignment(
                web_id=shortuuid.uuid(),
                assignment_group_id=assignment_group.id,
                name=name,
                canvas_assignment_id=canvas_assignment_id,
            )
            return assignment

        return _gen

    @pytest.fixture
    def create_assignment(self, sample_assignment, assignment_repo) -> CanvasCourse:
        def _gen(name, assignment_group, canvas_assignment_id=1):
            assignment = sample_assignment(
                name=name,
                assignment_group=assignment_group,
                canvas_assignment_id=canvas_assignment_id,
            )
            with assignment_repo.session():
                assignment = assignment_repo.save_or_update(assignment)
            return assignment

        return _gen

    @pytest.fixture
    def sample_assignment_group(self, patch_shortuuid):
        def _gen(name, course, group_weight=10, canvas_assignment_group_id=1):
            assignment = AssignmentGroup(
                web_id=shortuuid.uuid(),
                name=name,
                group_weight=group_weight,
                course_id=course.id,
                canvas_assignment_group_id=canvas_assignment_group_id,
            )
            return assignment

        return _gen

    @pytest.fixture
    def create_assignment_group(
        self, sample_assignment_group, assignment_group_repo
    ) -> CanvasCourse:
        def _gen(name, course, group_weight=10, canvas_assignment_group_id=1):
            assignment_group = sample_assignment_group(
                name=name,
                course=course,
                group_weight=group_weight,
                canvas_assignment_group_id=canvas_assignment_group_id,
            )
            with assignment_group_repo.session():
                assignment_group = assignment_group_repo.save_or_update(
                    assignment_group
                )
            return assignment_group

        return _gen

    @pytest.fixture
    def mock_aiohttp_get(
        self,
        canvas_ok_response,
        canvas_course_ok_response,
        canvas_get_students_ok_response,
        canvas_assignment_groups_response,
        canvas_get_student_attendances_ok_response,
        canvas_assignment_secure_params_response,
    ):
        def mocked_get(url, *args, **kwargs):
            if "/login/canvas" in url:
                return canvas_ok_response
            elif "/dashboard/dashboard_cards" in url:
                return canvas_course_ok_response
            elif "/users?include_inactive=true" in url:
                return canvas_get_students_ok_response
            elif "/students/submissions" in url:
                return canvas_get_student_attendances_ok_response
            elif "/assignment_groups" in url:
                return canvas_assignment_groups_response
            elif "/assignments/new?" in url:
                return canvas_assignment_secure_params_response
            else:
                raise NotImplementedError

        with patch("aiohttp.ClientSession.get", side_effect=mocked_get) as mock:
            yield mock

    @pytest.fixture
    def mock_aiohttp_post(self, canvas_ok_response, canvas_create_assignment_response):

        def mocked_post(url, *args, **kwargs):
            if "/login/canvas" in url:
                return canvas_ok_response
            elif "/assignments" in url:
                return canvas_create_assignment_response
            else:
                raise NotImplementedError

        with patch("aiohttp.ClientSession.post", side_effect=mocked_post) as mock:
            yield mock

    @pytest.fixture
    def canvas_ok_response(self):
        mock_response = AsyncMock()
        mock_response.__aenter__.return_value = mock_response
        mock_response.__aexit__.return_value = None

        mock_cookies = SimpleCookie()
        for key, value in sample_data.canvas_auth_data.items():
            mock_cookies[key] = value

        mock_response.cookies = MagicMock()
        mock_response.cookies.items.return_value = mock_cookies.items()

        return mock_response

    @pytest.fixture
    def canvas_course_ok_response(self):
        mock_response = AsyncMock()
        mock_response.__aenter__.return_value = mock_response
        mock_response.__aexit__.return_value = None
        mock_response.json.return_value = sample_data.canvas_courses_data

        return mock_response

    @pytest.fixture
    def canvas_get_students_ok_response(self):
        mock_response = AsyncMock()
        mock_response.__aenter__.return_value = mock_response
        mock_response.__aexit__.return_value = None
        mock_response.json.return_value = sample_data.canvas_get_students_response

        return mock_response

    @pytest.fixture
    def canvas_get_student_attendances_ok_response(self):
        mock_response = AsyncMock()
        mock_response.__aenter__.return_value = mock_response
        mock_response.__aexit__.return_value = None
        mock_response.json.return_value = (
            sample_data.canvas_get_student_attendances_response
        )

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
    def canvas_assignment_secure_params_response(self):
        mock_response = AsyncMock()
        mock_response.__aenter__.return_value = mock_response
        mock_response.__aexit__.return_value = None
        mock_response.text.return_value = (
            sample_data.canvas_assignment_secure_params_response
        )
        return mock_response

    @pytest.fixture
    def canvas_create_assignment_response(self):
        mock_response = AsyncMock()
        mock_response.__aenter__.return_value = mock_response
        mock_response.__aexit__.return_value = None
        mock_response.json.return_value = sample_data.canvas_create_assignment_response
        return mock_response
