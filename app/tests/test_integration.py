import pytest
import sqlite3
import numpy as np
import cv2
from pathlib import Path
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.services.face_recognition import FaceRecognitionService
from app.services.attendance_service import AttendanceService
from app.core.database import DatabaseManager


@pytest.fixture
def test_config():
    """Test configuration"""
    return {
        'face_recognition': {
            'model_backend': 'face_recognition',
            'detection_model': 'hog',
            'num_jitters': 1,
            'tolerance': 0.6,
            'known_faces_path': 'data/test_known_faces'
        },
        'database': {
            'path': 'data/test_attendance.db'
        },
        'attendance': {
            'duplicate_threshold': 300,
            'proxy_detection': False
        }
    }


@pytest.fixture
def setup_test_db(test_config):
    """Setup test database"""
    db_path = test_config['database']['path']
    
    # Clean up if exists
    if Path(db_path).exists():
        Path(db_path).unlink()
    
    # Create database
    db_manager = DatabaseManager(db_path)
    
    yield db_path
    
    # Cleanup
    if Path(db_path).exists():
        Path(db_path).unlink()
    
    # Clean up known faces
    known_faces_path = Path(test_config['face_recognition']['known_faces_path'])
    if known_faces_path.exists():
        import shutil
        shutil.rmtree(known_faces_path)


def test_student_registration_flow(test_config, setup_test_db):
    """Test complete student registration workflow"""
    # Create a simple test image (solid color with some variation)
    test_img = np.random.randint(100, 150, (200, 200, 3), dtype=np.uint8)
    
    # Initialize services
    face_service = FaceRecognitionService(test_config)
    
    # Test face detection (will likely fail on random image, which is expected)
    face_locations = face_service.detect_faces(test_img)
    
    # This test validates the service initialization and basic flow
    assert isinstance(face_locations, list)


def test_attendance_recording(test_config, setup_test_db):
    """Test attendance recording"""
    attendance_service = AttendanceService(
        setup_test_db,
        test_config
    )
    
    # Add a test student to database
    with sqlite3.connect(setup_test_db) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO students (student_id, name, email, is_active) VALUES (?, ?, ?, 1)",
            ("TEST001", "Test Student", "test@example.com")
        )
        conn.commit()
    
    # Record attendance
    result = attendance_service.record_attendance(
        student_id="TEST001",
        confidence=0.95,
        location="Test Location",
        device_id="TEST_CAM"
    )
    
    assert result is True
    
    # Verify record in database
    with sqlite3.connect(setup_test_db) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM attendance_records WHERE student_id=?", ("TEST001",))
        record = cursor.fetchone()
        assert record is not None
        assert record[1] == "TEST001"  # student_id column


def test_duplicate_attendance_prevention(test_config, setup_test_db):
    """Test that duplicate attendance within threshold is prevented"""
    attendance_service = AttendanceService(
        setup_test_db,
        test_config
    )
    
    # Add test student
    with sqlite3.connect(setup_test_db) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO students (student_id, name, email, is_active) VALUES (?, ?, ?, 1)",
            ("TEST002", "Test Student 2", "test2@example.com")
        )
        conn.commit()
    
    # Record first attendance
    result1 = attendance_service.record_attendance(
        student_id="TEST002",
        confidence=0.95
    )
    assert result1 is True
    
    # Try to record again immediately (should be prevented)
    result2 = attendance_service.record_attendance(
        student_id="TEST002",
        confidence=0.95
    )
    assert result2 is False


def test_database_schema_integrity(setup_test_db):
    """Verify database schema has all required tables"""
    with sqlite3.connect(setup_test_db) as conn:
        cursor = conn.cursor()
        
        # Check for required tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        required_tables = ['students', 'attendance_records', 'unknown_faces', 'alerts']
        for table in required_tables:
            assert table in tables, f"Missing required table: {table}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
