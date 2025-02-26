from db.data_repo import DataRepo
from src.models import StudentVector


class StudentVectorRepo(DataRepo[StudentVector]):
    _type = StudentVector
    _order_by_map = None
