from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.services.service_factory import service_factory
from src.services.face_recognition_service import FaceRecognitionService
from web.depends.db import get_db_session

router = APIRouter(prefix="/api/face-recognition/v1", tags=["Face Recognition"])


def get_service(db_session: Annotated[Session, Depends(get_db_session)]):
    return service_factory().face_recognition_service(db_session=db_session)


@router.post("/")
async def recognize_face(
    service: Annotated[FaceRecognitionService, Depends(get_service)]
):
    return None


@router.post("/hello")
async def hello(service: Annotated[FaceRecognitionService, Depends(get_service)]):
    res = service.run_test()
    return res
