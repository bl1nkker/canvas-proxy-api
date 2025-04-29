from deepface import DeepFace
from PIL import Image
from pydantic import BaseModel

ml_model = {}


class RepresentResult(BaseModel):
    embedding: list[float]


class MlService:
    def __init__(self):
        self.model_name = "Facenet512"

    def init_model(self):
        return DeepFace.build_model(model_name=self.model_name)

    def preprocess_image(self, file_path: str, max_size: int = 800) -> str:
        with Image.open(file_path) as img:
            img.thumbnail((max_size, max_size))
            img.save(file_path, format="JPEG", quality=100)
        return file_path

    def represent(self, image_path: str) -> RepresentResult:
        result = DeepFace.represent(
            img_path=image_path,
            model_name=self.model_name,
            enforce_detection=True,
            max_faces=1,
        )
        return RepresentResult(
            embedding=result[0]["embedding"],
        )
