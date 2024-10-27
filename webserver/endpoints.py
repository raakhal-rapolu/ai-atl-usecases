from flask import request, jsonify, Blueprint
from flask_restx import Resource
from webserver.api_models import multiply_api_model, add_face_parser, detect_face_parser, live_detection_api_model
from webserver.extensions import api
from flask_swagger_ui import get_swaggerui_blueprint
import os
import base64
import requests
from usecases.face_database import FaceDatabase
from usecases.face_identification import add_person_from_image
import os
from werkzeug.utils import secure_filename
import cv2
from ultralytics import YOLO
from usecases.face_prompt_llm import generate_message_with_llm, assist_dementia_patient
from usecases.face_database import FaceDatabase
import face_recognition
import numpy as np

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

@recall_namespace.route('/live_detection')
class LiveDetection(Resource):
    @api.expect(live_detection_api_model)

    def post(self):
        """Process a single frame from the live webcam feed"""
        try:
            # Parse the incoming request data
            data = request.json
            frame_data = data.get("frame")

            if not frame_data:
                return {"error": "No frame data provided"}, 400

            # Decode the base64 frame
            frame_bytes = base64.b64decode(frame_data)
            np_frame = np.frombuffer(frame_bytes, np.uint8)
            frame = cv2.imdecode(np_frame, cv2.IMREAD_COLOR)

            # Run YOLO prediction for object detection
            model = YOLO('models/yolov8n.pt')
            results = model.predict(frame, imgsz=640)
            result = results[0]  # Process the first result
            model_names = model.names

            # Extract detected objects
            boxes = result.boxes
            detected_objects = []
            if boxes is not None and len(boxes) > 0:
                cls_indices = boxes.cls.cpu().numpy().astype(int)
                detected_objects = [model_names[i] for i in cls_indices]

            # Filter sensitive words and prepare the context
            filtered_objects = filter_sensitive_words(detected_objects)
            context = {'objects': filtered_objects}
            image_path = 'current_frame.jpg'
            cv2.imwrite(image_path, frame)

            # Check if a face is among the detected objects
            detected_faces = 'person' in detected_objects
            if detected_faces:
                # Detect and encode faces
                face_locations = face_recognition.face_locations(frame)
                face_encodings = face_recognition.face_encodings(frame, face_locations)

                if face_encodings:
                    face_embedding = face_encodings[0]
                    similar_faces = face_db.find_similar_face(face_embedding)

                    if similar_faces:
                        matched_face = similar_faces[0]
                        context = {
                            "name": f"{matched_face['first_name']} {matched_face['last_name']}",
                            "relation": matched_face['relationship'],
                            "personal_information": matched_face.get('notes', '')
                        }
                    else:
                        context = {
                            "name": "an unfamiliar person",
                            "relation": "unknown",
                            "personal_information": "No additional information available."
                        }

                    # Generate message using the context for a detected face
                    response = generate_message_with_llm(image_path, context)
                else:
                    # No face encodings found
                    context = {
                        "name": "a person",
                        "relation": "unknown",
                        "personal_information": "No additional information available."
                    }
                    response = assist_dementia_patient(image_path, context)
            else:
                # Generate message for non-face frames
                response = assist_dementia_patient(image_path, context)

            return jsonify(response)
        except Exception as e:
            return {"error": str(e)}, 500

def filter_sensitive_words(detected_objects):
    sensitive_words = {'toilet', 'bathroom', 'weapon', 'knife', 'gun'}  # Add more words as needed
    filtered_objects = [obj for obj in detected_objects if obj.lower() not in sensitive_words]
    return filtered_objects