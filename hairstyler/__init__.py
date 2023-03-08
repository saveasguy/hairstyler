import os

from flask import Flask
from flask_cors import CORS

from hairstyler import ai
from hairstyler import core
from hairstyler.hairstyles import FeaturedHairstylesDB, HairstyleImagesDB
from hairstyler import views


MODULE_DIR = os.path.dirname(__file__)
print(MODULE_DIR)
featured_hairstyles_repository = FeaturedHairstylesDB(
    MODULE_DIR + "/../data/database.sqlite"
)
hairstyle_images_repository = HairstyleImagesDB(
    MODULE_DIR + "/../data/database.sqlite"
)
face_recognizer_repository = ai.FaceRecognizerRepository(
    MODULE_DIR + "/../ai/haarcascade_frontalface_default.xml"
)
face_shape_classifier_repository = ai.FaceShapeClassifierRepository(
    MODULE_DIR + "/../ai/face_shape_classifier.h5"
)

face_shape_interactor = core.FaceShapeInteractor(
    face_recognizer_repository, face_shape_classifier_repository
)
recommendation_interactor = core.HairstyleRecommendationInteractor(
    featured_hairstyles_repository,
    hairstyle_images_repository,
    face_recognizer_repository,
    face_shape_classifier_repository,
)

app = Flask(__name__)
CORS(app)
app.add_url_rule(
    "/faceshape",
    view_func=views.FaceShapeView.as_view("face_shape", face_shape_interactor),
)
app.add_url_rule(
    "/recommendation",
    view_func=views.RecommendationView.as_view(
        "recommendation", recommendation_interactor
    ),
)
app.add_url_rule(
    "/swagger",
    view_func=views.SwaggerFileView.as_view(
        "swagger", MODULE_DIR + "/../static"
    ),
)
app.register_blueprint(views.SWAGGERUI_BLUEPRINT)
