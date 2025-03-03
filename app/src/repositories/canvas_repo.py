from db.data_repo import DataRepo
from src.models import CanvasUser


class CanvasUserRepo(DataRepo[CanvasUser]):
    _type = CanvasUser
    _order_by_map = None
