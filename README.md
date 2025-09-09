# Parking Detection System and Parking-Zone Segmentation

A comprehensive project for analyzing parking lots with computer vision:
- Production API that detects cars, infers parking spots, and returns annotated results.
- Research track for segmenting parking zones (from aerial or CCTV images) using classical CV and/or deep learning.
- Optional persistence to Firestore and a frontend-ready API (CORS enabled).

Contents:
- Quick Start
- API Overview (car detection + occupancy)
- Research Track: Segmentation of Parking Zones
- Dataset (PKLot via KaggleHub)
- Methodology and Metrics
- Usage Examples (CLI and API)
- Troubleshooting and Tips

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

## API Overview (Car Detection + Occupancy)

- Purpose: Given a parking-lot image, detect cars, infer parking spots (white-line + row-based), match occupancy, and return an annotated image as Base64.
- Key endpoints:
  - GET / — API info
  - GET /health — Model and database status
  - POST /detect — Main detection (multipart/form-data, field: file; optional: total_slots)
  - POST /debug-detect — Raw detections for debugging
  - POST /simple-test — Minimal YOLO run to validate environment
  - POST /test-class67 — Class-2 vs. class-67 “car-like” report
  - GET /last-result, /history, /stats — Firestore-backed metadata endpoints (optional)

Notes:
- If white-line inference is not reliable in an image, the system augments with row-based estimation. As a last resort, it falls back to simple counting vs. total_slots.

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

Direct code snippet (if you need it in your own scripts):
- import kagglehub
- path = kagglehub.dataset_download("ammarnassanalhajali/pklot-dataset")
- print("Path to dataset files:", path)

Notes:
- Public datasets usually work out of the box with KaggleHub. If authentication is required, configure Kaggle credentials as prompted by the tool or refer to KaggleHub documentation.
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
- Or: python datasets/download_pklot.py --copy-to datasets/pklot_custom
- Or: python datasets/download_pklot.py --no-copy  (to only print KaggleHub cache path)

## Troubleshooting and Tips

- KaggleHub:
  - Ensure internet access on first run.
  - For any authentication prompts/issues, configure Kaggle credentials or re-run with appropriate environment.
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

## Notes on Production API

- The API supports CORS for easy frontend integration.
- Annotated image is returned as a data URL (Base64) and can be rendered directly in web apps.
- Firestore persistence is optional and can be enabled by placing the service account JSON in the project root.

## License and Acknowledgments

- The PKLot dataset is provided by its respective authors and hosted on Kaggle; please review PKLot and Kaggle terms of use.
- This repository includes classical CV utilities for research and a detection API for practical integration scenarios.
