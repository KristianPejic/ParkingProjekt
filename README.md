# Parking Detection System 🚗

A comprehensive computer vision system for automatically counting free parking spaces using YOLOv8 object detection, FastAPI backend, Vue.js frontend, and Firebase database.

## 🎯 Project Overview

This system uses computer vision to analyze parking lot images and automatically detect vehicles, count occupied spaces, and calculate free parking slots. It's designed as a complete solution with REST API, web interface, and cloud database integration.

## 🏗️ System Architecture

### Components
- **Backend**: FastAPI with YOLOv8 computer vision model
- **Frontend**: Vue.js 3 with modern UI/UX
- **Database**: Firebase Firestore + Storage
- **AI Model**: Ultralytics YOLOv8 for vehicle detection
- **Deployment**: Docker-ready configuration

### Data Flow
1. User uploads parking lot image via web interface
2. Frontend calls REST API `/detect` endpoint
3. Backend processes image with YOLOv8 model
4. System counts vehicles and calculates free spaces
5. Results are stored in Firebase and returned to client
6. Annotated image with bounding boxes is displayed

## 🛠️ Technologies

- **Python 3.13.5** - Backend runtime
- **FastAPI** - REST API framework
- **Ultralytics YOLOv8** - Computer vision model
- **Vue.js 3** - Frontend framework
- **Firebase** - Database and storage
- **OpenCV** - Image processing
- **Docker** - Containerization

## 📋 Features

### Core Functionality
- ✅ Vehicle detection using YOLOv8
- ✅ Automatic parking space counting
- ✅ Real-time image analysis
- ✅ Confidence scoring
- ✅ Bounding box visualization

### Web Interface
- 🎨 Modern, responsive design
- 📱 Mobile-friendly interface
- 🔄 Drag & drop image upload
- 📊 Real-time statistics
- 📝 Detection history
- 🖼️ Image gallery with modal view

### API Endpoints
- `POST /detect` - Analyze parking lot image
- `GET /last-result` - Get most recent detection
- `GET /history` - Retrieve detection history
- `GET /stats` - System usage statistics

## 🚀 Quick Start

### Prerequisites
- Python 3.13.5+
- Node.js 18+
- Firebase account with project setup
# Parking Detection System (FastAPI + YOLOv8)

A production-ready REST API for analyzing parking lot images. It detects cars with YOLOv8, infers parking spots from visible white lines and car layout, matches occupancy (occupied vs. free), and returns a JSON payload including an annotated image (as Base64). Results can be stored in Google Firestore when configured.

- Backend: FastAPI
- Computer Vision: Ultralytics YOLOv8 + OpenCV (lines/geometry)
- Storage (optional): Google Firestore via Firebase Admin SDK

## Key Features

- Car-only detection optimized for parking scenes
- Parking spot inference:
  - Precise white-line detection using Hough transforms
  - Row-based estimation from car distribution (fallback/augmentation)
  - Merging and deduplication logic to keep only plausible spots
- Occupancy analysis: match cars to inferred spots to compute totals
- Annotated image overlay (bounding boxes, spot IDs, FREE/OCCUPIED shading, summary banner) as Base64
- Firestore persistence for detection metadata (optional)
- CORS enabled for easy frontend integration
- Multiple debug/test endpoints to validate the pipeline

## Requirements

- Python 3.10+ (tested with 3.13.5)
- pip/virtualenv
- Internet access on first run to download YOLOv8 weights

Python packages you will need:
- fastapi
- uvicorn[standard]
- ultralytics (YOLOv8)
- opencv-python
- numpy
- firebase-admin (optional; for Firestore)
- python-multipart (for file uploads)

Tip: You can install these via one of:
- pip install fastapi "uvicorn[standard]" ultralytics opencv-python numpy firebase-admin python-multipart
- or create a requirements.txt and run pip install -r requirements.txt

Note on PyTorch:
- Ultralytics uses PyTorch. If PyTorch is not automatically resolved for your platform, install CPU-only build with:
  - pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
- For GPU, follow the official PyTorch installation instructions for your CUDA version.

## Quick Start

1) Create and activate a virtual environment:
- python -m venv .venv
- On macOS/Linux: source .venv/bin/activate
- On Windows (PowerShell): .\.venv\Scripts\Activate.ps1

2) Install dependencies:
- pip install fastapi "uvicorn[standard]" ultralytics opencv-python numpy firebase-admin python-multipart

3) (Optional) Configure Firestore:
- Place a Firebase service account key in the project root named: firebase-service-account.json
- Ensure the service account has Firestore access (e.g., roles: Datastore User or appropriate custom role)
- If this file is absent or invalid, Firestore integration is disabled gracefully and the API still works

4) Run the API server (development):
- uvicorn main:app --reload --host 0.0.0.0 --port 8000

5) Open interactive docs:
- http://localhost:8000/docs

The first request will download YOLOv8 weights (yolov8m.pt by default, yolov8n.pt as fallback), which may take a moment.

## Endpoints

- GET / — Basic API info/status
- GET /health — Health check (model/database status)
- POST /detect — Main detection endpoint (multipart/form-data image upload)
- POST /debug-detect — Verbose raw detection dump for debugging
- POST /simple-test — Minimal YOLO run returning raw class counts
- POST /test-class67 — Report of cars vs. “class 67” items (used as misclassified cars)
- GET /last-result — Latest Firestore metadata (if Firestore enabled)
- GET /history?limit=10 — Recent Firestore metadata entries
- GET /stats — Aggregate statistics from recent runs

