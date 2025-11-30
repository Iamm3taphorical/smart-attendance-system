import sys
import os
import cv2
import numpy as np
import logging

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.face_recognition import FaceRecognitionService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_pipeline():
    config = {
        'face_recognition': {
            'model_backend': 'face_recognition',
            'detection_model': 'hog',
            'num_jitters': 1,
            'tolerance': 0.6,
            'known_faces_path': 'data/known_faces'
        }
    }

    try:
        service = FaceRecognitionService(config)
        logger.info("FaceRecognitionService initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize service: {e}")
        return

    # Create a dummy image with a face (using a simple drawing or just checking if it runs without crashing on empty input)
    # Since we can't easily generate a real face, we will test the structure and error handling
    
    # Create a black image
    img = np.zeros((300, 300, 3), dtype=np.uint8)
    
    try:
        faces = service.detect_faces(img)
        logger.info(f"Detection ran successfully (found {len(faces)} faces)")
    except Exception as e:
        logger.error(f"Detection failed: {e}")

    logger.info("Pipeline verification complete")

if __name__ == "__main__":
    verify_pipeline()
