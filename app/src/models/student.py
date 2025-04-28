from sqlalchemy import Column, Integer, Text
from sqlalchemy.orm import relationship

from db import DbModel, HasWebId
from src.models.base import Base


class Student(Base, DbModel, HasWebId):
    __tablename__ = "students"
    name = Column(Text, nullable=False)
    email = Column(Text, nullable=True)
    canvas_user_id = Column(Integer, nullable=False, unique=True)

    enrollments = relationship("Enrollment", back_populates="student")
