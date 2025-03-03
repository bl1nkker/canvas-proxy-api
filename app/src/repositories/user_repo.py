from db.data_repo import DataRepo
from src.models import User


class UserRepo(DataRepo[User]):
    _type = User
    _order_by_map = None
