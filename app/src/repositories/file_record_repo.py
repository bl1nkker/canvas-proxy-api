from db.data_repo import DataRepo
from src.models import FileRecord


class FileRecordRepo(DataRepo[FileRecord]):
    _type = FileRecord
    _order_by_map = None

    def get_by_web_id(self, web_id: str) -> FileRecord:
        return self.query().filter(FileRecord.web_id == web_id).one()

    def get_by_name(self, name: str) -> list[FileRecord]:
        return self.query().filter(self._type.name == name).all()
