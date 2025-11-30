"""
Quick diagnostic script to test Smart Attendance System functionality
"""
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

print("=" * 60)
print("SMART ATTENDANCE SYSTEM - DIAGNOSTIC TEST")
print("=" * 60)

# Test 1: Import modules
print("\n[TEST 1] Importing modules...")
try:
    from app.services.face_recognition import FaceRecognitionService
    from app.services.attendance_service import AttendanceService
    from app.core.database import DatabaseManager
    print("✓ All modules imported successfully")
except Exception as e:
    print(f"✗ Import failed: {e}")
    sys.exit(1)

# Test 2: Load configuration
print("\n[TEST 2] Loading configuration...")
try:
    import yaml
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    print(f"✓ Config loaded: {config['system']['name']}")
    print(f"  - Database: {config['database']['path']}")
    print(f"  - Known faces: {config['face_recognition']['known_faces_path']}")
except Exception as e:
    print(f"✗ Config load failed: {e}")
    sys.exit(1)

# Test 3: Database connection
print("\n[TEST 3] Testing database...")
try:
    import sqlite3
    conn = sqlite3.connect(config['database']['path'])
    cursor = conn.cursor()
    
    # Check tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    print(f"✓ Database connected. Tables: {', '.join(tables)}")
    
    # Check student count
    cursor.execute("SELECT COUNT(*) FROM students")
    student_count = cursor.fetchone()[0]
    print(f"  - Registered students: {student_count}")
    
    # Check attendance count
    cursor.execute("SELECT COUNT(*) FROM attendance_records")
    attendance_count = cursor.fetchone()[0]
    print(f"  - Attendance records: {attendance_count}")
    
    conn.close()
except Exception as e:
    print(f"✗ Database test failed: {e}")
    sys.exit(1)

# Test 4: Face Recognition Service
print("\n[TEST 4] Testing Face Recognition Service...")
try:
    face_service = FaceRecognitionService(config)
    print(f"✓ Face service initialized")
    print(f"  - Backend: {face_service.model_backend}")
    print(f"  - Known faces loaded: {len(face_service.known_face_encodings)}")
except Exception as e:
    print(f"✗ Face service failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Check known faces directory
print("\n[TEST 5] Checking known faces storage...")
try:
    from pathlib import Path
    known_faces_path = Path(config['face_recognition']['known_faces_path'])
    encodings_file = known_faces_path / "encodings.pkl"
    
    if encodings_file.exists():
        print(f"✓ Encodings file exists: {encodings_file}")
        print(f"  - File size: {encodings_file.stat().st_size} bytes")
    else:
        print(f"⚠ Encodings file not found (no students registered yet)")
except Exception as e:
    print(f"✗ Storage check failed: {e}")

# Test 6: Web server configuration
print("\n[TEST 6] Checking web server...")
try:
    from app.web.dashboard import create_app
    app = create_app({'DATABASE_PATH': config['database']['path']})
    print(f"✓ Flask app created successfully")
    print(f"  - Routes: {len(app.url_map._rules)} registered")
except Exception as e:
    print(f"✗ Web server test failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("DIAGNOSTIC COMPLETE")
print("=" * 60)
print("\nSUMMARY:")
print("- System is operational")
print("- To register students: Go to http://localhost:5000/register")
print("- Upload a clear photo with good lighting")
print("- Camera will then recognize registered faces")
print("=" * 60)
