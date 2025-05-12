from typing import Optional

from pydantic import BaseModel

from src.dto import file_record_dto


class FilterParams(BaseModel):
    student_id: Optional[int] = None
    assignment_id: Optional[int] = None


class RecognitionDetails(BaseModel):
    duration: float


class Create(BaseModel):
    student_id: int
    assignment_id: int
    image_file: Optional[file_record_dto.Metadata]
    recognition_details: Optional[RecognitionDetails]


class Read(BaseModel):
    web_id: str
    student_id: int
    assignment_id: int
    image_file: Optional[file_record_dto.Metadata]
    recognition_details: Optional[RecognitionDetails]

    @classmethod
    def from_dbmodel(cls, dbmodel):
        return cls(
            web_id=dbmodel.web_id,
            assignment_id=dbmodel.assignment_id,
            student_id=dbmodel.student_id,
            image_file=dbmodel.image_file_json,
            recognition_details=dbmodel.recognition_details_json,
        )
