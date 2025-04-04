from typing import Any, Optional

from pydantic import BaseModel, Field


class Create(BaseModel):
    name: str
    email: str
    canvas_user_id: int


class CanvasRead(BaseModel):
    name: str
    email: str
    canvas_user_id: int = Field(validation_alias="id")


class Read(BaseModel):
    id: int
    web_id: Optional[str]
    name: str
    email: str

    @classmethod
    def from_dbmodel(cls, item):
        return cls(
            id=item.id,
            name=item.name,
            email=item.email,
            web_id=item.web_id,
        )


class StudentFile(BaseModel):
    origin_name: str
    image_id: str
    canvas_name: str
    canvas_login: str
    canvas_id: int
    image_vector: Optional[Any] = None
