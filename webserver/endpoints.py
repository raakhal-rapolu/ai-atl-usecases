from flask import request, jsonify, Blueprint
from flask_restx import Resource
from webserver.api_models import multiply_api_model, add_face_parser, detect_face_parser
from webserver.extensions import api
from flask_swagger_ui import get_swaggerui_blueprint
import os
import base64
import requests
from usecases.face_database import FaceDatabase
from usecases.face_identification import add_person_from_image
from usecases.face_prompt_llm import generate_message_with_llm
from usecases.detection_stream import DetectionStream
import os
from werkzeug.utils import secure_filename

# Initialize components
face_db = FaceDatabase()

# Define the temporary directory
TEMP_DIR = 'tmp'

# Create the directory if it doesn't exist
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)


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
    @api.expect(add_face_parser)
    def post(self):
        """Add a known face to the database"""
        try:
            args = add_face_parser.parse_args()
            first_name = args['first_name']
            last_name = args['last_name']
            relationship = args['relationship']
            image_file = args['image']
            notes = args['personal_context']

            # Save the uploaded image to a temporary location
            image_filename = secure_filename(image_file.filename)
            image_path = os.path.join(TEMP_DIR, image_filename)
            image_file.save(image_path)

            # Create face embedding from image and add to DB
            face_embedding = add_person_from_image(image_path)
            patient_id = face_db.add_patient(first_name, last_name)
            person_id = face_db.add_person(
                patient_id, first_name, last_name, relationship, face_embedding, notes
            )

            # Remove the temporary image file
            os.remove(image_path)

            # Return data directly, not a Response object
            return {"message": "Known face added", "person_id": person_id}
        except Exception as e:
            return {"error": str(e)}, 500


@recall_namespace.route('/detect_unknown_face')
class DetectUnknownFace(Resource):
    @api.expect(detect_face_parser)
    def post(self):
        """Detect an unknown face and match it with known faces"""
        try:
            args = detect_face_parser.parse_args()
            image_file = args['image']

            # Save the uploaded image to a temporary location
            image_filename = secure_filename(image_file.filename)
            image_path = os.path.join(TEMP_DIR, image_filename)
            image_file.save(image_path)

            # Generate face embedding for unknown face
            face_embedding = add_person_from_image(image_path)
            similar_faces = face_db.find_similar_face(face_embedding)

            if similar_faces:
                best_match = similar_faces[0]
                context = {
                    "name": best_match['first_name'],
                    "relation": best_match['relationship'],
                    "personal_information": best_match.get('notes', '')
                }

                # Generate the message using the LLM
                llm_response = generate_message_with_llm(image_path, context)

                # Remove the temporary image file
                os.remove(image_path)

                return llm_response
            else:
                # Remove the temporary image file
                os.remove(image_path)
                return {"message": "No similar faces found"}
        except Exception as e:
            # if image_path:
            #     # Remove the temporary image file if it exists
            #     if os.path.exists(image_path):
            #         os.remove(image_path)
            return {"error": str(e)}, 500


# @recall_namespace.route('/live_detection')
# class LiveDetection(Resource):
#     def get(self):
#         """Fetch the latest detection frame as base64"""
#         # Start the detection stream
#         # detection_stream.start()
#
#         # Get the latest frame
#         frame_data = detection_stream.get_latest_frame()
#         if frame_data:
#             encoded_frame = base64.b64encode(frame_data).decode('utf-8')
#             response = jsonify({"frame": encoded_frame})
#
#             # Stop the detection stream after processing
#             detection_stream.stop()
#             return response
#
#         # Stop the detection stream if no frame is available
#         detection_stream.stop()
#         return jsonify({"error": "No frame available"}), 404