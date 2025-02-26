from sqlalchemy import Column, Text

from db import DbModel, HasWebId
from src.models.base import Base


class Student(Base, DbModel, HasWebId):
    __tablename__ = "students"
    firstname = Column(Text, nullable=False)
    lastname = Column(Text, nullable=False)
    email = Column(Text, nullable=True)

    @property
    def fullname(self):
        return f"{self.firstname} {self.lastname}"
