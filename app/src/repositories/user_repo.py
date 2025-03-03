from db.data_repo import DataRepo
from src.models import User


class UserRepo(DataRepo[User]):
    _type = User
    _order_by_map = None

    def get_by_username(self, username, query=None) -> User:
        query = query or self.query()
        return query.filter(User.username == username).first()
