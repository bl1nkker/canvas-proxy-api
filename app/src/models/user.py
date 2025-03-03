import bcrypt
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from db import DbModel, HasWebId
from src.models.base import Base


class User(Base, DbModel, HasWebId):
    __tablename__ = "users"

    username = Column(String(32), nullable=False, unique=True)
    hashed_password = Column(String, nullable=False)

    canvas_user = relationship("CanvasUser", back_populates="user", uselist=False)

    def set_password(self, password: str):
        self.hashed_password = bcrypt.hashpw(
            password.encode(), bcrypt.gensalt()
        ).decode()

    def check_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode(), self.hashed_password.encode())
