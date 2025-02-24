from src.repositories.file_record_repo import FileRecordRepo
from ml import face_encoder
from sqlalchemy.sql import text


class FaceRecognitionService:
    def __init__(self, file_record_repo: FileRecordRepo):
        self._file_record_repo = file_record_repo

    def run_test(self) -> int:
        result = self.db_session.execute(text("SELECT 1")).scalar()
        return result
    
    def recognize_face(self, web_id: str) -> None:
        # Retrieve photo from db
        with self._file_record_repo.session():
            file = self._file_record_repo.get_by_web_id(web_id=web_id)
        # Get image encoding
        b = face_encoder.image_to_bytes(image_path=file.path)
        face_encoding = face_encoder.get_face_encoding(image=b)
        print(face_encoding)

        # Search vector using distance
        
        # Return metadata for image (name, etc)
        return 123
