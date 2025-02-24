from src.repositories.file_record_repo import FileRecordRepo
from ml.face_encoder import preprocess_image, get_face_encoding
from sqlalchemy.sql import text


class FaceRecognitionService:
    def __init__(self, file_record_repo: FileRecordRepo):
        self.file_record_repo = file_record_repo

    def run_test(self) -> int:
        result = self.db_session.execute(text("SELECT 1")).scalar()
        return result
