from src.services.auth_service import AuthService
from src.services.student_service import StudentService
from src.repositories.student_repo import StudentRepo
from src.repositories.student_vector_repo import StudentVectorRepo
from src.repositories.file_fs_repo import FileFsRepo
from src.services.upload_service import UploadService
from src.repositories.file_record_repo import FileRecordRepo
from src.services.face_recognition_service import FaceRecognitionService


class ServiceFactory:

    def student_repo(self, db_session):
        return StudentRepo(db_session=db_session)

    def student_vector_repo(self, db_session):
        return StudentVectorRepo(db_session=db_session)

    def file_fs_repo(self):
        return FileFsRepo()

    def file_record_repo(self, db_session):
        return FileRecordRepo(db_session=db_session)

    def upload_service(self, db_session):
        return UploadService(
            file_record_repo=self.file_record_repo(db_session=db_session),
            file_fs_repo=self.file_fs_repo(),
        )

    def face_recognition_service(self, db_session):
        return FaceRecognitionService(
            file_record_repo=self.file_record_repo(db_session=db_session),
            student_repo=self.student_repo(db_session=db_session),
            student_vector_repo=self.student_vector_repo(db_session=db_session),
        )

    def student_service(self, db_session):
        return StudentService(
            student_repo=self.student_repo(db_session=db_session),
            student_vector_repo=self.student_vector_repo(db_session=db_session),
            upload_service=self.upload_service(db_session=db_session),
        )
    
    def auth_service(self):
        return AuthService()


_service_factory = ServiceFactory()


def service_factory():
    return _service_factory
