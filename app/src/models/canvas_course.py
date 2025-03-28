from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from db import DbModel, HasWebId
from src.models.base import Base


class CanvasCourse(Base, DbModel, HasWebId):
    __tablename__ = "canvas_courses"
    long_name = Column(String, nullable=True)
    short_name = Column(String, nullable=True)
    original_name = Column(String, nullable=True)
    course_code = Column(String, nullable=True)
    canvas_course_id = Column(Integer, nullable=False, unique=True)
    canvas_user_id = Column(
        Integer, ForeignKey("app.canvas_users.id", ondelete="CASCADE")
    )
    canvas_user = relationship("CanvasUser", back_populates="courses", lazy="joined")

    enrollments = relationship(
        "Enrollment",
        back_populates="course",
        primaryjoin="CanvasCourse.id == Enrollment.course_id",
        lazy="selectin",
    )

    assignment_groups = relationship(
        "AssignmentGroup",
        back_populates="course",
        primaryjoin="CanvasCourse.id == AssignmentGroup.course_id",
        lazy="selectin",
    )
