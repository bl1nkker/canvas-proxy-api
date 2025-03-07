from typing import Optional

from pydantic import BaseModel, Field


class Create(BaseModel):
    firstname: str
    lastname: str
    email: str
    canvas_user_id: int


class CanvasRead(BaseModel):
    name: str
    email: str
    canvas_user_id: int = Field(validation_alias="id")


class Read(BaseModel):
    web_id: Optional[str]
    name: str
    email: str
    canvas_user_id: int

    @classmethod
    def from_dbmodel(cls, item):
        return cls(
            name=item.name,
            email=item.email,
            web_id=item.web_id,
            canvas_user_id=item.canvas_user_id,
        )
