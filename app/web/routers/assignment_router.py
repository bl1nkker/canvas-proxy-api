from typing import Annotated

from fastapi import APIRouter, Body, Depends, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from db.get_db_session import get_db_session
from src.dto import assignment_dto, auth_dto
from src.services.assignment_service import AssignmentService
from src.services.service_factory import service_factory
from web.depends.get_canvas_cookies import get_canvas_auth_data
from web.hooks.pagination_params import pagination_params

router = APIRouter(prefix="/api/assignments/v1", tags=["Assignments"])


def get_service(db_session: Annotated[Session, Depends(get_db_session)]):
    return service_factory().assignment_service(db_session=db_session)


@router.post("/")
async def create_assignment(
    service: Annotated[AssignmentService, Depends(get_service)],
    dto: Annotated[assignment_dto.Create, Body(...)],
    auth_data: Annotated[auth_dto.CanvasAuthData, Depends(get_canvas_auth_data)],
):
    dto = await service.create_assignment(dto=dto, canvas_auth_data=auth_data)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED, content=jsonable_encoder(dto)
    )


@router.get("/")
async def list_assignments(
    service: Annotated[AssignmentService, Depends(get_service)],
    filter_params: Annotated[assignment_dto.FilterParams, Depends()],
    pagination_params: Annotated[dict, Depends(pagination_params)],
):
    dto = service.list_assignments(filter_params=filter_params, **pagination_params)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED, content=jsonable_encoder(dto)
    )
