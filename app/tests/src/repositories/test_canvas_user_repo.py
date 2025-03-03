import pytest

from src.models import CanvasUser
from tests.base_test import BaseTest


class TestCanvasUserRepo(BaseTest):

    def test_create_canvas_user(self, sample_user, canvas_user_repo, cleanup_all):
        with canvas_user_repo.session():
            user = sample_user()
            canvas_user = CanvasUser(
                user_id=user.id,
                canvas_id="canvas-id-1",
                username=f"canvas_{user.username}",
                web_id="web-id-1",
            )
            canvas_user.set_password(password="test-pwd123")
            canvas_user_repo.save_or_update(canvas_user)

        with canvas_user_repo.session():
            users = canvas_user_repo.list_all()
            assert len(users) == 1
            assert users[0].username == "canvas_test@gmail.com"
            assert users[0].web_id == "web-id-1"
            assert users[0].canvas_id == "canvas-id-1"
            assert users[0].user_id == user.id
            assert users[0].password == "test-pwd123"
            assert users[0].check_password("test-pwd123") is True
            assert users[0].check_password("test-pwd1234") is False

    def test_get_canvas_user_by_id(
        self, sample_canvas_user, canvas_user_repo, cleanup_all
    ):
        with canvas_user_repo.session():
            user = sample_canvas_user(username="test@gmail.com")
            created_user = canvas_user_repo.save_or_update(user)
            for i in range(5):
                user = sample_canvas_user(
                    username=f"test_{i}@gmail.com",
                    web_id=f"web-id-{2 + i}",
                    canvas_id=f"canvas-id-{2 + i}",
                )
                canvas_user_repo.save_or_update(user)

        with canvas_user_repo.session():
            users = canvas_user_repo.list_all()
            assert len(users) == 6
            user = canvas_user_repo.get_by_db_id(db_id=created_user.id)
            assert user is not None
            # beacuse of "_canvas" prefix
            assert user.username == "canvas_test@gmail.com"

    def test_update_canvas_user(
        self, sample_canvas_user, canvas_user_repo, cleanup_all
    ):
        with canvas_user_repo.session():
            user = sample_canvas_user(username="test@gmail.com")
            created_user = canvas_user_repo.save_or_update(user)

        with canvas_user_repo.session():
            user = canvas_user_repo.get_by_db_id(db_id=created_user.id)
            user.username = "another@gmail.com"
            user.set_password(password="another-pwd")
            canvas_user_repo.save_or_update(user)

        with canvas_user_repo.session():
            users = canvas_user_repo.list_all()
            assert len(users) == 1
            assert users[0].username == "another@gmail.com"
            assert users[0].check_password(password="test-pwd") is False
            assert users[0].check_password(password="another-pwd") is True

    def test_delete_canvas_user(
        self, sample_canvas_user, canvas_user_repo, cleanup_all
    ):
        with canvas_user_repo.session():
            user = sample_canvas_user(username="test@gmail.com")
            created_user = canvas_user_repo.save_or_update(user)

        with canvas_user_repo.session():
            user = canvas_user_repo.get_by_db_id(db_id=created_user.id)
            canvas_user_repo.delete(user)

        with canvas_user_repo.session():
            users = canvas_user_repo.list_all()
            assert len(users) == 0

    def test_get_by_user_id(self, sample_canvas_user, canvas_user_repo, cleanup_all):
        with canvas_user_repo.session():
            user = sample_canvas_user(username="test@gmail.com")
            created_user = canvas_user_repo.save_or_update(user)
            for i in range(5):
                user = sample_canvas_user(
                    username=f"test_{i}@gmail.com",
                    web_id=f"web-id-{2 + i}",
                    canvas_id=f"canvas-id-{2 + i}",
                )
                canvas_user_repo.save_or_update(user)

        with canvas_user_repo.session():
            users = canvas_user_repo.list_all()
            assert len(users) == 6
            user = canvas_user_repo.get_by_user_id(user_id=created_user.user_id)
            assert user is not None
            # beacuse of "_canvas" prefix
            assert user.username == "canvas_test@gmail.com"
