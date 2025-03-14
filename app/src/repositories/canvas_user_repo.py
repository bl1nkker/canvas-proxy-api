from db.data_repo import DataRepo
from src.models import CanvasUser


class CanvasUserRepo(DataRepo[CanvasUser]):
    _type = CanvasUser
    _order_by_map = None

    def get_by_user_id(self, user_id: int, query=None):
        query = query or self.query()
        return query.filter(CanvasUser.user_id == user_id).first()

    def get_by_web_id(self, web_id: str, query=None):
        query = query or self.query()
        return query.filter(CanvasUser.web_id == web_id).first()
