from typing import Optional

from pydantic import BaseModel, Field


class CanvasRead(BaseModel):
    canvas_assignment_id: int = Field(None, validation_alias="id")
    name: str


class Read(BaseModel):
    web_id: str
    canvas_assignment_id: int
    name: str
    course_id: int

    @classmethod
    def from_dbmodel(cls, item):
        return cls(
            web_id=item.web_id,
            name=item.name,
            course_id=item.course_id,
            canvas_assignment_id=item.canvas_assignment_id,
        )


class AssignmentGroup(BaseModel):
    group_weight: int
    assignment_group_id: int = Field(None, validation_alias="id")
    name: str
    position: int
    sis_source_id: Optional[int]
    assignments: list[Read]


class Create(BaseModel):
    assignment_group_id: int
