from typing import Optional

from pydantic import BaseModel, Field


class Assignment(BaseModel):
    assignment_id: int = Field(None, validation_alias="id")
    name: str


class AssignmentGroup(BaseModel):
    group_weight: int
    assignment_group_id: int = Field(None, validation_alias="id")
    name: str
    position: int
    sis_source_id: Optional[int]
    assignments: list[Assignment]


class Create(BaseModel):
    assignment_group_id: int
