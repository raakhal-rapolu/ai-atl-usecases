from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import cv2
import numpy as np
from ultralytics import YOLO
import base64
import threading
import asyncio
import logging
import queue

# Initialize FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create a more robust HTML page with error handling and connection status
HTML_CONTENT = """
<!DOCTYPE html>
<html>
    <head>
        <title>Detection Stream</title>
        <style>
            .container {
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                text-align: center;
            }
            #video-stream {
                width: 100%;
                max-width: 800px;
                height: auto;
                border: 1px solid #ccc;
            }
            .status {
                margin: 10px 0;
                padding: 10px;
                border-radius: 4px;
            }
            .connected {
                background-color: #d4edda;
                color: #155724;
            }
            .disconnected {
                background-color: #f8d7da;
                color: #721c24;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Live Detection Stream</h1>
            <div id="connection-status" class="status disconnected">Connecting...</div>
            <img id="video-stream" src="">
        </div>
        
        <script>
            const statusDiv = document.getElementById('connection-status');
            const img = document.getElementById('video-stream');
            let ws;
            
            function connect() {
                ws = new WebSocket("ws://" + window.location.host + "/ws");
                
                ws.onopen = function() {
                    statusDiv.textContent = 'Connected';
                    statusDiv.className = 'status connected';
                };
                
                ws.onclose = function() {
                    statusDiv.textContent = 'Disconnected - Retrying...';
                    statusDiv.className = 'status disconnected';
                    setTimeout(connect, 1000);
                };
                
                ws.onerror = function(err) {
                    console.error('Socket encountered error: ', err.message, 'Closing socket');
                    ws.close();
                };
                
                ws.onmessage = function(event) {
                    img.src = "data:image/jpeg;base64," + event.data;
                };
            }
            
            connect();
        </script>
    </body>
</html>
"""

class DetectionStream:
    def __init__(self):
        self.model = YOLO('models/yolov8n.pt')
        self.frame_queue = queue.Queue(maxsize=10)
        self.processed_frame = None
        self.running = True
        self.lock = threading.Lock()
        
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def list_cameras(self):
        """List all available cameras"""
        available_cameras = []
        for i in range(10):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                ret, _ = cap.read()
                if ret:
                    available_cameras.append(i)
                cap.release()
        return available_cameras

    def capture_frames(self):
        """Capture frames from camera"""
        cameras = self.list_cameras()
        if not cameras:
            self.logger.error("No cameras found!")
            return

        cap = cv2.VideoCapture(cameras[0])
        
        # Set lower resolution for better performance
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        self.logger.info(f"Started capture on camera {cameras[0]}")

        try:
            while self.running:
                ret, frame = cap.read()
                if ret:
                    # Resize frame for better performance
                    frame = cv2.resize(frame, (640, 480))
                    
                    if self.frame_queue.full():
                        try:
                            self.frame_queue.get_nowait()
                        except queue.Empty:
                            pass
                    self.frame_queue.put(frame)
                else:
                    self.logger.warning("Failed to capture frame")
                    break
        finally:
            cap.release()

    def process_frames(self):
        """Process frames with YOLO detection"""
        while self.running:
            try:
                frame = self.frame_queue.get(timeout=1)
                
                # Run YOLO detection
                results = self.model(frame)
                
                # Draw results on frame
                annotated_frame = results[0].plot()
                
                # Convert to smaller JPEG for faster transmission
                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 80]
                _, buffer = cv2.imencode('.jpg', annotated_frame, encode_param)
                
                # Update processed frame
                with self.lock:
                    self.processed_frame = buffer
                    
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Error processing frame: {e}")

    def get_latest_frame(self):
        """Get the latest processed frame"""
        with self.lock:
            return self.processed_frame

    def start(self):
        """Start the detection stream"""
        self.capture_thread = threading.Thread(target=self.capture_frames)
        self.process_thread = threading.Thread(target=self.process_frames)
        
        self.capture_thread.start()
        self.process_thread.start()

    def stop(self):
        """Stop the detection stream"""
        self.running = False
        if hasattr(self, 'capture_thread'):
            self.capture_thread.join()
        if hasattr(self, 'process_thread'):
            self.process_thread.join()

# Create detection stream instance
detection_stream = DetectionStream()

@app.on_event("startup")
async def startup_event():
    """Start the detection stream when the app starts"""
    detection_stream.start()

@app.on_event("shutdown")
async def shutdown_event():
    """Stop the detection stream when the app shuts down"""
    detection_stream.stop()

@app.get("/", response_class=HTMLResponse)
async def get_index():
    """Serve the HTML page"""
    return HTMLResponse(content=HTML_CONTENT)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for streaming video"""
    await websocket.accept()
    
    try:
        while True:
            frame_data = detection_stream.get_latest_frame()
            if frame_data is not None:
                # Send the JPEG buffer directly
                await websocket.send_text(base64.b64encode(frame_data).decode('utf-8'))
            await asyncio.sleep(0.033)  # ~30 FPS
    except Exception as e:
        logging.error(f"WebSocket error: {e}")
    finally:
        await websocket.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")