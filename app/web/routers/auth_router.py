from typing import Annotated

import redis
from fastapi import APIRouter, Depends, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from broker.get_client import get_broker_client
from db.get_db_session import get_db_session
from src.dto import auth_dto
from src.services.auth_service import AuthService
from src.services.service_factory import service_factory

router = APIRouter(prefix="/api/auth/v1", tags=["Auth"])


def get_service(
    db_session: Annotated[Session, Depends(get_db_session)],
    redis_client: Annotated[redis.Redis, Depends(get_broker_client)],
):
    return service_factory().auth_service(
        db_session=db_session, redis_client=redis_client
    )


@router.post("/signin")
async def signin(
    dto: auth_dto.LoginRequest, service: Annotated[AuthService, Depends(get_service)]
):
    result, auth_data = await service.signin(dto=dto)
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
