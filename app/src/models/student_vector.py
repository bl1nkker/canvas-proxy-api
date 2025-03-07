from pgvector.sqlalchemy import Vector
from sqlalchemy import BigInteger, Column, ForeignKey
from sqlalchemy.orm import relationship

from db import DbModel, HasWebId
from src.models.base import Base


class StudentVector(Base, DbModel, HasWebId):
    __tablename__ = "student_vectors"
    student_id = Column(BigInteger, ForeignKey("app.students.id"), nullable=False)
    student = relationship("Student", foreign_keys=[student_id])
    embedding = Column(Vector(192), nullable=False, unique=True)
