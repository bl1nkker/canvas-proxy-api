from sqlalchemy import Column, Integer, String

from db import DbModel, HasWebId
from src.models.base import Base


class FileRecord(Base, DbModel, HasWebId):
    __tablename__ = "files"

    name = Column(String(256), nullable=False)
    content_type = Column(String(256), nullable=False)
    size = Column(Integer, nullable=False)
    path = Column(String(512), nullable=False)
