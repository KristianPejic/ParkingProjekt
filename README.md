# Parking Detection System and Parking-Zone Segmentation

A comprehensive project for analyzing parking lots with computer vision:
- Production API that detects cars, infers parking spots, and returns annotated results.
- Research track for segmenting parking zones (from aerial or CCTV images) using classical CV and/or deep learning.
- Optional persistence to Firestore and a frontend-ready API (CORS enabled).

Contents:
- Quick Start
- Architecture Overview
- Technologies and Packages
- API Overview (car detection + occupancy)
- Frontend UI: Screens & Visualizations
- Research Track: Segmentation of Parking Zones
- Dataset (PKLot via KaggleHub)
- Methodology and Metrics
- Usage Examples (CLI and API)
- Local Development (Backend & Frontend)
- Run with Docker Compose
- Environment Variables
- Troubleshooting and Tips
- License and Acknowledgments

## Quick Start

1) Create and activate a virtual environment
- python -m venv .venv
- macOS/Linux: source .venv/bin/activate
- Windows (PowerShell): .\.venv\Scripts\Activate.ps1

2) Install dependencies
- pip install -r requirements.txt
- Note: On first detection run, YOLOv8 weights are downloaded automatically.

3) Run the API (development)
- uvicorn main:app --reload --host 0.0.0.0 --port 8000
- Open http://localhost:8000/docs for interactive API docs

4) Optional: Configure Firestore
- Place a service account JSON in project root named: firebase-service-account.json
- If not present, API still runs with database features disabled.

## Architecture Overview

- Backend (Python/FastAPI): runs car and parking-spot analysis (white-line + row-based inference), returns metadata and an annotated image (Base64).
- Frontend (Vue 3 + Vite): upload images, visualize detections, and explore analytics/training charts.
- Storage (optional): Firestore used to store detection metadata for history/stats.
- Dataset & Training View: PKLot dataset accessed via KaggleHub for classical CV feature analysis and clustering (KMeans).

Data flow:
1) Frontend uploads an image to the API.
2) Backend detects cars and infers parking spots; returns counts, confidence, and annotated image.
3) Optional metadata is stored in Firestore for history/statistics.
4) Training view queries /train to compute dataset features and returns chart-ready data.

## Technologies and Packages

Backend
- Language: Python 3.13.5
- Framework: FastAPI
- ASGI server: Uvicorn
- Vision/ML:
  - ultralytics (YOLOv8) for detection
  - opencv-python (OpenCV)
  - numpy
  - scipy (KMeans via kmeans2)
  - pillow
- Cloud/DB (optional):
  - firebase-admin (Firestore)
  - google-cloud-storage (optional utility)
- HTTP/Utils: requests, pyyaml, click, protobuf, six, pyparsing, sympy (utility/optional)
- Plotting/Graphs (optional utilities): matplotlib, networkx

Frontend
- Vue: 3.3.4
- Vite: 4.4.9
- @vitejs/plugin-vue: 4.3.4
- Router: vue-router 4.2.4
- HTTP: axios 1.5.0

Dev/Runtime
- Virtual environments: venv (or virtualenv)
- Node.js + npm for frontend

## API Overview (Car Detection + Occupancy)

- Purpose: Given a parking-lot image, detect cars, infer parking spots (white-line + row-based), match occupancy, and return an annotated image as Base64.
- Key endpoints:
  - GET / — API info
  - GET /health — Model and database status
  - POST /detect — Main detection (multipart/form-data, field: file; optional: total_slots)
  - POST /debug-detect — Raw detections for debugging
  - POST /simple-test — Minimal YOLO run to validate environment
  - POST /test-class67 — Report real-car vs. “misclassified car” counts
  - GET /last-result — Latest stored metadata
  - GET /history — Detection history (metadata only)
  - GET /stats — Aggregate stats (requires Firestore)
  - GET /train — Dataset analysis (features, clustering, charts)

Notes:
- If white-line inference is weak for a given image, the system augments with row-based estimation. As a last resort, it falls back to simple counting vs. total_slots.

## Frontend UI: Screens & Visualizations

