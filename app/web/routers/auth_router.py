from typing import Annotated
from fastapi import APIRouter, Depends

from src.dto import auth_dto
from src.services.auth_service import AuthService
from src.services.service_factory import service_factory

router = APIRouter(prefix="/api/auth/v1", tags=["Auth"])

def get_service():
    return service_factory().auth_service()

@router.post("/")
async def login(
    dto: auth_dto.LoginCredentials,
    service: Annotated[AuthService, Depends(get_service)]
):
    result = await service.login(dto=dto)
    return result