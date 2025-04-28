import os

import cv2
import numpy as np
from ai_edge_litert.interpreter import Interpreter
from deepface import DeepFace
from pydantic import BaseModel

ml_model = {}


class RepresentResult(BaseModel):
    embedding: list[float]


class MlService:
    def __init__(self):
        pass

    def init_model(self, model_name: str):
        if model_name == "Mobile":
            model_path = "ml/mobile_face_net.tflite"
            if not os.path.exists(model_path):
                raise Exception(f"Model file '{model_path}' not found! Check path.")
            global ml_model
            ml_model["interpreter"] = Interpreter(model_path=model_path)
            ml_model["interpreter"].allocate_tensors()
            ml_model["input_details"] = ml_model["interpreter"].get_input_details()
            ml_model["output_details"] = ml_model["interpreter"].get_output_details()
            return ml_model
        else:
            return DeepFace.build_model(model_name=model_name)

    def represent(self, model_name: str, image_path: str) -> RepresentResult:
        if model_name == "Mobile":
            return RepresentResult(
                embedding=self.represent_mobile(image_path=image_path)
            )
        result = DeepFace.represent(
            img_path=image_path,
            model_name=model_name,
            enforce_detection=False,
        )
        return RepresentResult(
            embedding=result[0]["embedding"],
        )

    def represent_mobile(self, image_path: str):
        def image_to_bytes(image_path: str) -> bytes:
            with open(image_path, "rb") as f:
                return f.read()

        b = image_to_bytes(image_path=image_path)
        return self._represent_mobile(image=b)

    def _represent_mobile(self, image):
        def preprocess_image(image: bytes) -> np.ndarray:
            img_array = np.frombuffer(image, dtype=np.uint8)
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            img = cv2.resize(img, (112, 112))
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img = img.astype(np.float32)
            img = (img - 127.5) / 128.0
            img = np.expand_dims(img, axis=0)
            return img

        img = preprocess_image(image)
        interpreter, input_details, output_details = (
            ml_model["interpreter"],
            ml_model["input_details"],
            ml_model["output_details"],
        )
        interpreter.set_tensor(input_details[0]["index"], img)
        interpreter.invoke()
        encoding = interpreter.get_tensor(output_details[0]["index"])
        return np.squeeze(encoding)
