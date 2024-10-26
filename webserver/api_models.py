from flask_restx import fields
from flask_restx import reqparse
from werkzeug.datastructures import FileStorage
from webserver.extensions import api

multiply_api_model = api.model('Multiply two numbers', {
    'a': fields.Integer,
    'b': fields.Integer
})

# Model for adding a known face
add_face_model = api.model('AddKnownFace', {
    'first_name': fields.String(required=True, description="First name of the person"),
    'last_name': fields.String(required=True, description="Last name of the person"),
    'relationship': fields.String(required=True, description="Relationship with the patient"),
    'image_path': fields.String(required=True, description="Path to the person's image")
})

# Model for detecting an unknown face
detect_face_model = api.model('DetectUnknownFace', {
    'image_path': fields.String(required=True, description="Path to the unknown person's image")
})