import sqlite3
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class AttendanceService:
    """Minimal attendance service for recording and reporting attendance."""

    def __init__(self, db_path: str, config: Optional[dict] = None):
        self.db_path = db_path
        self.config = config or {}

    def record_attendance(self, student_id: str, confidence: float,
                          location: Optional[str] = None,
                          device_id: Optional[str] = None,
                          image_path: Optional[str] = None) -> bool:
        """Record an attendance row. Returns True on success."""
        try:
            if self._is_duplicate_checkin(student_id):
                logger.warning("Duplicate check-in for %s", student_id)
                return False

            if self.config.get("attendance", {}).get("proxy_detection"):
                if self._detect_proxy_attempt(student_id, location, device_id):
                    self._create_alert("proxy_attempt",
                                       f"Possible proxy attempt for {student_id}",
                                       "warning")
                    return False

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                sql = (
                    "INSERT INTO attendance_records "
                    "(student_id, confidence, location, device_id, image_path) "
                    "VALUES (?, ?, ?, ?, ?)"
                )
                cursor.execute(sql, (student_id, confidence, location, device_id, image_path))
                conn.commit()

            logger.info("Recorded attendance for %s", student_id)
            return True

        except sqlite3.Error:
            logger.exception("Failed to record attendance")
            return False

    def _is_duplicate_checkin(self, student_id: str) -> bool:
        """Return True if the student checked in within the duplicate threshold."""
        threshold = self.config.get("attendance", {}).get("duplicate_threshold", 300)
        cutoff = datetime.now() - timedelta(seconds=threshold)
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT COUNT(*) FROM attendance_records WHERE student_id = ? AND timestamp > ?",
                    (student_id, cutoff),
                )
                row = cursor.fetchone()
                return (row[0] if row else 0) > 0
        except sqlite3.Error:
            return False

    def _detect_proxy_attempt(self, student_id: str, location: Optional[str], device_id: Optional[str]) -> bool:
        """Placeholder proxy detection - returns False (no proxy) by default."""
        return False

    def _create_alert(self, alert_type: str, message: str, severity: str = "info") -> None:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO alerts (type, message, severity) VALUES (?, ?, ?)",
                    (alert_type, message, severity),
                )
                conn.commit()
        except sqlite3.Error:
            logger.exception("Failed to create alert")

    def get_attendance_report(self, start_date: str, end_date: str) -> List[Dict]:
        """Return a simple attendance report between two ISO dates."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT s.student_id, s.name, s.email,
                       COUNT(ar.id) as total_classes,
                       SUM(CASE WHEN ar.status = 'present' THEN 1 ELSE 0 END) as present_count,
                       SUM(CASE WHEN ar.status = 'late' THEN 1 ELSE 0 END) as late_count,
                       SUM(CASE WHEN ar.status = 'absent' THEN 1 ELSE 0 END) as absent_count
                FROM students s
                LEFT JOIN attendance_records ar ON s.student_id = ar.student_id
                    AND date(ar.timestamp) BETWEEN ? AND ?
                WHERE s.is_active = 1
                GROUP BY s.student_id, s.name, s.email
                ORDER BY s.student_id
                """,
                (start_date, end_date),
            )
            return [dict(r) for r in cursor.fetchall()]
