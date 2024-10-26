from flask_restx import fields
from flask_restx import reqparse
from werkzeug.datastructures import FileStorage
from webserver.extensions import api

multiply_api_model = api.model('Multiply two numbers', {
    'a': fields.Integer,
    'b': fields.Integer
})

# Parser for /add_known_face endpoint
add_face_parser = reqparse.RequestParser()
add_face_parser.add_argument('first_name', type=str, required=True, help='First name of the person')
add_face_parser.add_argument('last_name', type=str, required=True, help='Last name of the person')
add_face_parser.add_argument('relationship', type=str, required=True, help='Relationship with the patient')
add_face_parser.add_argument('personal_context', type=str, required=True, help='Mutual interest')
add_face_parser.add_argument('image', type=FileStorage, location='files', required=True, help='Image file')

# Parser for /detect_unknown_face endpoint
detect_face_parser = reqparse.RequestParser()
detect_face_parser.add_argument('image', type=FileStorage, location='files', required=True, help='Image file')
