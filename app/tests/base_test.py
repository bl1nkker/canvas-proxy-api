import uuid
from http.cookies import SimpleCookie
from unittest.mock import AsyncMock, MagicMock

import pytest
import shortuuid
from sqlalchemy.sql import text

from app_config import AppConfig, get_app_config
from db.base_repo import BaseRepo
from src.enums.attendance_status import AttendanceStatus
from src.enums.attendance_value import AttendanceValue
from src.models import CanvasUser, FileRecord, User
from src.models.assignment import Assignment
from src.models.attendance import Attendance
from src.models.canvas_course import CanvasCourse
from src.models.enrollment import Enrollment
from src.models.student import Student
from src.repositories.assignment_repo import AssignmentRepo
from src.repositories.attendance_repo import AttendanceRepo
from src.repositories.canvas_course_repo import CanvasCourseRepo
from src.repositories.canvas_user_repo import CanvasUserRepo
from src.repositories.enrollment_repo import EnrollmentRepo
from src.repositories.file_fs_repo import FileFsRepo
from src.repositories.file_record_repo import FileRecordRepo
from src.repositories.student_repo import StudentRepo
from src.repositories.student_vector_repo import StudentVectorRepo
from src.repositories.user_repo import UserRepo
from src.services.attendance_service import AttendanceService
from src.services.auth_service import AuthService
from src.services.canvas_course_service import CanvasCourseService
from src.services.student_service import StudentService
from src.services.upload_service import UploadService
from tests.fixtures import sample_data
from tests.fixtures.db_fixtures import DbTest
from tests.fixtures.file_fixtures import FileFixtures


class BaseTest(DbTest, FileFixtures):

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
    def student_vector_repo(self, db_session):
        return StudentVectorRepo(db_session)

    @pytest.fixture
    def auth_service(self, user_repo, canvas_user_repo):
        return AuthService(user_repo=user_repo, canvas_user_repo=canvas_user_repo)

    @pytest.fixture
    def student_service(
        self,
        student_repo,
        enrollment_repo,
        canvas_course_repo,
        student_vector_repo,
        upload_service,
    ):
        return StudentService(
            student_repo=student_repo,
            enrollment_repo=enrollment_repo,
            canvas_course_repo=canvas_course_repo,
            student_vector_repo=student_vector_repo,
            upload_service=upload_service,
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
        self, attendance_repo, student_repo, assignment_repo, canvas_course_repo
    ):
        return AttendanceService(
            attendance_repo=attendance_repo,
            student_repo=student_repo,
            assignment_repo=assignment_repo,
            canvas_course_repo=canvas_course_repo,
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
            Assignment,
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
                    f"ALTER SEQUENCE {mdl.__table_args__['schema']}.{mdl.__tablename__}_id_seq RESTART WITH 1"
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
        ):
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
            canvas_id=1,
        ):
            user = sample_canvas_user(
                username=username, password=password, canvas_id=canvas_id
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
    def sample_attendance(self):
        def _gen(
            student,
            course,
            assignment,
            status=AttendanceStatus.INITIATED,
            value=AttendanceValue.COMPLETE,
        ):
            att = Attendance(
                course_id=course.id,
                student_id=student.id,
                assignment_id=assignment.id,
                status=status,
                value=value,
            )
            return att

        return _gen

    @pytest.fixture
    def create_attendance(self, sample_attendance, attendance_repo) -> CanvasCourse:
        def _gen(
            student,
            course,
            assignment,
            status=AttendanceStatus.INITIATED,
            value=AttendanceValue.COMPLETE,
        ):
            att = sample_attendance(
                course=course,
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
        def _gen(name, course, canvas_assignment_id=1):
            assignment = Assignment(
                web_id=shortuuid.uuid(),
                course_id=course.id,
                name=name,
                canvas_assignment_id=canvas_assignment_id,
            )
            return assignment

        return _gen

    @pytest.fixture
    def create_assignment(self, sample_assignment, assignment_repo) -> CanvasCourse:
        def _gen(name, course, canvas_assignment_id=1):
            assignment = sample_assignment(
                name=name,
                course=course,
                canvas_assignment_id=canvas_assignment_id,
            )
            with assignment_repo.session():
                assignment = assignment_repo.save_or_update(assignment)
            return assignment

        return _gen

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
