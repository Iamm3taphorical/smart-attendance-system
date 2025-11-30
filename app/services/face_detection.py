"""Simple face detection wrapper using `face_recognition` when available."""
import logging
from typing import List, Tuple
try:
	import face_recognition
except Exception:
	face_recognition = None

logger = logging.getLogger(__name__)


def detect_faces(image) -> List[Tuple[int, int, int, int]]:
	if face_recognition is None:
		logger.warning('face_recognition not installed; detect_faces returns empty list')
		return []
	return face_recognition.face_locations(image)
