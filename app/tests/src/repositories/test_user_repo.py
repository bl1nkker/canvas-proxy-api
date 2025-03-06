from src.models import User
from tests.base_test import BaseTest


class TestUserRepo(BaseTest):

    def test_create_user(self, user_repo, cleanup_all):
        with user_repo.session():
            user = User(username="test@gmail.com", web_id="web-id-1")
            user.set_password(password="test-pwd123")
            user_repo.save_or_update(user)

        with user_repo.session():
            users = user_repo.list_all()
            assert len(users) == 1
            assert users[0].username == "test@gmail.com"
            assert users[0].web_id == "web-id-1"
            assert users[0].check_password("test-pwd123") is True
            assert users[0].check_password("test-pwd1234") is False

    def test_get_user_by_id(self, sample_user, user_repo, cleanup_all):
        with user_repo.session():
            user = sample_user(username="test@gmail.com")
            created_user = user_repo.save_or_update(user)
            for i in range(5):
                user = sample_user(username=f"test_{i}@gmail.com")
                user_repo.save_or_update(user)

        with user_repo.session():
            users = user_repo.list_all()
            assert len(users) == 6
            user = user_repo.get_by_db_id(db_id=created_user.id)
            assert user is not None
            assert user.username == "test@gmail.com"

    def test_update_user(self, sample_user, user_repo, cleanup_all):
        with user_repo.session():
            user = sample_user(username="test@gmail.com")
            created_user = user_repo.save_or_update(user)

        with user_repo.session():
            user = user_repo.get_by_db_id(db_id=created_user.id)
            user.username = "another@gmail.com"
            user.set_password(password="another-pwd")
            user_repo.save_or_update(user)

        with user_repo.session():
            users: list[User] = user_repo.list_all()
            assert len(users) == 1
            assert users[0].username == "another@gmail.com"
            assert users[0].check_password(password="test-pwd") is False
            assert users[0].check_password(password="another-pwd") is True

    def test_delete_user(self, sample_user, user_repo, cleanup_all):
        with user_repo.session():
            user = sample_user(username="test@gmail.com")
            created_user = user_repo.save_or_update(user)

        with user_repo.session():
            user = user_repo.get_by_db_id(db_id=created_user.id)
            user_repo.delete(user)

        with user_repo.session():
            users: list[User] = user_repo.list_all()
            assert len(users) == 0

    def test_get_by_username(self, sample_user, user_repo, cleanup_all):
        with user_repo.session():
            user = sample_user(username="test@gmail.com")
            user_repo.save_or_update(user)
            for i in range(5):
                user = sample_user(username=f"test_{i}@gmail.com")
                user_repo.save_or_update(user)

        with user_repo.session():
            users = user_repo.list_all()
            assert len(users) == 6
            user = user_repo.get_by_username(username="test@gmail.com")
            assert user is not None
            assert user.username == "test@gmail.com"
