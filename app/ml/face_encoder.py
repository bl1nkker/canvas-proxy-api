import numpy as np
import cv2
from ml import ml_model


def preprocess_image(image: bytes) -> np.ndarray:
    img_array = np.frombuffer(image, dtype=np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    img = cv2.resize(img, (112, 112))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = img.astype(np.float32)
    img = (img - 127.5) / 128.0
    img = np.expand_dims(img, axis=0)
    return img


def get_face_encoding(image: bytes) -> np.ndarray:
    img = preprocess_image(image)
    interpreter, input_details, output_details = ml_model.get_interpreter()
    interpreter.set_tensor(input_details[0]["index"], img)
    interpreter.invoke()
    encoding = interpreter.get_tensor(output_details[0]["index"])
    return np.squeeze(encoding)
