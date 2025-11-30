import time
import cv2
import numpy as np
from app.services.face_recognition import FaceRecognitionService


def benchmark_face_recognition():
	"""Benchmark face recognition performance"""
	config = {
		'face_recognition': {
			'model_backend': 'face_recognition',
			'detection_model': 'hog',
			'tolerance': 0.6,
			'num_jitters': 1,
			'known_faces_path': 'data/known_faces/'
		}
	}
    
	face_service = FaceRecognitionService(config)
    
	# Test with sample images
	test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    
	# Benchmark face detection
	start_time = time.time()
	for _ in range(100):
		face_locations = face_service.detect_faces(test_image)
	detection_time = (time.time() - start_time) / 100
    
	print(f"Average face detection time: {detection_time:.4f}s")
	print(f"Detection FPS: {1/detection_time:.2f}")
    
	# Benchmark face encoding
	if face_locations:
		start_time = time.time()
		for _ in range(100):
			encoding = face_service.encode_face(test_image, face_locations[0])
		encoding_time = (time.time() - start_time) / 100
        
		print(f"Average face encoding time: {encoding_time:.4f}s")
		print(f"Encoding FPS: {1/encoding_time:.2f}")


if __name__ == "__main__":
	benchmark_face_recognition()
