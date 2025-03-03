import pytest

from src.models import FileRecord
from tests.base_test import BaseTest


class TestFileRecordRepo(BaseTest):
    @pytest.fixture
    def file_record1(self):
        return FileRecord(
            web_id="web-id-1",
            name="data.csv",
            content_type="text/csv",
            size=1024,
            path="/dev/null",
        )

    def test_should_save_file_record(self, file_record_repo, file_record1):
        file_record_repo.save_or_update(file_record1)

        file_records = file_record_repo.list_all()
        assert len(file_records) == 1
        assert file_records[0] is file_record1

    def test_get_file_record_by_web_id(self, file_record_repo, file_record1):
        file_record = file_record_repo.save_or_update(file_record1)

        found_file_record = file_record_repo.get_by_web_id("web-id-1")
        assert file_record is found_file_record

    def test_delete_file_record(self, file_record_repo, file_record1):
        file_record = file_record_repo.save_or_update(file_record1)
        file_record_repo.delete(file_record)

        file_records = file_record_repo.list_all()
        assert len(file_records) == 0
