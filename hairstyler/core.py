from typing import List, Tuple, Union

import numpy as np


class IAIFilter:
    def input_shape(self) -> Union[Tuple, None]:
        raise NotImplementedError

    def eval(
        self, input_: np.ndarray, output_shape: Union[Tuple, None] = None
    ) -> np.ndarray:
        raise NotImplementedError

    def __call__(
        self, input_: np.ndarray, output_shape: Union[Tuple, None] = None
    ) -> np.ndarray:
        return self.eval(input_, output_shape)


class IAIRepository:
    def get(self) -> IAIFilter:
        raise NotImplementedError


class IDatabaseRepository:
    def get_featured_hairstyles(self, feature: str) -> List[str]:
        raise NotImplementedError

    def get_hairstyle_image(self, hairstyle: str) -> str:
        raise NotImplementedError


class IResponse:
    def get(self) -> Tuple:
        raise NotImplementedError


class FeatureProbability(IResponse):
    def __init__(self, feature: str, probability: float):
        self._feature = feature
        self._probability = probability

    def get(self) -> Tuple:
        return (self._feature, self._probability)


class HairstyleRecommendation(IResponse):
    def __init__(self, hairstyle: str, image: str, probability: float):
        self._hairstyle = hairstyle
        self._image = image
        self._probablity = probability

    def get(self) -> Tuple:
        return (self._hairstyle, self._image, self._probablity)


class IInteractor:
    def response(self, image: np.ndarray) -> List[IResponse]:
        raise NotImplementedError


class FaceShapeInteractor(IInteractor):
    def __init__(
        self,
        face_recognizer_repository: IAIRepository,
        face_shape_classifier_repository: IAIRepository,
    ):
        self._recognizer_repository = face_recognizer_repository
        self._classifier_repository = face_shape_classifier_repository

    def response(self, image: np.ndarray) -> List[IResponse]:
        recognizer = self._recognizer_repository.get()
        classifier = self._classifier_repository.get()
        face_image = recognizer(image, classifier.input_shape())
        face_shape, probability = classifier(face_image, (1,))[0]
        return [FeatureProbability(face_shape, probability)]


class HairstyleRecommendationInteractor(IInteractor):
    def __init__(
        self,
        db: IDatabaseRepository,
        face_recognizer_repository: IAIRepository,
        face_shape_classifier_repository: IAIRepository,
    ):
        self._db = db
        self._recognizer_repository = face_recognizer_repository
        self._classifier_repository = face_shape_classifier_repository

    def response(self, image: np.ndarray) -> List[IResponse]:
        recognizer = self._recognizer_repository.get()
        classifier = self._classifier_repository.get()
        face_image = recognizer(image, classifier.input_shape())
        face_features = classifier(face_image)
        result = {}
        for feature, probability in face_features:
            fitting_hairstyles = self._db.get_featured_hairstyles(feature)
            for hairstyle in fitting_hairstyles:
                if not hairstyle in result:
                    result[hairstyle] = probability
                else:
                    result[hairstyle] = max(result[hairstyle], probability)
        labeled_probabilities = [
            HairstyleRecommendation(
                hairstyle,
                self._db.get_hairstyle_image(hairstyle),
                probability,
            )
            for hairstyle, probability in result.items()
        ]
        return sorted(
            labeled_probabilities, key=lambda x: x.get()[2], reverse=True
        )
