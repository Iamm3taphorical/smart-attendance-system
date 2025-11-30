import sqlite3
from app.services.attendance_service import AttendanceService
from app.core.database import DatabaseManager


def test_record_and_query(tmp_path):
	db_path = tmp_path / 'test.db'
	# create minimal schema
	schema = '''CREATE TABLE students (student_id TEXT PRIMARY KEY, name TEXT, email TEXT, is_active BOOLEAN);
	CREATE TABLE attendance_records (id INTEGER PRIMARY KEY AUTOINCREMENT, student_id TEXT, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP, confidence REAL, location TEXT, device_id TEXT, image_path TEXT);
	CREATE TABLE alerts (id INTEGER PRIMARY KEY AUTOINCREMENT, type TEXT, message TEXT, severity TEXT);
	'''
	with open(tmp_path / 'schema.sql', 'w', encoding='utf-8') as f:
		f.write(schema)

	db_mgr = DatabaseManager(str(db_path), schema_path=str(tmp_path / 'schema.sql'))
	svc = AttendanceService(str(db_path), {'attendance': {'duplicate_threshold': 1, 'proxy_detection': False}})

	# insert a student and record attendance
	with sqlite3.connect(db_path) as conn:
		conn.execute("INSERT INTO students (student_id, name, email, is_active) VALUES ('S1','T','t@example.com',1)")

	ok = svc.record_attendance('S1', 0.9, location='test')
	assert ok is True
