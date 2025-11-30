import cv2
from typing import Optional, Tuple


def open_camera(source: int = 0, width: int = 640, height: int = 480, fps: int = 30):
	cap = cv2.VideoCapture(source)
	cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
	cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
	cap.set(cv2.CAP_PROP_FPS, fps)
	return cap


def read_frame(cap) -> Optional[Tuple[bool, 'ndarray']]:
	if cap is None:
		return None
	ret, frame = cap.read()
	return ret, frame

