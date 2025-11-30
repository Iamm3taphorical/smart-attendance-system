import time
import logging
import threading
import yaml
import numpy as np

import cv2

from app.services.face_recognition import FaceRecognitionService
from app.services.attendance_service import AttendanceService
from app.services.alert_service import AlertService
from app.core.database import DatabaseManager
from app.web.dashboard import create_app

logger = logging.getLogger(__name__)


class SmartAttendanceSystem:
    def __init__(self, config_path: str = "config.yaml"):
        self.config = self._load_config(config_path)
        self.setup_logging()

        # Initialize services
        self.db_manager = DatabaseManager(self.config['database']['path'])
        self.face_service = FaceRecognitionService(self.config)
        self.attendance_service = AttendanceService(
            self.config['database']['path'],
            self.config
        )
        self.alert_service = AlertService(
            self.config['database']['path'],
            self.config
        )

        self.is_running = False
        self.capture_thread = None
        self.web_thread = None
        # Pass the full config to Flask app so FaceRecognitionService can access it
        self.flask_app = create_app(self.config)

    def _load_config(self, config_path: str) -> dict:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def setup_logging(self):
        logging.basicConfig(
            level=logging.DEBUG if self.config['system'].get('debug') else logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('data/system.log'),
                logging.StreamHandler()
            ]
        )

    def start_camera_capture(self, camera_index: int = 0):
        self.is_running = True
        self.capture_thread = threading.Thread(
            target=self._camera_loop,
            args=(camera_index,),
            daemon=True
        )
        self.capture_thread.start()
        logger.info("Camera capture started")

    def start_web_server(self):
        self.web_thread = threading.Thread(
            target=self._run_flask,
            daemon=True
        )
        self.web_thread.start()
        logger.info("Web server started")

    def _run_flask(self):
        # Disable reloader to avoid main thread issues
        self.flask_app.run(
            host='0.0.0.0', 
            port=5000, 
            debug=self.config['system'].get('debug', False),
            use_reloader=False
        )

    def _camera_loop(self, camera_index: int):
        cap = cv2.VideoCapture(camera_index)

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config['camera']['width'])
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config['camera']['height'])
        cap.set(cv2.CAP_PROP_FPS, self.config['camera']['fps'])

        if not cap.isOpened():
            logger.error(f"Could not open camera {camera_index}")
            return

        logger.info("Camera initialized successfully")

        while self.is_running:
            ret, frame = cap.read()
            if not ret:
                logger.error("Failed to capture frame")
                break

            self._process_frame(frame)
            time.sleep(1 / max(1, int(self.config['camera'].get('fps', 10))))

        cap.release()
        logger.info("Camera capture stopped")

    def _process_frame(self, frame: np.ndarray):
        try:
            # Check for updates to known faces (hot-reload)
            self.face_service._load_known_faces()
            
            face_locations = self.face_service.detect_faces(frame)

            for face_location in face_locations:
                encoding = self.face_service.encode_face(frame, face_location)
                if encoding is not None:
                    student_id, confidence = self.face_service.recognize_face(encoding)

                    if student_id:
                        self.attendance_service.record_attendance(
                            student_id=student_id,
                            confidence=confidence,
                            location=self.config.get('camera', {}).get('location', 'Main Entrance'),
                            device_id=self.config.get('camera', {}).get('device_id', 'CAM_001')
                        )
                    else:
                        # Save small crop for unknown face alert
                        try:
                            top, right, bottom, left = face_location
                            face_img = frame[top:bottom, left:right]
                        except Exception:
                            face_img = frame

                        self.alert_service.handle_unknown_face(encoding, face_img, self.config.get('camera', {}).get('location'))

        except Exception:
            logger.exception("Error processing frame")

    def stop(self):
        self.is_running = False
        if self.capture_thread:
            self.capture_thread.join(timeout=5.0)
        logger.info("Smart Attendance System stopped")


def main():
    system = SmartAttendanceSystem()

    try:
        logger.info("Starting Smart Attendance System")
        # Start web server
        system.start_web_server()
        
        # Start camera
        system.start_camera_capture(system.config['camera'].get('source', 0))
        
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutdown signal received")
    finally:
        system.stop()


if __name__ == '__main__':
    main()
