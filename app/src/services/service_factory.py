from src.repositories.file_fs_repo import FileFsRepo
from src.services.upload_service import UploadService
from src.repositories.file_record_repo import FileRecordRepo
from src.services.face_recognition_service import FaceRecognitionService


class ServiceFactory:
    
    def file_fs_repo(self):
        return FileFsRepo()

    def file_record_repo(self, db_session):
        return FileRecordRepo(db_session=db_session)

    def upload_service(self, db_session):
        return UploadService(file_record_repo=self.file_record_repo(db_session=db_session), file_fs_repo=self.file_fs_repo())

    def face_recognition_service(self, db_session):
        return FaceRecognitionService(file_record_repo=self.file_record_repo(db_session=db_session))



_service_factory = ServiceFactory()


def service_factory():
    return _service_factory
