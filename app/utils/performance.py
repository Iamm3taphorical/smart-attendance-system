import cv2
import numpy as np
import time
from typing import Optional
from collections import deque


class PerformanceMonitor:
    """Monitor and track performance metrics for face recognition system"""
    
    def __init__(self, window_size: int = 30):
        self.window_size = window_size
        self.frame_times = deque(maxlen=window_size)
        self.detection_times = deque(maxlen=window_size)
        self.recognition_times = deque(maxlen=window_size)
        
    def record_frame_time(self, duration: float):
        """Record time taken to process a frame"""
        self.frame_times.append(duration)
    
    def record_detection_time(self, duration: float):
        """Record time taken for face detection"""
        self.detection_times.append(duration)
    
    def record_recognition_time(self, duration: float):
        """Record time taken for face recognition"""
        self.recognition_times.append(duration)
    
    def get_average_fps(self) -> float:
        """Calculate average FPS from recent frames"""
        if not self.frame_times:
            return 0.0
        avg_time = sum(self.frame_times) / len(self.frame_times)
        return 1.0 / avg_time if avg_time > 0 else 0.0
    
    def get_stats(self) -> dict:
        """Get comprehensive performance statistics"""
        return {
            'avg_fps': self.get_average_fps(),
            'avg_frame_time': sum(self.frame_times) / len(self.frame_times) if self.frame_times else 0,
            'avg_detection_time': sum(self.detection_times) / len(self.detection_times) if self.detection_times else 0,
            'avg_recognition_time': sum(self.recognition_times) / len(self.recognition_times) if self.recognition_times else 0,
        }


def optimize_frame_for_detection(frame: np.ndarray, target_width: int = 640) -> np.ndarray:
    """
    Optimize frame for faster face detection.
    Converts to grayscale and optionally resizes.
    """
    # Convert to grayscale for faster processing
    if len(frame.shape) == 3:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    else:
        gray = frame
    
    # Resize if frame is too large
    height, width = gray.shape[:2]
    if width > target_width:
        scale = target_width / width
        new_height = int(height * scale)
        gray = cv2.resize(gray, (target_width, new_height))
    
    return gray


def should_process_frame(frame_count: int, skip_frames: int = 2) -> bool:
    """
    Determine if current frame should be processed.
    Implements frame skipping for performance.
    
    Args:
        frame_count: Current frame number
        skip_frames: Number of frames to skip between processing (0 = process all)
    
    Returns:
        True if frame should be processed
    """
    if skip_frames == 0:
        return True
    return frame_count % (skip_frames + 1) == 0


class AdaptiveFrameSkipper:
    """
    Adaptively skip frames based on system performance.
    Increases skip rate if processing is slow.
    """
    
    def __init__(self, target_fps: float = 10.0, max_skip: int = 5):
        self.target_fps = target_fps
        self.max_skip = max_skip
        self.current_skip = 0
        self.last_adjust_time = time.time()
        self.recent_fps = deque(maxlen=10)
    
    def update_fps(self, current_fps: float):
        """Update with current FPS measurement"""
        self.recent_fps.append(current_fps)
        
        # Adjust skip rate every 2 seconds
        if time.time() - self.last_adjust_time > 2.0:
            self._adjust_skip_rate()
            self.last_adjust_time = time.time()
    
    def _adjust_skip_rate(self):
        """Adjust frame skip rate based on performance"""
        if not self.recent_fps:
            return
        
        avg_fps = sum(self.recent_fps) / len(self.recent_fps)
        
        # If FPS is too low, increase skip rate
        if avg_fps < self.target_fps * 0.8:
            self.current_skip = min(self.current_skip + 1, self.max_skip)
        # If FPS is good, try reducing skip rate
        elif avg_fps > self.target_fps * 1.2 and self.current_skip > 0:
            self.current_skip = max(self.current_skip - 1, 0)
    
    def should_process(self, frame_count: int) -> bool:
        """Determine if frame should be processed"""
        return should_process_frame(frame_count, self.current_skip)
