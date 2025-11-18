import os
import pickle
import logging
import numpy as np
from typing import List, Tuple, Optional, Dict
import cv2
from pathlib import Path

logger = logging.getLogger(__name__)

class FaceRecognitionService:
    def __init__(self, config: dict):
        self.config = config
        self.known_face_encodings = []
        self.known_face_metadata = []
        self.model_backend = config['face_recognition']['model_backend']
        self._load_model_backend()
        self._load_known_faces()
    
    def _load_model_backend(self):
        """Load the selected face recognition backend"""
        try:
            if self.model_backend == "face_recognition":
                import face_recognition
                self.face_recognition_lib = face_recognition
            elif self.model_backend == "dlib":
                import dlib
                self.face_recognition_lib = dlib
            elif self.model_backend == "insightface":
                import insightface
                self.face_recognition_lib = insightface
            else:
                raise ValueError(f"Unsupported model backend: {self.model_backend}")
        except ImportError as e:
            logger.error(f"Failed to load {self.model_backend}: {e}")
            raise
    
    def _load_known_faces(self):
        """Load known face encodings from database or disk"""
        known_faces_path = Path(self.config['face_recognition']['known_faces_path'])
        known_faces_path.mkdir(parents=True, exist_ok=True)
        
        encodings_file = known_faces_path / "encodings.pkl"
        if encodings_file.exists():
            try:
                with open(encodings_file, 'rb') as f:
                    data = pickle.load(f)
                    self.known_face_encodings = data['encodings']
                    self.known_face_metadata = data['metadata']
                logger.info(f"Loaded {len(self.known_face_encodings)} known faces")
            except Exception as e:
                logger.error(f"Error loading known faces: {e}")
    
    def save_known_faces(self):
        """Save known face encodings to disk"""
        known_faces_path = Path(self.config['face_recognition']['known_faces_path'])
        encodings_file = known_faces_path / "encodings.pkl"
        
        try:
            with open(encodings_file, 'wb') as f:
                pickle.dump({
                    'encodings': self.known_face_encodings,
                    'metadata': self.known_face_metadata
                }, f)
            logger.info("Saved known faces to disk")
        except Exception as e:
            logger.error(f"Error saving known faces: {e}")
    
    def add_known_face(self, encoding: np.ndarray, metadata: dict):
        """Add a new known face to the system"""
        self.known_face_encodings.append(encoding)
        self.known_face_metadata.append(metadata)
        self.save_known_faces()
    
    def detect_faces(self, image: np.ndarray) -> List[Tuple]:
        """Detect faces in an image"""
        if self.model_backend == "face_recognition":
            face_locations = self.face_recognition_lib.face_locations(
                image, 
                model=self.config['face_recognition']['detection_model']
            )
            return face_locations
        else:
            # Implement other backends
            return []
    
    def encode_face(self, image: np.ndarray, face_location: Tuple) -> np.ndarray:
        """Encode a face into a feature vector"""
        if self.model_backend == "face_recognition":
            encoding = self.face_recognition_lib.face_encodings(
                image, 
                [face_location],
                num_jitters=self.config['face_recognition']['num_jitters']
            )
            return encoding[0] if encoding else None
        else:
            # Implement other backends
            return None
    
    def recognize_face(self, encoding: np.ndarray) -> Tuple[Optional[str], float]:
        """Recognize a face from known encodings"""
        if not self.known_face_encodings:
            return None, 0.0
        
        if self.model_backend == "face_recognition":
            distances = self.face_recognition_lib.face_distance(
                self.known_face_encodings, 
                encoding
            )
            
            if len(distances) > 0:
                min_distance = min(distances)
                if min_distance < self.config['face_recognition']['tolerance']:
                    best_match_idx = np.argmin(distances)
                    student_id = self.known_face_metadata[best_match_idx]['student_id']
                    confidence = 1 - min_distance
                    return student_id, confidence
        
        return None, 0.0