Detection (Upload/Analyze)
- Cards: Free, Occupied, Total, Confidence.
- Occupancy gauge: circular gauge showing percentage of occupied slots.
- Annotated image: returned as Base64 (no file hosting needed).
- Vehicles detected: total count.

Training Dashboard (/train)
- Coverage gauge: processed vs total images in the dataset.
- White Ratio Histogram: distribution of bright-pixel fractions (proxy for painted lines).
- Scatter — White Ratio vs Edge Density: structure richness vs line brightness, colored by cluster.
- Cluster Distribution: counts per KMeans cluster.
- Edge Density Histogram: distribution of edge density values derived from scatter points.
- Cluster Centers (Grouped Bars): per-cluster feature means for white ratio, edge density, and brightness (all in [0,1]).

Training Dashboard Chart Guide (what each chart is for)
- Coverage gauge
  - Purpose: Indicates how much of the dataset was analyzed in the current run (progress).
  - Use it to judge representativeness: low coverage suggests results are a quick sample; high coverage means stronger confidence in the distribution summaries.
- White Ratio Histogram
  - Purpose: Shows how frequently images contain large areas of bright/white pixels (a proxy for painted parking lines).
  - Interpretation: Peaks at higher white ratios imply lots with strong, visible markings; lower values may indicate faded lines, shadows, or nighttime images.
- Scatter — White Ratio vs Edge Density
  - Purpose: Visualizes relationship between painted lines (white ratio) and structural richness (edge density), colored by KMeans cluster.
  - Interpretation: Clusters reveal typical scenes (e.g., “high-lines-high-edges” vs “low-lines-low-edges”). Outliers may be problematic frames or different viewpoints.
- Cluster Distribution
  - Purpose: Counts the number of samples assigned to each KMeans cluster.
  - Interpretation: A dominant cluster means the dataset has a prevalent scene type; balanced clusters indicate diverse conditions (lighting, texture, layout).
- Edge Density Histogram
  - Purpose: Distribution of edge density values (how busy/structured images are).
  - Interpretation: Higher edge density can correspond to many lines, cars, or clutter; low density suggests simpler scenes or smooth surfaces (e.g., snow, glare).
- Cluster Centers (Grouped Bars)
  - Purpose: Shows the mean feature values per cluster for white ratio, edge density, and brightness (normalized to [0,1]).
  - Interpretation: Use as “fingerprints” of each cluster (e.g., Cluster 1 = bright lines + rich edges; Cluster 2 = dim, low-structure scenes). Helpful for selecting target clusters for further training or filtering.

Statistics (/stats)
- Occupancy Trend — % of slots occupied per detection (last N runs).
- Slots per Detection — Free vs Occupied (stacked counts).
- Detection Confidence Distribution — model certainty histogram.
- All charts are stacked vertically for readability.

History (/history)
- Cards for past detections with free/occupied/total counts and confidence indicators.

## Research Track: Segmentation of Parking Zones

Problem statement (what and why):
- Segment parking zones on images captured from drones, satellites, or fixed CCTV.
- Automate boundary extraction for parking stalls, detect painted white lines, and identify obstacles.
- Enables Smart Parking, live occupancy inference, urban infrastructure planning, and GIS-ready data exports.

Project goals:
- Automatic segmentation of line markings that define parking stalls.
- Recognition of entire parking areas or rows.
- Visual analysis of organization and occupancy cues.
- Produce outputs that can be consumed by GIS or downstream analytics.

Approaches:
- Classical CV (OpenCV)
  - Grayscale conversion
  - Thresholding for bright/white markings
  - Morphological filtering and edge detection (Canny)
  - Hough transforms for line extraction
  - Post-processing to create rectangles between line pairs (vertical/horizontal)
- Deep Learning (optional extension)
  - Semantic segmentation (e.g., U-Net/DeepLab) trained on annotated masks
  - Instance-level stall detection (custom datasets/labels required)

Deliverables in this repo:
- CLI segmentation pipeline (classical CV) that:
  - Finds white lines
  - Builds candidate stall rectangles from vertical/horizontal line pairs
  - Filters/merges plausible spots
  - Saves overlay images and JSON summaries

