import numpy as np
import face_recognition

def add_person_from_image(image_path: str) -> np.ndarray:
    """Extract face embedding from an image file"""
    # Load the image file
    image = face_recognition.load_image_file(image_path)
    if image is None:
        raise ValueError(f"Image at path {image_path} could not be read")

    # Detect face locations in the image
    face_locations = face_recognition.face_locations(image)
    if not face_locations:
        raise ValueError("No face found in the image")

    # Get the face embedding for the first face found
    face_encodings = face_recognition.face_encodings(image, face_locations)
    if not face_encodings:
        raise ValueError("Could not compute face embedding")

    face_embedding = face_encodings[0]

    return face_embedding
