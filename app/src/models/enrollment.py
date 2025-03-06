from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from db import DbModel, HasWebId
from src.models.base import Base


class Enrollment(Base, DbModel, HasWebId):
    __tablename__ = "enrollments"
    student_id = Column(Integer, ForeignKey("app.students.id"))
    student = relationship("Student", back_populates="enrollments")
    course_id = Column(Integer, ForeignKey("app.canvas_courses.id"))
    course = relationship("CanvasCourse", back_populates="enrollments")
