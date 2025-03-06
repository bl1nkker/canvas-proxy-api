from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from db import DbModel, HasWebId
from src.models.base import Base
from utils.dencrypt import decrypt, encrypt


class CanvasUser(Base, DbModel, HasWebId):
    __tablename__ = "canvas_users"

    user_id = Column(Integer, ForeignKey("app.users.id", ondelete="CASCADE"))
    canvas_id = Column(String, unique=True, nullable=False)
    username = Column(String(32), nullable=False, unique=True)
    encrypted_password = Column(String, nullable=False)

    user = relationship("User", back_populates="canvas_user")
    courses = relationship(
        "CanvasCourse", back_populates="canvas_user", cascade="all, delete-orphan"
    )

    def set_password(self, password: str):
        self.encrypted_password = encrypt(password)

    def check_password(self, password: str) -> bool:
        return password == self.password

    @property
    def password(self):
        return decrypt(self.encrypted_password)
