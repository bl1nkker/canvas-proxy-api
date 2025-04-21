from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from db.get_db_session import get_db_session
from src.services.service_factory import service_factory
from src.services.source_data_load_service import SourceDataLoadService

router = APIRouter(prefix="/internal/admin/v1", tags=["Admin"])


def get_source_data_load_service(
    db_session: Annotated[Session, Depends(get_db_session)],
):
    return service_factory().source_data_load_service(db_session=db_session)


@router.post("/load/{user_id}")
async def load_canvas_data(
    user_id: int,
    service: Annotated[SourceDataLoadService, Depends(get_source_data_load_service)],
):
    result = await service.load_data_from_canvas(user_id=user_id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder(result),
    )
