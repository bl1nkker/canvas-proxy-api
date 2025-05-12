from pydantic import BaseModel


class RecognitionDetails(BaseModel):
    duration: float
