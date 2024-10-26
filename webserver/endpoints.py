from flask import request, jsonify, Blueprint
from flask_restx import Resource
from webserver.api_models import multiply_api_model, add_face_model, detect_face_model
from webserver.extensions import api
from flask_swagger_ui import get_swaggerui_blueprint
import os
import base64
import requests
from usecases.face_database import FaceDatabase
from usecases.face_identification import add_person_from_image
from usecases.detection_stream import DetectionStream

# Initialize components
face_db = FaceDatabase()
detection_stream = DetectionStream()
detection_stream.start()

API_VERSION = '/api/v1'
CATALOG_MODULE = '/use-case-svc'
CORE_PREFIX = CATALOG_MODULE + API_VERSION

# Initialize Blueprint and Swagger UI
blueprint = Blueprint('api', __name__, url_prefix=CORE_PREFIX)
api.init_app(blueprint)

SWAGGER_URL = CORE_PREFIX
API_URL = CORE_PREFIX + '/swagger.json'
swagger_ui_blueprint = get_swaggerui_blueprint(SWAGGER_URL, API_URL, config={'app_name': 'ReCallMe'})

# Define namespace
recall_namespace = api.namespace(name='reinforce_memory')
api.add_namespace(recall_namespace)


@recall_namespace.route('/multiply')
class Multiply(Resource):
    @recall_namespace.doc(security="Basic Auth")
    @api.expect(multiply_api_model)
    def post(self):
        """Multiply two numbers"""
        try:
            data = request.json
            a = data['a']
            b = data['b']
            result = a * b
            return jsonify({"result": result})
        except Exception as e:
            return jsonify({"error": str(e)}), 500


@recall_namespace.route('/add_known_face')
class AddKnownFace(Resource):
    @api.expect(add_face_model)
    def post(self):
        """Add a known face to the database"""
        try:
            data = request.json
            first_name = data.get('first_name')
            last_name = data.get('last_name')
            relationship = data.get('relationship')
            image_path = data.get('image_path')

            # Create face embedding from image and add to DB
            face_embedding = add_person_from_image(image_path)
            patient_id = face_db.add_patient(first_name, last_name)
            person_id = face_db.add_person(patient_id, first_name, last_name, relationship, face_embedding)

            return jsonify({"message": "Known face added", "person_id": person_id})
        except Exception as e:
            return jsonify({"error": str(e)}), 500


@recall_namespace.route('/detect_unknown_face')
class DetectUnknownFace(Resource):
    @api.expect(detect_face_model)
    def post(self):
        """Detect an unknown face and match it with known faces"""
        try:
            data = request.json
            image_path = data.get('image_path')

            # Generate face embedding for unknown face
            face_embedding = add_person_from_image(image_path)
            similar_faces = face_db.find_similar_face(face_embedding)

            # Send results to external URL if similar faces found
            if similar_faces:
                context = {"faces": similar_faces}
                response = requests.post(os.getenv("LLM_API_URL"), json=context)
                if response.status_code == 200:
                    return response.json()
                else:
                    return jsonify({"error": "Failed to call LLM API"}), 502
            else:
                return jsonify({"message": "No similar faces found"})
        except Exception as e:
            return jsonify({"error": str(e)}), 500


@recall_namespace.route('/live_detection')
class LiveDetection(Resource):
    def get(self):
        """Fetch the latest detection frame as base64"""
        frame_data = detection_stream.get_latest_frame()
        if frame_data:
            encoded_frame = base64.b64encode(frame_data).decode('utf-8')
            return jsonify({"frame": encoded_frame})
        return jsonify({"error": "No frame available"}), 404
