from typing import Optional

from pydantic import BaseModel


class AssignmentGroup(BaseModel):
    group_weight: int
    id: int
    name: str
    position: int
    sis_source_id: Optional[int]
