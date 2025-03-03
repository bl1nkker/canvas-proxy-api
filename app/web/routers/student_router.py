from functools import partial
from typing import Annotated

from fastapi import APIRouter, Body, Depends, File, UploadFile, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from src.dto import student_dto
from src.services.service_factory import service_factory
from src.services.student_service import StudentService
from web.depends.db import get_db_session
from web.hooks.validate_content_type import validate_content_type

router = APIRouter(prefix="/api/students/v1", tags=["Students"])


def get_service(db_session: Annotated[Session, Depends(get_db_session)]):
    return service_factory().student_service(db_session=db_session)


@router.get("/{web_id}")
async def get_student(
    web_id: str, service: Annotated[StudentService, Depends(get_service)]
):
    dto = service.get_student_by_web_id(web_id=web_id)
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(dto))


@router.get("/")
async def list_students(
    service: Annotated[StudentService, Depends(get_service)],
    page: int = 1,
    page_size: int = 10,
    order_by: str = "id",
    asc: bool = False,
):
    dto = service.list_students(
        page=page, page_size=page_size, order_by=order_by, asc=asc
    )
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(dto))


@router.post("/")
async def save_student(
    service: Annotated[StudentService, Depends(get_service)],
    dto: student_dto.Create = Body(
        ...,
        example={"firstname": "Sam", "lastname": "Altman", "email": "bot@gmail.com"},
    ),
):
    dto = service.save_student(dto=dto)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED, content=jsonable_encoder(dto)
    )


@router.post(
    "/{web_id}/image",
    dependencies=[Depends(partial(validate_content_type, ["image/jpeg"]))],
)
async def save_student_image(
    web_id: str,
    service: Annotated[StudentService, Depends(get_service)],
    file: UploadFile = File(...),
):
    dto = service.save_student_image(
        web_id=web_id,
        name=file.filename,
        content_type=file.content_type,
        stream=file.file,
    )
    return JSONResponse(
        status_code=status.HTTP_201_CREATED, content=jsonable_encoder(dto)
    )


@router.post(
    "/search",
    dependencies=[Depends(partial(validate_content_type, ["image/jpeg"]))],
)
async def search_student_by_image(
    service: Annotated[StudentService, Depends(get_service)],
    file: UploadFile = File(...),
):
    dto = service.search_student_by_image(
        name=file.filename, content_type=file.content_type, stream=file.file
    )
    return JSONResponse(
        status_code=status.HTTP_201_CREATED, content=jsonable_encoder(dto)
    )
