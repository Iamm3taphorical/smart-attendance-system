from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import datetime
from app.api import api_bp

def create_app(config=None):
    app = Flask(__name__, template_folder='templates')
    
    if config:
        app.config.update(config)
    
    # Register Blueprints
    app.register_blueprint(api_bp, url_prefix='/api')

    @app.route('/')
    def dashboard():
        return '<h1>Smart Attendance Dashboard</h1>'

    return app

if __name__ == '__main__':
    app = create_app({'DATABASE_PATH': 'data/attendance.db'})
    app.run(host='0.0.0.0', port=5000, debug=True)

