import base64
import os

import cv2
from flask import jsonify, send_from_directory, request
from flask import views
from flask_swagger_ui import get_swaggerui_blueprint
import numpy as np

from hairstyler import core


class ImageHandlerView(views.View):
    def parse_image_from_request(self):
        encoded_image = request.get_json()["image"]
        decoded_image = base64.b64decode(encoded_image)
        image = cv2.imdecode(
            np.frombuffer(decoded_image, np.uint8), cv2.IMREAD_COLOR
        )
        return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    def dispatch_request(self):
        raise NotImplementedError


class FaceShapeView(ImageHandlerView):
    methods = ["POST"]

    def __init__(
        self,
        face_shape_interactor: core.IInteractor,
    ):
        self._interactor = face_shape_interactor

    def dispatch_request(self):
        image = self.parse_image_from_request()
        response = self._interactor.response(image)[0]
        face_shape, probability = response.get()
        return jsonify(
            {
                "face_shape": face_shape,
                "probability": str(probability),
            }
        )


class RecommendationView(ImageHandlerView):
    methods = ["POST"]

    def __init__(
        self,
        hairstyle_recommendation_interactor: core.IInteractor,
    ):
        self._interactor = hairstyle_recommendation_interactor

    def dispatch_request(self):
        image = self.parse_image_from_request()
        responses = self._interactor.response(image)
        json_response = []
        for response in responses:
            hairstyle, image, probability = response.get()
            json_response.append(
                {
                    "hairstyle": hairstyle,
                    "image": image,
                    "probability": str(probability),
                }
            )
        return jsonify(json_response)


class SwaggerFileView(views.View):
    init_every_request = False

    def __init__(self, static_path):
        self._static_path = static_path

    def dispatch_request(self):
        return send_from_directory(
            self._static_path, "swagger.json"
        )


# SWAGGER UI blueprint description
SWAGGER_URL = "/docs"
SWAGGER_JSON_URL = "/swagger"
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(SWAGGER_URL, SWAGGER_JSON_URL)
