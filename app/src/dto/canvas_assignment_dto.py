from pydantic import BaseModel, Field


class AssignmentGroupBase(BaseModel):
    group_weight: int
    name: str


class CanvasRead(BaseModel):
    canvas_assignment_id: int = Field(None, validation_alias="id")
    name: str


class Read(BaseModel):
    id: int
    web_id: str
    canvas_assignment_id: int
    name: str
    assignment_group_id: int

    @classmethod
    def from_dbmodel(cls, item):
        return cls(
            id=item.id,
            web_id=item.web_id,
            name=item.name,
            assignment_group_id=item.assignment_group_id,
            canvas_assignment_id=item.canvas_assignment_id,
        )


class AssignmentGroupRead(AssignmentGroupBase):
    web_id: str
    id: int
    canvas_assignment_group_id: int
    assignments: list[Read]

    @classmethod
    def from_dbmodel(cls, item):
        return cls(
            id=item.id,
            web_id=item.web_id,
            group_weight=item.group_weight,
            name=item.name,
            canvas_assignment_group_id=item.canvas_assignment_group_id,
            assignments=[Read.from_dbmodel(a) for a in item.assignments],
        )


class AssignmentGroupCanvas(AssignmentGroupBase):
    assignment_group_id: int = Field(None, validation_alias="id")
    assignments: list[CanvasRead]
