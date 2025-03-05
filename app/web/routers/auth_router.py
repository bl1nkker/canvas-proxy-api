from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from src.dto import auth_dto
from src.services.auth_service import AuthService
from src.services.service_factory import service_factory
from web.depends.db import get_db_session

router = APIRouter(prefix="/api/auth/v1", tags=["Auth"])


def get_service(db_session: Annotated[Session, Depends(get_db_session)]):
    return service_factory().auth_service(db_session=db_session)


@router.post("/signin")
async def signin(
    dto: auth_dto.LoginRequest, service: Annotated[AuthService, Depends(get_service)]
):
    result, auth_data = await service.get_canvas_auth_data(dto=dto)
    response = JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder(result),
    )
    for k, v in auth_data.model_dump(by_alias=True).items():
        response.set_cookie(key=k, value=v)
    return response


@router.post("/signup")
async def signup(
    dto: auth_dto.Signup, service: Annotated[AuthService, Depends(get_service)]
):
    result, auth_data = await service.create_user(dto=dto)
    response = JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder(result),
    )
    for k, v in auth_data.model_dump(by_alias=True).items():
        response.set_cookie(key=k, value=v)
    return response
