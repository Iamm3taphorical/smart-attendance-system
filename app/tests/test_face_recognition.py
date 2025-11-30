import numpy as np
from app.services.face_recognition import FaceRecognitionService


def test_load_known_faces_empty(tmp_path, monkeypatch):
	# Provide minimal config with temp known_faces path
	config = {'face_recognition': {'model_backend': 'face_recognition', 'detection_model': 'hog', 'num_jitters': 1, 'tolerance': 0.6, 'known_faces_path': str(tmp_path)}}
	# Monkeypatch face_recognition import if not present
	try:
		import face_recognition  # noqa: F401
	except Exception:
		import types
		fr = types.SimpleNamespace()
		fr.face_locations = lambda img, model=None: []
		fr.face_encodings = lambda img, locs, num_jitters=1: []
		fr.face_distance = lambda known, enc: []
		monkeypatch.setitem(__import__('sys').modules, 'face_recognition', fr)

	svc = FaceRecognitionService(config)
	assert isinstance(svc.known_face_encodings, list)
