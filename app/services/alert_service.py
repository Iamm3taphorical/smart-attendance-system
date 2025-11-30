import sqlite3
import logging
from pathlib import Path
import time
import base64
from typing import Optional
import numpy as np
import pickle

logger = logging.getLogger(__name__)


class AlertService:
    def __init__(self, db_path: str, config: dict):
        self.db_path = db_path
        self.config = config
        # ensure data directories
        Path('data/unknown_faces').mkdir(parents=True, exist_ok=True)
        Path(self.config.get('face_recognition', {}).get('known_faces_path', 'data/known_faces')).mkdir(parents=True, exist_ok=True)

    def _execute(self, sql: str, params: tuple = ()): 
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            conn.commit()

    def create_alert(self, alert_type: str, message: str, severity: str = 'info'):
        try:
            self._execute(
                'INSERT INTO alerts (type, message, severity) VALUES (?, ?, ?)',
                (alert_type, message, severity)
            )
            logger.info(f"Alert created: {alert_type} - {message}")
        except Exception:
            logger.exception("Failed to create alert")

    def handle_unknown_face(self, encoding: Optional[np.ndarray], image: Optional[bytes], location: Optional[str] = None):
        """Save unknown face info and create an alert. `image` may be raw bytes or a numpy array saved by caller."""
        ts = int(time.time())
        image_path = None

        try:
            if image is not None:
                # allow either bytes or numpy array
                img_dir = Path('data/unknown_faces')
                img_dir.mkdir(parents=True, exist_ok=True)
                image_path = str(img_dir / f"unknown_{ts}.jpg")
                # if bytes, write directly
                if isinstance(image, (bytes, bytearray)):
                    with open(image_path, 'wb') as f:
                        f.write(image)
                else:
                    # assume numpy array (BGR), use cv2 if available
                    try:
                        import cv2
                        cv2.imwrite(image_path, image)
                    except Exception:
                        # fallback: attempt to pickle
                        with open(image_path + '.pkl', 'wb') as f:
                            pickle.dump(image, f)

            encoding_blob = None
            if encoding is not None:
                try:
                    encoding_blob = pickle.dumps(encoding)
                except Exception:
                    encoding_blob = None

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO unknown_faces (face_encoding, location, image_path, processed)
                    VALUES (?, ?, ?, 0)
                ''', (encoding_blob, location, image_path))
                conn.commit()

            self.create_alert('unknown_face', f'Unknown face seen at {location or "unknown"}', 'warning')

        except Exception:
            logger.exception('Failed to handle unknown face')
