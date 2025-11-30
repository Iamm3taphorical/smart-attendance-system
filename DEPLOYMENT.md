# Deployment Guide

This guide covers how to deploy the Smart Attendance System using Docker or directly on a host machine.

## Prerequisites

- **Python 3.9+** (for local deployment)
- **Docker & Docker Compose** (for containerized deployment)
- **Webcam** (connected to the host machine)

## Option 1: Docker Deployment (Recommended)

1. **Build and Run**
   ```bash
   docker-compose up -d --build
   ```

2. **Access the Dashboard**
   Open [http://localhost:5000](http://localhost:5000) in your browser.

3. **View Logs**
   ```bash
   docker-compose logs -f
   ```

4. **Stop the System**
   ```bash
   docker-compose down
   ```

> **Note**: For the camera to work inside Docker, you may need to pass the device flag. Update `docker-compose.yml` if needed:
> ```yaml
> devices:
>   - "/dev/video0:/dev/video0"
> ```
> On Windows, accessing USB devices from Docker containers can be tricky. It is often easier to run the application natively on Windows.

## Option 2: Native Deployment (Windows/Linux)

1. **Clone the Repository**
   ```bash
   git clone https://github.com/Iamm3taphorical/smart-attendance-system.git
   cd smart-attendance-system
   ```

2. **Set up Virtual Environment**
   ```bash
   python -m venv venv
   # Windows
   .\venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize Database**
   ```bash
   python scripts/setup.py
   ```

5. **Run the Application**
   ```bash
   python -m app.main
   ```

6. **Access Dashboard**
   Open [http://localhost:5000](http://localhost:5000).

## Configuration

Edit `config.yaml` to customize:
- **Camera**: Resolution, FPS, and Source ID.
- **Database**: Path and backup settings.
- **Face Recognition**: Model backend (face_recognition, dlib, insightface) and tolerance.

## Troubleshooting

- **Camera not opening**: Check if another application is using the camera. Verify `source` index in `config.yaml`.
- **Missing dependencies**: Ensure you have installed C++ build tools if you encounter errors installing `dlib` or `face_recognition`.
