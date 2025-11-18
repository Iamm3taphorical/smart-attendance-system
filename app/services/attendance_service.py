# app/services/attendance_service.py
import sqlite3
import time
import logging
from typing import Optional, Dict, List
from datetime import datetime, timedelta
import hashlib

logger = logging.getLogger(__name__)

class AttendanceService:
    def __init__(self, db_path: str, config: dict):
        self.db_path = db_path
        self.config = config
        self._init_database()
    
    def _init_database(self):
        """Initialize database tables"""
        with sqlite3.connect(self.db_path) as conn:
            # Tables are created by schema.sql, but we ensure they exist
            pass
    
    def record_attendance(self, student_id: str, confidence: float, 
                         location: str = None, device_id: str = None,
                         image_path: str = None) -> bool:
        """Record attendance for a student"""
        
        # Check for duplicate check-ins
        if self._is_duplicate_checkin(student_id):
            logger.warning(f"Duplicate check-in attempt for {student_id}")
            return False
        
        # Check for proxy detection
        if self.config['attendance']['proxy_detection']:
            if self._detect_proxy_attempt(student_id, location, device_id):
                self._create_alert(
                    "proxy_attempt",
                    f"Possible proxy attempt detected for {student_id}",
                    "warning"
                )
                return False
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO attendance_records 
                    (student_id, confidence, location, device_id, image_path)
                    VALUES (?, ?, ?, ?, ?)
                ''', (student_id, confidence, location, device_id, image_path))
                
                logger.info(f"Attendance recorded for {student_id} with confidence {confidence:.2f}")
                return True
                
        except sqlite3.Error as e:
            logger.error(f"Database error recording attendance: {e}")
            return False
    
    def _is_duplicate_checkin(self, student_id: str) -> bool:
        """Check if student has already checked in recently"""
        threshold_seconds = self.config['attendance']['duplicate_threshold']
        time_threshold = datetime.now() - timedelta(seconds=threshold_seconds)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT COUNT(*) FROM attendance_records 
                WHERE student_id = ? AND timestamp > ?
            ''', (student_id, time_threshold))
            
            count = cursor.fetchone()[0]
            return count > 0
    
    def _detect_proxy_attempt(self, student_id: str, location: str, device_id: str) -> bool:
        """Detect potential proxy attendance attempts"""
        # Implement proxy detection logic
        # Check for unusual locations, multiple devices, etc.
        return False
    
    def _create_alert(self, alert_type: str, message: str, severity: str = "info"):
        """Create a new alert"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO alerts (type, message, severity) 
                VALUES (?, ?, ?)
            ''', (alert_type, message, severity))
    
    def get_attendance_report(self, start_date: str, end_date: str) -> List[Dict]:
        """Generate attendance report for a date range"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT s.student_id, s.name, s.email,
                       COUNT(ar.id) as total_classes,
                       SUM(CASE WHEN ar.status = 'present' THEN 1 ELSE 0 END) as present_count,
                       SUM(CASE WHEN ar.status = 'late' THEN 1 ELSE 0 END) as late_count,
                       SUM(CASE WHEN ar.status = 'absent' THEN 1 ELSE 0 END) as absent_count
                FROM students s
                LEFT JOIN attendance_records ar ON s.student_id = ar.student_id 
                    AND date(ar.timestamp) BETWEEN ? AND ?
                WHERE s.is_active = TRUE
                GROUP BY s.student_id, s.name, s.email
                ORDER BY s.student_id
            ''', (start_date, end_date))
            
            return [dict(row) for row in cursor.fetchall()]