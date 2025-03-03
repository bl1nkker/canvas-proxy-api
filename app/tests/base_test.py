import uuid

import pytest
import shortuuid

from src.models import CanvasUser, FileRecord, User
from src.repositories.canvas_repo import CanvasUserRepo
from src.repositories.file_fs_repo import FileFsRepo
from src.repositories.file_record_repo import FileRecordRepo
from src.repositories.user_repo import UserRepo
from tests.fixtures.db_fixtures import DbTest
from tests.fixtures.file_fixtures import FileFixtures


class BaseTest(DbTest, FileFixtures):

    @pytest.fixture
    def file_record_repo(self, db_session):
        return FileRecordRepo(db_session)

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
    def sample_user(self) -> User:
        def _gen(username: str = "test@gmail.com", web_id="web-id-1"):
            user = User(username=username, web_id=web_id)
            user.set_password(password="test-pwd")
            return user

        return _gen
