from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.dto import auth_dto
from src.services.auth_service import AuthService
from src.services.service_factory import service_factory
from web.depends.db import get_db_session

router = APIRouter(prefix="/api/auth/v1", tags=["Auth"])


def get_service(db_session: Annotated[Session, Depends(get_db_session)]):
    return service_factory().auth_service(db_session=db_session)


@router.post("/")
async def login(
    dto: auth_dto.LoginRequest, service: Annotated[AuthService, Depends(get_service)]
):
    result = await service.get_canvas_auth_data(dto=dto)
    return result


@router.post("/signup")
async def signup(
    dto: auth_dto.LoginRequest, service: Annotated[AuthService, Depends(get_service)]
):
    result = await service.create_user(dto=dto)
    return result


@router.post("/courses")
async def get_courses(
    dto: auth_dto.LoginRequest, service: Annotated[AuthService, Depends(get_service)]
):
    result = await service.get_courses(dto=dto)
    return result
