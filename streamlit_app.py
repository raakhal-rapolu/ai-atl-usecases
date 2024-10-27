# streamlit_app.py
import streamlit as st
import cv2
import base64
import requests
import time

# Define the Flask endpoint URL
FLASK_ENDPOINT = "http://127.0.0.1:8000/use-case-svc/api/v1/reinforce_memory/live_detection"

st.title("Live Detection Stream")
st.text("Captures frames from the webcam every second, sends them to the server, and displays the response.")

# Initialize session state for streaming control
if "streaming" not in st.session_state:
    st.session_state.streaming = False

# Start the webcam capture using OpenCV
cap = cv2.VideoCapture(0)

# Set up columns for side-by-side view
col1, col2 = st.columns([1, 1])

# Placeholder for the live image in the left column
with col1:
    image_placeholder = st.empty()

# Placeholder container for responses in the right column
with col2:
    st.write("Response Stream:")
    response_container = st.empty()

# Custom CSS for auto-scrolling response container
st.markdown(
    """
    <style>
    .response-container {
        max-height: 400px;
        overflow-y: auto;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Button to start/stop the live stream
if st.button("Start Live Stream"):
    st.session_state.streaming = True

if st.button("Stop Live Stream"):
    st.session_state.streaming = False

# List to hold responses for display
responses = []

# Capture frames while streaming is active
while st.session_state.streaming:
    # Capture a frame
    ret, frame = cap.read()
    if not ret:
        st.error("Failed to capture frame from webcam.")
        break

    # Encode the frame as JPEG and then base64
    _, buffer = cv2.imencode('.jpg', frame)
    frame_base64 = base64.b64encode(buffer).decode('utf-8')

    # Send the frame to the Flask backend
    response = requests.post(FLASK_ENDPOINT, json={"frame": frame_base64})

    # Process the response
    if response.status_code == 200:
        try:
            result = response.json()  # Try parsing JSON
            response_text = result.get("response", "No response text available")

            # Append the response text and keep only the latest 10 responses
            responses.append(response_text)
            if len(responses) > 10:
                responses.pop(0)

            # Update the display
            with col1:
                image_placeholder.image(frame, channels="BGR")

            # Update responses in the scrolling container
            with col2:
                response_container.markdown(
                    '<div class="response-container">' +
                    ''.join([f"<p>{msg}</p>" for msg in responses]) +
                    '</div>',
                    unsafe_allow_html=True
                )
        except requests.exceptions.JSONDecodeError:
            st.error("Received a non-JSON response from the server.")
    else:
        st.error(f"Error: Received status code {response.status_code}")

    # Wait for 1 second before capturing the next frame
    time.sleep(1)

# Release the webcam when streaming stops
cap.release()
