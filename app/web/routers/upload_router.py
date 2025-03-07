from collections.abc import Iterator
from typing import Annotated

from fastapi import APIRouter, Body, Depends, File, UploadFile, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy.orm import Session

from db.get_db_session import get_db_session
from src.dto import file_record_dto
from src.services.service_factory import service_factory
from src.services.upload_service import UploadService

router = APIRouter(
    prefix="/api/uploads/v1",
    tags=["Uploads"],
    responses={404: {"description": "Not found"}},
)


def get_service(db_session: Annotated[Session, Depends(get_db_session)]):
    return service_factory().upload_service(db_session=db_session)


@router.post(
    "/",
    response_model=file_record_dto.Read,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a new file",
    description="Uploads a new file and returns the uploaded file data.",
)
def post_create_upload(
    file: Annotated[UploadFile, File(...)],
    upload_service: Annotated[UploadService, Depends(get_service)],
):
    dto = upload_service.create_upload(
        name=file.filename,
        content_type=file.content_type,
        stream=file.file,
        media=None,
    )
    return JSONResponse(
        status_code=status.HTTP_201_CREATED, content=jsonable_encoder(dto)
    )


@router.get(
    "/{web_id}",
    status_code=status.HTTP_200_OK,
    summary="Download an uploaded file",
    description="Downloads an uploaded file by its web ID.",
)
def get_download_upload(
    web_id: str,
    upload_service: Annotated[UploadService, Depends(get_service)],
):

    record, stream = upload_service.get_upload_by_web_id(web_id=web_id)

    def iterfile() -> Iterator[bytes]:
        with stream:
            while chunk := stream.read(1024):
                yield chunk

    response = StreamingResponse(iterfile(), media_type=record.content_type)
    response.headers["Content-Disposition"] = f"attachment; filename={record.name}"

    return response


@router.get(
    "/metadata/{web_id}",
    response_model=file_record_dto.Metadata,
    status_code=status.HTTP_200_OK,
    summary="Get metadata for an uploaded file",
    description="Retrieves metadata associated with an uploaded file by its web ID.",
)
def get_metadata(
    web_id: str,
    upload_service: Annotated[UploadService, Depends(get_service)],
):
    dto = upload_service.get_metadata_by_web_id(web_id=web_id)
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(dto))


@router.post(
    "/metadata",
    response_model=file_record_dto.Metadata,
    status_code=status.HTTP_201_CREATED,
    summary="Create metadata for an uploaded file",
    description="Creates metadata for an uploaded file and returns the created metadata.",
)
def post_create_metadata(
    dto: Annotated[
        file_record_dto.CreateMetadata,
        Body(
            ...,
            example={
                "name": "Test File",
                "file_name": "test_file.csv",
                "content_type": "text/csv",
            },
        ),
    ],
    upload_service: Annotated[UploadService, Depends(get_service)],
):

    dto = upload_service.create_metadata(dto=dto)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED, content=jsonable_encoder(dto)
    )
