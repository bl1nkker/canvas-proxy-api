from typing import Optional

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
