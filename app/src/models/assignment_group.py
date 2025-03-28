from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from db import DbModel, HasWebId
from src.models.base import Base


class AssignmentGroup(Base, DbModel, HasWebId):
    __tablename__ = "assignment_groups"

    name = Column(String, nullable=False)
    group_weight = Column(Integer, nullable=False)
    course_id = Column(Integer, ForeignKey("app.canvas_courses.id"))
    course = relationship("CanvasCourse", back_populates="assignment_groups")
    canvas_assignment_group_id = Column(Integer, nullable=False)

    assignments = relationship(
        "Assignment",
        back_populates="assignment_group",
        primaryjoin="AssignmentGroup.id == Assignment.assignment_group_id",
        lazy="selectin",
    )
