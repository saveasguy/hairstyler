import threading
from typing import Tuple, Union

import cv2
import numpy as np
import tensorflow as tf

from hairstyler import core


class FaceUnrecognizedError(Exception):
    pass


class FaceRecognizer(core.IAIFilter):
    def __init__(self, cascade: cv2.CascadeClassifier):
        self._cascade = cascade
        self._mutex = threading.Lock()

    def input_shape(self) -> Union[Tuple, None]:
        return None

    def eval(
        self, input_: np.ndarray, output_shape: Union[Tuple, None] = None
    ) -> np.ndarray:
        face_region = self.get_face_region(input_)
        if output_shape:
            return self.extract_resized_face_region_from_image(
                input_, face_region, output_shape[:2]
            )
        return self.extract_face_region_from_image(input_, face_region)

    def get_face_region(self, input_: np.array) -> Tuple:
        gray = cv2.cvtColor(input_, cv2.COLOR_RGB2GRAY)
        with self._mutex:
            faces = self._cascade.detectMultiScale(
                gray, scaleFactor=1.3, minSize=(100, 100)
            )
        if len(faces) == 0:
            raise FaceUnrecognizedError("No faces are recognized!")
        return max(faces, key=lambda item: (item[2], item[3]))

    def extract_face_region_from_image(
        self, image: np.ndarray, face_region: Tuple
    ) -> np.ndarray:
        x = face_region[0]
        y = face_region[1]
        width = face_region[2]
        height = face_region[3]
        return image[y : y + height, x : x + width]

    def extract_resized_face_region_from_image(
        self, image: np.ndarray, face_region: Tuple, size: Tuple
    ) -> np.ndarray:
        sides_ratio = size[1] / size[0]
        x = face_region[0]
        y = face_region[1]
        ratio_width = face_region[2]
        ratio_height = int(ratio_width * sides_ratio)
        if ratio_height > image.shape[0]:
            ratio_width = int(ratio_height / sides_ratio)
            difference = face_region[2] - ratio_width
            x += difference // 2
        else:
            ratio_height = int(ratio_width * sides_ratio)
            difference = ratio_height - face_region[3]
            y -= min(y, difference // 2)
        extracted_face = image[y : y + ratio_height, x : x + ratio_width]
        return cv2.resize(extracted_face, size)


class FaceRecognizerProxy(core.IAIFilter):
    def __init__(self, face_recognizer: FaceRecognizer):
        self._face_recognizer = face_recognizer
        self._image = None
        self._face_region = None

    def input_shape(self) -> Union[Tuple, None]:
        return self._face_recognizer.input_shape()

    def eval(
        self, input_: np.ndarray, output_shape: Union[Tuple, None] = None
    ) -> np.ndarray:
        if not self._image is input_:
            self._image = input_
            self._face_region = self._face_recognizer.get_face_region(
                self._image
            )
        if output_shape:
            return (
                self._face_recognizer.extract_resized_face_region_from_image(
                    self._image, self._face_region, output_shape[:2]
                )
            )
        return self._face_recognizer.extract_face_region_from_image(
            self._image, self._face_region
        )


class FaceShapeClassifier(core.IAIFilter):
    def __init__(self, model: tf.keras.models.Model):
        self._classifier = model
        self._mutex = threading.Lock()
        self._input_width = 190
        self._input_height = 250
        self._labels = (
            "heart_face",
            "oblong_face",
            "oval_face",
            "round_face",
            "square_face",
        )

    def input_shape(self):
        return (self._input_width, self._input_height, 1)

    def eval(
        self, input_: np.ndarray, output_shape: Union[Tuple, None] = None
    ) -> np.ndarray:
        face_image = cv2.cvtColor(input_, cv2.COLOR_RGB2GRAY)
        face_image = face_image.reshape(
            1, self._input_height, self._input_width, 1
        )
        face_image = face_image / 255  # convert to float
        with self._mutex:
            probabilities = self._classifier(face_image)
        probabilities = probabilities.numpy()[0]
        if output_shape and (
            len(output_shape) == 0 or output_shape[0] > len(probabilities)
        ):
            raise ValueError(
                f"output_shape({output_shape}) should contain single value \
                and value should be less than FaceShapeClassifier \
                output({len(probabilities)})!"
            )
        labeled_probabilities = zip(self._labels, probabilities.tolist())
        labeled_probabilities = sorted(
            labeled_probabilities, key=lambda x: x[1], reverse=True
        )
        labeled_probabilities = np.array(labeled_probabilities, dtype=object)
        if output_shape:
            return labeled_probabilities[: output_shape[0]]
        return labeled_probabilities


class FaceRecognizerRepository(core.IAIRepository):
    def __init__(self, haarcascade_path: str):
        cascade = cv2.CascadeClassifier(haarcascade_path)
        self._face_recognizer = FaceRecognizer(cascade)

    def get(self) -> core.IAIFilter:
        return self._face_recognizer

    def get_face_recognizer(self) -> FaceRecognizer:
        return self._face_recognizer


class FaceRecognizerProxyRepository(core.IAIRepository):
    def __init__(self, face_recognizer_repository: FaceRecognizerRepository):
        self._face_recognizer_repository = face_recognizer_repository

    def get(self) -> core.IAIFilter:
        return FaceRecognizerProxy(
            self._face_recognizer_repository.get_face_recognizer()
        )


class FaceShapeClassifierRepository(core.IAIRepository):
    def __init__(self, model_path: str):
        model = tf.keras.models.load_model(model_path)
        self._classifier = FaceShapeClassifier(model)

    def get(self) -> core.IAIFilter:
        return self._classifier
