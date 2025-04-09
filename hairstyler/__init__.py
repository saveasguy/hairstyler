import os

from flask import Flask
from flask_cors import CORS

from hairstyler import ai
from hairstyler import core
from hairstyler.hairstyles import RedisDB
from hairstyler import views


MODULE_DIR = os.path.dirname(__file__)
REDIS_HOST = os.getenv("REDIS_SERVICE_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_SERVICE_PORT", 6379))
db_repository = RedisDB(REDIS_HOST, REDIS_PORT, MODULE_DIR + "/../data/hairstyles_data.json") 
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
    db_repository,
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
