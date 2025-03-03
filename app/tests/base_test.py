import uuid
from http.cookies import SimpleCookie
from unittest.mock import AsyncMock, MagicMock

import pytest
import shortuuid

from app_config import AppConfig, get_app_config
from src.models import CanvasUser, FileRecord, User
from src.models.canvas_course import CanvasCourse
from src.repositories.canvas_course_repo import CanvasCourseRepo
from src.repositories.canvas_user_repo import CanvasUserRepo
from src.repositories.file_fs_repo import FileFsRepo
from src.repositories.file_record_repo import FileRecordRepo
from src.repositories.user_repo import UserRepo
from src.services.auth_service import AuthService
from tests.fixtures import sample_data
from tests.fixtures.db_fixtures import DbTest
from tests.fixtures.file_fixtures import FileFixtures


class BaseTest(DbTest, FileFixtures):

    @pytest.fixture
    def app_config(self) -> AppConfig:
        return get_app_config()

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
    def auth_service(self, user_repo, canvas_user_repo):
        return AuthService(user_repo=user_repo, canvas_user_repo=canvas_user_repo)

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
    def cleanup_all(self, cleanup_file_records, cleanup_users, cleanup_canvas_users):
        pass

    @pytest.fixture
    def cleanup_file_records(self, file_record_repo):
        yield
        with file_record_repo.session():
            file_record_repo.query(FileRecord).delete()

    @pytest.fixture
    def cleanup_users(self, user_repo):
        yield
        with user_repo.session():
            user_repo.query(User).delete()

    @pytest.fixture
    def cleanup_canvas_users(self, canvas_user_repo):
        yield
        with canvas_user_repo.session():
            canvas_user_repo.query(CanvasUser).delete()

    @pytest.fixture
    def cleanup_canvas_courses(self, canvas_course_repo):
        yield
        with canvas_course_repo.session():
            canvas_course_repo.query(CanvasCourse).delete()

    @pytest.fixture
    def sample_user(self) -> User:
        def _gen(
            username: str = "test@gmail.com", password="test-pwd", web_id="web-id-1"
        ):
            user = User(username=username, web_id=web_id)
            user.set_password(password=password)
            return user

        return _gen

    @pytest.fixture
    def create_user(self, sample_user, user_repo) -> User:
        def _gen(username="test@gmail.com", password="test-pwd", web_id="web-id-1"):
            user = sample_user(username=username, password=password, web_id=web_id)
            with user_repo.session():
                user = user_repo.save_or_update(user)
            return user

        return _gen

    @pytest.fixture
    def sample_canvas_user(self, create_user):
        def _gen(
            username="test@gmail.com",
            password="test-pwd",
            web_id="web-id-1",
            canvas_id="canvas-id-1",
        ):
            user = create_user(username=username, password=password, web_id=web_id)
            canvas_user = CanvasUser(
                user_id=user.id,
                canvas_id=canvas_id,
                username=f"canvas_{user.username}",
                web_id=web_id,
            )
            canvas_user.set_password(password=password)
            return canvas_user

        return _gen

    @pytest.fixture
    def create_canvas_user(self, sample_canvas_user, canvas_user_repo) -> CanvasUser:
        def _gen(username="test@gmail.com", password="test-pwd", web_id="web-id-1"):
            user = sample_canvas_user(
                username=username, password=password, web_id=web_id
            )
            with canvas_user_repo.session():
                user = canvas_user_repo.save_or_update(user)
            return user

        return _gen

    @pytest.fixture
    def canvas_ok_response(self):
        mock_response = AsyncMock()
        mock_response.__aenter__.return_value = mock_response
        mock_response.__aexit__.return_value = None

        mock_cookies = SimpleCookie()
        for key, value in sample_data.canvas_ok_data.items():
            mock_cookies[key] = value

        mock_response.cookies = MagicMock()
        mock_response.cookies.items.return_value = mock_cookies.items()

        return mock_response
