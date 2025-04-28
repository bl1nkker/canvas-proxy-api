from deepface import DeepFace
from pydantic import BaseModel

ml_model = {}


class RepresentResult(BaseModel):
    embedding: list[float]


class MlService:
    def __init__(self):
        self.model_name = "Facenet512"

    def init_model(self):
        return DeepFace.build_model(model_name=self.model_name)

    def represent(self, image_path: str) -> RepresentResult:
        result = DeepFace.represent(
            img_path=image_path,
            model_name=self.model_name,
            enforce_detection=False,
        )
        return RepresentResult(
            embedding=result[0]["embedding"],
        )