### POST /detect

Request:
- Content-Type: multipart/form-data
- Form field: file (image/jpeg, image/png, etc.)
- Optional query param: total_slots (int) used as a fallback when no valid parking spots can be inferred

Example (curl):
- curl -X POST "http://localhost:8000/detect?total_slots=20" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/your/parking_lot.jpg"

Response (example shape):
{
  "timestamp": "2024-01-01T12:34:56.789Z",
  "total_slots": 18,
  "occupied_slots": 12,
  "free_slots": 6,
  "confidence": 0.74,
  "image_base64": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQA...",  // annotated image
  "detections": [
    {
      "class_id": 2,
      "class_name": "car",
      "confidence": 0.85,
      "bbox": [x1, y1, x2, y2],
      "area": 12345.6,
      "area_ratio": 0.07
    }
    // ...
  ],
  "parking_spots": {
    "detected_spots": 18,
    "occupied_spots": 12,
    "free_spots": 6,
    "spot_detection_method": "computer_vision"  // or "manual_count"
  }
}

Notes:
- image_base64 contains a JPEG with overlays: cars (green), white lines (cyan), FREE (green shading), OCCUPIED (red shading), and a summary banner.
- If white-line inference fails, the service falls back to row-based estimation or, if necessary, to simple counting vs. total_slots.

### Other useful endpoints

- POST /debug-detect
  - Returns raw YOLO detections for introspection (class IDs, confidences, boxes)
- POST /simple-test
  - Quick sanity check to see what YOLO detects in your image
- POST /test-class67
  - Shows how many “cars” come from class 2 vs. class 67 (helpful for parking lot corner-cases)
- GET /health
  - See model loaded status, Firestore connectivity, and timestamp

## How It Works (High Level)

1) Car detection:
- YOLOv8 (medium model by default; nano as fallback) runs on the input image
- Only car-like classes are considered for occupancy

2) Parking spot inference:
- White-line detection (OpenCV) identifies vertical/horizontal parking dividers using edge detection + Hough transforms
- Spots are created conservatively between validated line pairs
- Row-based estimation from car layout augments line-derived spots when lines are partially visible
- Overlapping/implausible spots are filtered out via size, aspect ratio, and overlap thresholds

3) Occupancy matching:
- Cars are matched to spots via overlap and center proximity
- Occupied and free spot counts are computed
- An annotated image is generated

4) Persistence (optional):
- If Firestore is configured, a lightweight metadata record (no image payload) is saved for analytics/history

## Configuration

- Firebase/Firestore:
  - Place firebase-service-account.json in the project root
  - If missing or invalid, Firestore is disabled automatically and the API continues to operate
- CORS:
  - Enabled for all origins by default to simplify frontend integration
- Models:
  - Default: yolov8m.pt (better accuracy)
  - Fallback: yolov8n.pt (faster, smaller)
  - Weights are downloaded automatically on first run

## Frontend Integration

- The API is CORS-enabled. You can POST a FormData image from any modern frontend framework (e.g., Vue/React).
- The /detect response includes an annotated image as a data URL (image_base64). You can display it directly in an <img> tag.
- For history/analytics dashboards, use /history and /stats (if Firestore is enabled).

## Performance Tips

- Prefer reasonably sized inputs (e.g., ~1280px width). Extremely large images increase inference time without improving accuracy beyond a point.
- GPU acceleration: If a compatible GPU and PyTorch build are available, YOLO will leverage it automatically.
- Batch large workloads by queuing requests rather than sending many concurrent uploads.
- Consider pre-cropping to the parking area if your source images include irrelevant regions.

## Troubleshooting

- “YOLO model not loaded” or model errors:
  - Ensure ultralytics and (optionally) torch are installed
  - Ensure the host has internet on first run for weight download
- Firestore errors:
  - Verify firebase-service-account.json path and permissions
  - Ensure Firestore is in “Native mode” and the service account has access
- OpenCV decoding issues:
  - Ensure the uploaded file is a valid image (Content-Type must start with image/)
- Poor spot detection:
  - White lines must be reasonably visible; adjust lighting or camera angle
  - Try different images or ensure the lot markings are not obstructed
- Slow inference:
  - Try smaller images
  - Consider using the nano model (fallback) for faster inference at some cost to accuracy

## Running in Production

- Example (gunicorn + uvicorn workers):
  - gunicorn -k uvicorn.workers.UvicornWorker -w 2 -b 0.0.0.0:8000 main:app
- Ensure the service user has permission to read firebase-service-account.json if Firestore is enabled.
- Monitor logs for first-run model download and cache warm-up.

## Development Notes

- Interactive API docs available at /docs (Swagger UI)
- Alternative docs at /redoc
- Logs include detailed steps (model loading, line detection counts, matching debug info) to aid debugging

## Disclaimer

- Parking spot inference relies on visible line markings and typical car spacing; edge cases (e.g., unmarked lots, heavy occlusions, extreme angles) may reduce accuracy. Always validate results for critical applications.
### Backend Setup

1. **Clone and setup Python environment:**
