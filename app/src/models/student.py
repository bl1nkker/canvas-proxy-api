from sqlalchemy import Column, Text
from sqlalchemy.orm import relationship

from db import DbModel, HasWebId
from src.models.base import Base


class Student(Base, DbModel, HasWebId):
    __tablename__ = "students"
    firstname = Column(Text, nullable=False)
    lastname = Column(Text, nullable=False)
    email = Column(Text, nullable=True)

    enrollments = relationship("Enrollment", back_populates="student")

    @property
    def fullname(self):
        return f"{self.firstname} {self.lastname}"
