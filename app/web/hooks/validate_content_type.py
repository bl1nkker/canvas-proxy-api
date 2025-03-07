from typing import Annotated

from fastapi import File, UploadFile

from src.errors.types import InvalidContentTypeError


def validate_content_type(
    file: Annotated[UploadFile, File(...)], valid_content_types: list[str] = None
):
    valid_content_types = valid_content_types or []
    content_type = file.content_type
    if content_type not in valid_content_types:
        expected = ",".join(valid_content_types)
        raise InvalidContentTypeError(
            f"lsse_invalid_content_type:content_type={content_type};expected={expected}"
        )