Command-line tool:
- python segmentation/parking_segmentation.py --image path/to/image.jpg --out outputs/segmentation
- python segmentation/parking_segmentation.py --dir path/to/images --glob "**/*.jpg" --out outputs/segmentation

Outputs:
- Overlay image with detected lines and stall rectangles
- JSON file with line definitions, stall bboxes, image size, and counts

## Dataset: PKLot via KaggleHub

This project integrates the PKLot dataset for experimentation.

Download the dataset:
- python datasets/download_pklot.py
- By default, it downloads via KaggleHub and copies into datasets/pklot (configurable with --copy-to; use --no-copy to skip copying and just print the cache path).

Notes:
- PKLot images include multiple parking lots and weather conditions; they are suitable for classical CV experiments and for building segmentation training sets.

## Methodology and Metrics

Classical CV baseline (provided):
- Preprocessing: grayscale → white mask (threshold) → morphology → Canny edges
- Structure detection: HoughLinesP
- Stall inference:
  - Vertical dividers: create spots between adjacent vertical lines with sufficient overlap
  - Horizontal pairs: create row rectangles between adjacent horizontal lines with sufficient width
- Filtering and de-duplication by area, aspect ratio, and IoU

Suggested evaluation metrics:
- Precision/recall or IoU against a ground-truth mask or stall polygons (if available)
- Count-based accuracy (# stalls identified vs. annotated)
- Coverage of painted lines (percentage of white-line pixels explained by detected structure)

Result presentation:
- Side-by-side: original vs. overlay
- Quantitative tables: per-image and aggregate metrics
- Qualitative examples: successes and failure cases (e.g., faint markings, occlusion, oblique angles)

## Usage Examples

1) Run the detector API and test with a local image:
- uvicorn main:app --reload
- curl -X POST "http://localhost:8000/detect" -F "file=@/path/to/parking.jpg"

2) Run segmentation on a single image:
- python segmentation/parking_segmentation.py --image datasets/pklot/SomeLot/image.jpg --out outputs/segmentation

3) Batch process a folder:
- python segmentation/parking_segmentation.py --dir datasets/pklot --glob "**/*.jpg" --out outputs/segmentation

4) Download PKLot dataset:
- python datasets/download_pklot.py
- Optional args:
  - --copy-to datasets/pklot_custom
  - --no-copy (to only print KaggleHub cache path)

## Local Development

Backend
- Create venv and install: pip install -r requirements.txt
- Run: uvicorn main:app --reload --host 0.0.0.0 --port 8000
- Docs: http://localhost:8000/docs

Frontend
- cd frontend
- npm install
- npm run dev
- Dev server runs on http://localhost:3000 with a proxy forwarding /api to the backend.

## Run with Docker Compose

- docker-compose up --build
- Frontend on http://localhost:3000
- Backend on http://localhost:8000

## Environment Variables

Backend
- FIREBASE_SERVICE_ACCOUNT=/app/firebase-service-account.json (path inside container)
- FIREBASE_STORAGE_BUCKET=your-bucket-name (optional)

Frontend
- VITE_API_URL=http://localhost:8000 (used by the dev/proxy or deployments)

## Troubleshooting and Tips

- KaggleHub:
  - Ensure internet access on first run.
  - If authentication is required, configure Kaggle credentials per tool instructions.
- OpenCV decoding:
  - Ensure input files are actual images; JPG/PNG recommended.
- Weak or faded line markings:
  - Adjust lighting, resolution, or camera angle if possible.
  - Consider tuning thresholds or adding adaptive thresholding.
- Performance:
  - Use reasonably sized images (e.g., around 1280px width).
  - Batch CLI runs if processing entire datasets.
- Extending to deep learning segmentation:
  - Prepare pixel-level masks or stall polygons from PKLot or a custom labeled subset.
  - Train a segmentation model (e.g., U-Net) and integrate its inference path alongside or instead of the classical CV pipeline.

## License and Acknowledgments

- The PKLot dataset is provided by its respective authors and hosted on Kaggle; please review PKLot and Kaggle terms of use.
- This repository includes classical CV utilities for research and a detection API for practical integration scenarios.
