from typing import Optional

from sqlalchemy import JSON, BigInteger, Column, ForeignKey
from sqlalchemy.orm import relationship

from db import DbModel, HasWebId
from src.dto import file_record_dto, recognition_history_dto
from src.models.base import Base


class RecognitionHistory(Base, DbModel, HasWebId):
    __tablename__ = "recognition_history"
    student_id = Column(BigInteger, ForeignKey("app.students.id"), nullable=True)
    student = relationship("Student", foreign_keys=[student_id])

    image_file_json = Column(JSON(none_as_null=True), nullable=True)
    recognition_details_json = Column(JSON(none_as_null=True), nullable=True)

    @property
    def image_file(self) -> file_record_dto.Metadata:
        if self.image_file_json:
            return file_record_dto.Metadata(**self.image_file_json)

    @property
    def recognition_details(
        self,
    ) -> Optional[recognition_history_dto.RecognitionDetails]:
        if self.recognition_details_json:
            return recognition_history_dto.RecognitionDetails(
                **self.recognition_details_json
            )
