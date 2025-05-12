from db.data_repo import DataRepo
from src.models import RecognitionHistory


class RecognitionHistoryRepo(DataRepo[RecognitionHistory]):
    _type = RecognitionHistory
    _order_by_map = None
