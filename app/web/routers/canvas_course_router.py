from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from src.dto import auth_dto, canvas_assignment_dto, canvas_course_dto
from src.services.canvas_assignment_service import CanvasAssignmentService
from src.services.canvas_course_service import CanvasCourseService
from src.services.service_factory import service_factory
from web.depends.db import get_db_session
from web.depends.get_canvas_cookies import get_canvas_auth_data
from web.hooks.pagination_params import pagination_params

router = APIRouter(prefix="/api/canvas-courses/v1", tags=["Courses"])


def get_service(db_session: Annotated[Session, Depends(get_db_session)]):
    return service_factory().canvas_course_service(db_session=db_session)


def get_assignment_service(db_session: Annotated[Session, Depends(get_db_session)]):
    return service_factory().canvas_assignment_service(db_session=db_session)


@router.post("/load/users/{canvas_user_web_id}")
async def load_courses(
    canvas_user_web_id: str,
    service: Annotated[CanvasCourseService, Depends(get_service)],
    auth_data: Annotated[auth_dto.CanvasAuthData, Depends(get_canvas_auth_data)],
):
    result = await service.load_courses(
        canvas_user_web_id=canvas_user_web_id, canvas_auth_data=auth_data
    )
    return JSONResponse(
        status_code=status.HTTP_201_CREATED, content=jsonable_encoder(result)
    )


@router.get("/")
async def list_courses(
    filter_params: Annotated[canvas_course_dto.FilterParams, Depends()],
    pagination_params: Annotated[dict, Depends(pagination_params)],
    service: Annotated[CanvasCourseService, Depends(get_service)],
):
    result = service.list_courses(filter_params=filter_params, **pagination_params)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder(result),
    )


@router.get("/{web_id}/attendance-assignment-group")
async def get_attendance_assignment_group(
    web_id: str,
    service: Annotated[CanvasAssignmentService, Depends(get_assignment_service)],
    auth_data: Annotated[auth_dto.CanvasAuthData, Depends(get_canvas_auth_data)],
):
    result = await service.get_attendance_assignment_group(
        web_id=web_id, canvas_auth_data=auth_data
    )
    return JSONResponse(
        status_code=status.HTTP_200_OK, content=jsonable_encoder(result)
    )


@router.post("/{web_id}/assignments")
async def create_assignment(
    web_id: str,
    dto: canvas_assignment_dto.Create,
    service: Annotated[CanvasAssignmentService, Depends(get_assignment_service)],
    auth_data: Annotated[auth_dto.CanvasAuthData, Depends(get_canvas_auth_data)],
):
    result = await service.create_assignment(
        web_id=web_id, dto=dto, canvas_auth_data=auth_data
    )
    return JSONResponse(
        status_code=status.HTTP_201_CREATED, content=jsonable_encoder(result)
    )
