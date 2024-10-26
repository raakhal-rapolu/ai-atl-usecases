import cv2
import numpy as np
import threading
import queue
import logging
from ultralytics import YOLO

class DetectionStream:
    def __init__(self):
        self.model = YOLO('models/yolov8n.pt')  # Ensure this model file exists
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
