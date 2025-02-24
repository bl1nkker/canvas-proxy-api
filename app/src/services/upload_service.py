import io
import os
from typing import Tuple, BinaryIO
import shortuuid
from sqlalchemy.orm.exc import NoResultFound

from src.dto import file_record_dto
from src.repositories.file_fs_repo import FileFsRepo
from src.models import FileRecord
from src.repositories.file_record_repo import FileRecordRepo
from src.errors.types import NotFoundError


class UploadService:
    @staticmethod
    def read_from_dbmodel(file_record: FileRecord):
        return file_record_dto.Read(
            web_id=file_record.web_id,
            name=file_record.name,
            size=file_record.size,
            content_type=file_record.content_type,
        )

    @staticmethod
    def metadata_from_dbmodel(file_record: FileRecord):
        return file_record_dto.Metadata(
            web_id=file_record.web_id,
            name=file_record.name,
            size=file_record.size,
            content_type=file_record.content_type,
            path=file_record.path,
        )

    def __init__(self, file_fs_repo: FileFsRepo, file_record_repo: FileRecordRepo):
        self._file_fs_repo = file_fs_repo
        self._file_record_repo = file_record_repo

    def create_upload(
        self,
        name: str,
        content_type: str,
        stream: io.BufferedReader,
        media: dict = None,
    ) -> file_record_dto.Metadata:
        file_path, file_size = self._file_fs_repo.save(content_type, stream, media)
        with self._file_record_repo.session():
            file_record = FileRecord(
                web_id=shortuuid.uuid(),
                name=name,
                content_type=content_type,
                size=file_size,
                path=file_path,
            )
            self._file_record_repo.save_or_update(file_record)
            return self.metadata_from_dbmodel(file_record)

    def get_upload_by_web_id(
        self, web_id: str
    ) -> Tuple[file_record_dto.Read, BinaryIO]:
        with self._file_record_repo.session():
            file_record = self._get_file_record_by_web_id(web_id)
            return self.read_from_dbmodel(file_record), open(file_record.path, "rb")

    def get_metadata_by_web_id(self, web_id: str) -> file_record_dto.Metadata:
        with self._file_record_repo.session():
            file_record = self._get_file_record_by_web_id(web_id)
            return self.metadata_from_dbmodel(file_record)

    def get_metadata_by_name(self, name: str) -> file_record_dto.Metadata | None:
        with self._file_record_repo.session():
            file_records = self._file_record_repo.get_by_name(name)
            for file_record in file_records:
                if os.path.exists(file_record.path):
                    return self.metadata_from_dbmodel(file_record)

    def create_metadata(
        self, dto: file_record_dto.CreateMetadata
    ) -> file_record_dto.Metadata:
        file_info = self._file_fs_repo.get_file_info(dto.file_name)
        if not file_info:
            raise NotFoundError(
                f"_error_msg_file_with_such_name_not_found:{dto.file_name}"
            )

        file_path, file_size = file_info
        with self._file_record_repo.session():
            file_record = FileRecord(
                web_id=shortuuid.uuid(),
                name=dto.name,
                content_type=dto.content_type,
                size=file_size,
                path=file_path,
            )
            self._file_record_repo.save_or_update(file_record)
            return self.metadata_from_dbmodel(file_record)

    def _get_file_record_by_web_id(self, web_id: str) -> FileRecord:
        try:
            file_record = self._file_record_repo.get_by_web_id(web_id)
            if not os.path.exists(file_record.path):
                raise NotFoundError(f"_error_msg_file_not_found:{web_id}")
            return file_record
        except NoResultFound:
            raise NotFoundError(f"_error_msg_file_not_found:{web_id}")
