import cv2
import numpy as np
from typing import Tuple, Optional


def calculate_blur_score(image: np.ndarray) -> float:
    """
    Calculate blur score using Laplacian variance.
    Higher values indicate sharper images.
    Typical threshold: > 100 for acceptable quality.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    return laplacian_var


def assess_lighting_quality(image: np.ndarray) -> Tuple[bool, str]:
    """
    Assess if image has adequate lighting.
    Returns (is_acceptable, reason).
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
    mean_brightness = np.mean(gray)
    std_brightness = np.std(gray)
    
    # Too dark
    if mean_brightness < 50:
        return False, "Image is too dark"
    
    # Too bright (overexposed)
    if mean_brightness > 200:
        return False, "Image is overexposed"
    
    # Low contrast (flat lighting)
    if std_brightness < 30:
        return False, "Image has low contrast"
    
    return True, "Lighting is acceptable"


def validate_face_quality(image: np.ndarray, face_location: Tuple) -> Tuple[bool, str]:
    """
    Comprehensive face quality validation.
    Returns (is_valid, message).
    """
    top, right, bottom, left = face_location
    face_img = image[top:bottom, left:right]
    
    # Check if face region is too small
    face_height = bottom - top
    face_width = right - left
    
    if face_height < 80 or face_width < 80:
        return False, "Face is too small. Please move closer to the camera."
    
    # Check blur
    blur_score = calculate_blur_score(face_img)
    if blur_score < 100:
        return False, f"Image is too blurry (score: {blur_score:.1f}). Please ensure good focus."
    
    # Check lighting
    lighting_ok, lighting_msg = assess_lighting_quality(face_img)
    if not lighting_ok:
        return False, lighting_msg
    
    return True, "Face quality is acceptable"


def detect_multiple_faces_warning(face_locations: list) -> Optional[str]:
    """
    Check if multiple faces are detected and return warning message.
    """
    if len(face_locations) == 0:
        return "No face detected in the image"
    elif len(face_locations) > 1:
        return f"Multiple faces detected ({len(face_locations)}). Please ensure only one person is in the frame."
    return None
