from flask import Blueprint, jsonify, request, current_app
import sqlite3
from datetime import datetime

api_bp = Blueprint('api', __name__)


def get_db_connection():
    db_path = current_app.config.get('DATABASE_PATH', 'data/attendance.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


@api_bp.route('/health')
def health():
    return jsonify({'status': 'ok', 'time': datetime.utcnow().isoformat()})


@api_bp.route('/attendance', methods=['GET'])
def attendance_list():
    date_str = request.args.get('date', datetime.utcnow().strftime('%Y-%m-%d'))
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute('''SELECT ar.*, s.name FROM attendance_records ar LEFT JOIN students s ON ar.student_id = s.student_id WHERE date(ar.timestamp)=?''', (date_str,))
        rows = [dict(r) for r in cur.fetchall()]
    return jsonify(rows)


@api_bp.route('/alerts', methods=['GET'])
def alerts():
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute('SELECT * FROM alerts ORDER BY timestamp DESC LIMIT 100')
        rows = [dict(r) for r in cur.fetchall()]
    return jsonify(rows)

