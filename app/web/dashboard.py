from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
import sqlite3
import os
import cv2
import numpy as np
from datetime import datetime
from app.api import api_bp
from app.services.face_recognition import FaceRecognitionService

def create_app(config=None):
    app = Flask(__name__, template_folder='templates')
    app.secret_key = 'dev-secret-key' # Change in production
    
    if config:
        app.config.update(config)
    
    # Register Blueprints
    app.register_blueprint(api_bp, url_prefix='/api')

    def get_db():
        # Handle both full config and simple dict with DATABASE_PATH
        db_path = app.config.get('DATABASE_PATH')
        if not db_path and 'database' in app.config:
            db_path = app.config['database']['path']
        if not db_path:
            db_path = 'data/attendance.db'
        
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn

    @app.route('/')
    def dashboard():
        today = datetime.now().strftime('%Y-%m-%d')
        stats = {
            'present': 0,
            'late': 0,
            'unknown': 0,
            'total_students': 0
        }
        
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Get stats
            cursor.execute("SELECT COUNT(*) FROM students WHERE is_active=1")
            stats['total_students'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT status, COUNT(*) FROM attendance_records WHERE date(timestamp)=? GROUP BY status", (today,))
            for row in cursor.fetchall():
                if row['status'] == 'present': stats['present'] = row[1]
                elif row['status'] == 'late': stats['late'] = row[1]
            
            cursor.execute("SELECT COUNT(*) FROM alerts WHERE type='unknown_face' AND date(timestamp)=?", (today,))
            stats['unknown'] = cursor.fetchone()[0]

            # Get recent attendance
            cursor.execute('''
                SELECT ar.*, s.name, s.email 
                FROM attendance_records ar
                LEFT JOIN students s ON ar.student_id = s.student_id
                WHERE date(ar.timestamp) = ?
                ORDER BY ar.timestamp DESC LIMIT 10
            ''', (today,))
            recent_attendance = [dict(row) for row in cursor.fetchall()]

        return render_template('dashboard.html', stats=stats, recent_attendance=recent_attendance)

    @app.route('/register', methods=['GET', 'POST'])
    def register_student():
        if request.method == 'POST':
            name = request.form['name']
            student_id = request.form['student_id']
            email = request.form['email']
            photo = request.files['photo']

            if not photo:
                flash('Photo is required', 'danger')
                return redirect(request.url)

            try:
                # Read image
                file_bytes = np.frombuffer(photo.read(), np.uint8)
                img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
                
                if img is None:
                    flash('Invalid image file', 'danger')
                    return redirect(request.url)

                # Initialize service to get encoding
                # Use the app's configuration
                from flask import current_app
                from app.utils.face_quality import validate_face_quality, detect_multiple_faces_warning
                
                face_service = FaceRecognitionService(current_app.config)
                
                # Detect and encode
                face_locations = face_service.detect_faces(img)
                
                # Check for multiple faces or no faces
                multi_face_warning = detect_multiple_faces_warning(face_locations)
                if multi_face_warning:
                    flash(multi_face_warning, 'warning')
                    return redirect(request.url)
                
                # Validate face quality
                is_valid, quality_msg = validate_face_quality(img, face_locations[0])
                if not is_valid:
                    flash(quality_msg, 'warning')
                    return redirect(request.url)

                encoding = face_service.encode_face(img, face_locations[0])
                
                if encoding is None:
                    flash('Could not encode face. Please try another photo.', 'danger')
                    return redirect(request.url)

                # Save to DB
                with get_db() as conn:
                    cursor = conn.cursor()
                    try:
                        cursor.execute(
                            "INSERT INTO students (student_id, name, email, is_active) VALUES (?, ?, ?, 1)",
                            (student_id, name, email)
                        )
                        conn.commit()
                    except sqlite3.IntegrityError:
                        flash(f'Student ID {student_id} or Email {email} already exists.', 'danger')
                        return redirect(request.url)

                # Add to known faces (this saves to pickle/disk as per current implementation)
                face_service.add_known_face(encoding, {'student_id': student_id})
                
                flash(f'Student {name} registered successfully!', 'success')
                return redirect(url_for('dashboard'))

            except Exception as e:
                flash(f'Error registering student: {str(e)}', 'danger')
                return redirect(request.url)

        return render_template('register.html')

    @app.route('/analytics')
    def analytics():
        from datetime import datetime, timedelta
        
        # Get date range from query params or default to last 7 days
        end_date = request.args.get('end_date', datetime.now().strftime('%Y-%m-%d'))
        start_date = request.args.get('start_date', (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'))
        
        analytics_data = {
            'total_records': 0,
            'unique_students': 0,
            'avg_daily': 0,
            'peak_day': 'N/A',
            'chart_labels': [],
            'chart_data': [],
            'top_students': []
        }
        
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Total records in date range
            cursor.execute(
                "SELECT COUNT(*) FROM attendance_records WHERE date(timestamp) BETWEEN ? AND ?",
                (start_date, end_date)
            )
            analytics_data['total_records'] = cursor.fetchone()[0]
            
            # Unique students
            cursor.execute(
                "SELECT COUNT(DISTINCT student_id) FROM attendance_records WHERE date(timestamp) BETWEEN ? AND ?",
                (start_date, end_date)
            )
            analytics_data['unique_students'] = cursor.fetchone()[0]
            
            # Daily attendance for chart
            cursor.execute("""
                SELECT date(timestamp) as day, COUNT(*) as count
                FROM attendance_records
                WHERE date(timestamp) BETWEEN ? AND ?
                GROUP BY day
                ORDER BY day
            """, (start_date, end_date))
            
            daily_data = cursor.fetchall()
            if daily_data:
                analytics_data['chart_labels'] = [row[0] for row in daily_data]
                analytics_data['chart_data'] = [row[1] for row in daily_data]
                analytics_data['avg_daily'] = sum(analytics_data['chart_data']) / len(analytics_data['chart_data'])
                
                # Peak day
                max_idx = analytics_data['chart_data'].index(max(analytics_data['chart_data']))
                analytics_data['peak_day'] = analytics_data['chart_labels'][max_idx]
            
            # Top students
            cursor.execute("""
                SELECT s.name, ar.student_id, COUNT(*) as count
                FROM attendance_records ar
                LEFT JOIN students s ON ar.student_id = s.student_id
                WHERE date(ar.timestamp) BETWEEN ? AND ?
                GROUP BY ar.student_id
                ORDER BY count DESC
                LIMIT 10
            """, (start_date, end_date))
            
            analytics_data['top_students'] = [
                {'name': row[0] or 'Unknown', 'student_id': row[1], 'count': row[2]}
                for row in cursor.fetchall()
            ]
        
        return render_template('analytics.html', analytics=analytics_data, start_date=start_date, end_date=end_date)

    @app.route('/attendance')
    def attendance_records():
        from datetime import datetime
        
        # Get filters
        selected_date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
        selected_student = request.args.get('student_id', '')
        
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Build query with filters
            query = '''
                SELECT ar.*, s.name, s.email 
                FROM attendance_records ar
                LEFT JOIN students s ON ar.student_id = s.student_id
                WHERE 1=1
            '''
            params = []
            
            if selected_date:
                query += ' AND date(ar.timestamp) = ?'
                params.append(selected_date)
            
            if selected_student:
                query += ' AND ar.student_id LIKE ?'
                params.append(f'%{selected_student}%')
            
            query += ' ORDER BY ar.timestamp DESC LIMIT 100'
            
            cursor.execute(query, params)
            records = [dict(row) for row in cursor.fetchall()]
            
            # Get stats
            cursor.execute('SELECT COUNT(*) FROM attendance_records')
            total_records = cursor.fetchone()[0]
            
            cursor.execute(
                'SELECT COUNT(*) FROM attendance_records WHERE date(timestamp) = ?',
                (datetime.now().strftime('%Y-%m-%d'),)
            )
            today_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT AVG(confidence) FROM attendance_records')
            avg_confidence = cursor.fetchone()[0] or 0
        
        return render_template(
            'attendance.html',
            records=records,
            total_records=total_records,
            today_count=today_count,
            avg_confidence=avg_confidence,
            selected_date=selected_date,
            selected_student=selected_student
        )

    @app.route('/settings')
    def settings():
        with get_db() as conn:
            cursor = conn.cursor()
            
            stats = {}
            cursor.execute('SELECT COUNT(*) FROM students')
            stats['total_students'] = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM attendance_records')
            stats['total_records'] = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM unknown_faces')
            stats['unknown_faces'] = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM alerts')
            stats['total_alerts'] = cursor.fetchone()[0]
        
        return render_template('settings.html', config=app.config, stats=stats)

    @app.route('/export/csv')
    def export_csv():
        from datetime import datetime
        import csv
        from io import StringIO
        from flask import Response
        
        selected_date = request.args.get('date', '')
        selected_student = request.args.get('student_id', '')
        export_all = request.args.get('all', '')
        
        with get_db() as conn:
            cursor = conn.cursor()
            
            if export_all:
                cursor.execute('''
                    SELECT ar.*, s.name, s.email 
                    FROM attendance_records ar
                    LEFT JOIN students s ON ar.student_id = s.student_id
                    ORDER BY ar.timestamp DESC
                ''')
            else:
                query = '''
                    SELECT ar.*, s.name, s.email 
                    FROM attendance_records ar
                    LEFT JOIN students s ON ar.student_id = s.student_id
                    WHERE 1=1
                '''
                params = []
                
                if selected_date:
                    query += ' AND date(ar.timestamp) = ?'
                    params.append(selected_date)
                
                if selected_student:
                    query += ' AND ar.student_id LIKE ?'
                    params.append(f'%{selected_student}%')
                
                query += ' ORDER BY ar.timestamp DESC'
                cursor.execute(query, params)
            
            records = cursor.fetchall()
        
        # Create CSV
        output = StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow(['ID', 'Timestamp', 'Student ID', 'Name', 'Email', 'Confidence', 'Location', 'Device ID'])
        
        # Data
        for record in records:
            writer.writerow([
                record[0],  # id
                record[1],  # timestamp
                record[2],  # student_id
                record[7] or 'Unknown',  # name
                record[8] or 'N/A',  # email
                f"{record[3]:.2f}",  # confidence
                record[4] or 'N/A',  # location
                record[5] or 'N/A'   # device_id
            ])
        
        # Create response
        output.seek(0)
        filename = f"attendance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename={filename}'}
        )

    return app

if __name__ == '__main__':
    app = create_app({'DATABASE_PATH': 'data/attendance.db'})
    app.run(host='0.0.0.0', port=5000, debug=True)

