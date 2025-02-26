from src.errors.types import InvalidContentTypeError
from fastapi import File, UploadFile


def validate_content_type(
    file: UploadFile = File(...), valid_content_types: list[str] = ["image/jpeg"]
):
    content_type = file.content_type
    if content_type not in valid_content_types:
        expected = ",".join(valid_content_types)
        raise InvalidContentTypeError(
            f"lsse_invalid_content_type:content_type={content_type};expected={expected}"
        )
