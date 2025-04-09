import json
import os
import unittest
from typing import List

import cv2
import numpy as np

import hairstyler.ai as ai
import hairstyler.core as core


class MockJSONHairstylesRepository(core.IDatabaseRepository):
    def __init__(self, json_path: str):
        with open(json_path, encoding="utf-8") as json_file:
            self._hairstyles = json.load(json_file)

    def get_featured_hairstyles(self, feature: str) -> List[str]:
        if not feature in self._hairstyles:
            raise ValueError(f"'{feature}' feature doesn't exist!")
        return self._hairstyles[feature]

    def get_hairstyle_image(self, hairstyle: str) -> str:
        return "img"


class TestAI(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestAI, self).__init__(*args, **kwargs)
        module_dir = os.path.dirname(__file__)
        self.face_recognizer_repo = ai.FaceRecognizerRepository(
            module_dir + "/../ai/haarcascade_frontalface_default.xml"
        )
        self.face_recognizer_proxy_repo = ai.FaceRecognizerProxyRepository(
            self.face_recognizer_repo
        )
        self.face_shape_classifier_repo = ai.FaceShapeClassifierRepository(
            module_dir + "/../ai/face_shape_classifier.h5"
        )
        self.hairstyles_repo = MockJSONHairstylesRepository(
            module_dir + "/hairstyles_files/fake_hairstyles.json"
        )

    def test_image_recognition(self):
        face_recognizer = self.face_recognizer_repo.get()
        mbappe_image = cv2.imread("test/images/mbappe.jpg")
        mbappe_image = cv2.cvtColor(mbappe_image, cv2.COLOR_BGR2RGB)
        _ = face_recognizer(np.asarray(mbappe_image))
        _ = face_recognizer(np.asarray(mbappe_image), (190, 250))

    def test_image_recognition_proxy(self):
        face_recognizer_proxy = self.face_recognizer_proxy_repo.get()
        mbappe_image = cv2.imread("test/images/mbappe.jpg")
        mbappe_image = cv2.cvtColor(mbappe_image, cv2.COLOR_BGR2RGB)
        _ = face_recognizer_proxy(mbappe_image)
        _ = face_recognizer_proxy(mbappe_image), (190, 250)

    def test_face_shape_classification(self):
        interactor = core.FaceShapeInteractor(
            self.face_recognizer_repo,
            self.face_shape_classifier_repo,
        )
        mbappe_image = cv2.imread("test/images/mbappe.jpg")
        mbappe_image = cv2.cvtColor(mbappe_image, cv2.COLOR_BGR2RGB)
        response = interactor.response(mbappe_image)
        self.assertEqual(response[0].get()[0], "round_face")

    def test_hairstyle_recommendation(self):
        interactor = core.HairstyleRecommendationInteractor(
            self.hairstyles_repo,
            self.face_recognizer_repo,
            self.face_shape_classifier_repo,
        )
        mbappe_image = cv2.imread("test/images/mbappe.jpg")
        mbappe_image = cv2.cvtColor(mbappe_image, cv2.COLOR_BGR2RGB)
        response = interactor.response(mbappe_image)
        self.assertEqual(response[0].get()[0], "round_hair")
