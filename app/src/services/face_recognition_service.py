from sqlalchemy.sql import text


class FaceRecognitionService:
    def __init__(self, db_session):
        self.db_session = db_session

    def run_test(self) -> int:
        result = self.db_session.execute(text("SELECT 1")).scalar()
        return result
