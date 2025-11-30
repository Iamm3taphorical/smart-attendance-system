# Smart Attendance and Identity System

A production-ready face recognition-based attendance system for campuses with modern features and privacy preservation.

## Features

- Multi-model Support: `face_recognition`, `dlib`, and `InsightFace` backends
- Real-time Processing: Live camera feed processing
- Anti-spoofing: Duplicate and proxy detection primitives
- Privacy-focused: Local storage with optional encrypted backups
- Web Dashboard: Real-time monitoring and manual corrections
- REST API: Mobile app integration ready
- Comprehensive Reporting: CSV and PDF exports

## Quick Start

1. Clone and Setup

```powershell
git clone <repository>
cd smart-attendance-system
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

2. Configuration

```powershell
copy config.example.yaml config.yaml
# Edit `config.yaml` for your environment
```

3. Database Setup

```powershell
python scripts\setup.py --config config.yaml
```

4. Run System

```powershell
python -m app.main
```

5. Access Dashboard

Open http://localhost:5000

## Docker Deployment

```powershell
docker-compose up -d --build
```

## Notes

- `face_recognition` has native dependencies (dlib). For a production image use the provided `Dockerfile` which installs minimal system libs.
- To add student faces, store face encodings via the services or add helper scripts that import images and call `FaceRecognitionService.add_known_face`.

## Development & Tests

- Initialize DB: `python scripts\setup.py`
- Run tests: `pytest`

## Contributing

Please open issues or pull requests for features, bugs, or improvements.
# Smart Attendance and Identity System

A production-ready face recognition-based attendance system for campuses with modern features and privacy preservation.

## Features

- **Multi-model Support**: face_recognition, dlib, and InsightFace backends
- **Real-time Processing**: Live camera feed processing
- **Anti-spoofing**: Duplicate and proxy detection
- **Privacy-focused**: Local storage with encrypted backups
- **Web Dashboard**: Real-time monitoring and manual corrections
- **REST API**: Mobile app integration ready
- **Comprehensive Reporting**: CSV and PDF exports

## Quick Start

1. **Clone and Setup**
   ```bash
   git clone <repository>
   cd smart-attendance-system
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt