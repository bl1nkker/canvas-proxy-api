from src.services.face_recognition_service import FaceRecognitionService


class ServiceFactory:

    @staticmethod
    def face_recognition_service(db_session):
        return FaceRecognitionService(db_session=db_session)


_service_factory = ServiceFactory()


def service_factory():
    return _service_factory
