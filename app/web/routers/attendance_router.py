from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from db.get_db_session import get_db_session
from src.dto import attendance_dto, auth_dto
from src.services.attendance_service import AttendanceService
from src.services.service_factory import service_factory
from web.depends.get_canvas_cookies import get_canvas_auth_data
from web.hooks.pagination_params import pagination_params

router = APIRouter(prefix="/api/attendances/v1", tags=["Attendances"])


def get_service(db_session: Annotated[Session, Depends(get_db_session)]):
    return service_factory().attendance_service(db_session=db_session)


@router.get("/")
def list_attendance_by_assignment_id(
    filter_params: Annotated[attendance_dto.FilterParams, Depends()],
    pagination_params: Annotated[dict, Depends(pagination_params)],
    service: Annotated[AttendanceService, Depends(get_service)],
):
    result = service.list_attendances_by_assignment(
        assignment_id=filter_params.assignment_id, **pagination_params
    )
    return JSONResponse(
        status_code=status.HTTP_200_OK, content=jsonable_encoder(result)
    )


@router.put("/{web_id}/mark")
def mark_attendance(
    web_id: str,
    dto: attendance_dto.Mark,
    service: Annotated[AttendanceService, Depends(get_service)],
):
    result = service.mark_attendance(web_id=web_id, dto=dto)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED, content=jsonable_encoder(result)
    )


@router.put("/mark/search")
def search_and_mark_attendance_by_student_image(
    file: Annotated[UploadFile, File(...)],
    course_id: Annotated[int, Form(...)],
    assignment_id: Annotated[int, Form(...)],
    service: Annotated[AttendanceService, Depends(get_service)],
):
    result = service.mark_attendance_by_image(
        dto=attendance_dto.Search(course_id=course_id, assignment_id=assignment_id),
        stream=file.file,
    )
    return JSONResponse(
        status_code=status.HTTP_201_CREATED, content=jsonable_encoder(result)
    )


@router.post("/load")
async def load_course_attendances_from_canvas(
    dto: attendance_dto.Load,
    service: Annotated[AttendanceService, Depends(get_service)],
    auth_data: Annotated[auth_dto.CanvasAuthData, Depends(get_canvas_auth_data)],
):
    result = await service.load_course_attendances_from_canvas(
        dto=dto, canvas_auth_data=auth_data
    )
    return JSONResponse(
        status_code=status.HTTP_201_CREATED, content=jsonable_encoder(result)
    )
