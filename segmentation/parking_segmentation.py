from __future__ import annotations
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Tuple, Dict, Any

import cv2
import numpy as np


@dataclass
class LineDet:
    start: Tuple[int, int]
    end: Tuple[int, int]
    length: float
    angle_deg: float
    is_horizontal: bool
    is_vertical: bool


@dataclass
class Spot:
    bbox: Tuple[float, float, float, float]  # x1, y1, x2, y2
    area: float
    aspect_ratio: float
    center: Tuple[float, float]
    type: str


def load_image(path: Path) -> np.ndarray:
    img = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError(f"Failed to read image: {path}")
    return img


def detect_white_lines(image: np.ndarray) -> List[LineDet]:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    white_mask = cv2.inRange(gray, 170, 255)

    kernel = np.ones((2, 2), np.uint8)
    white_mask = cv2.morphologyEx(white_mask, cv2.MORPH_CLOSE, kernel)
    white_mask = cv2.morphologyEx(white_mask, cv2.MORPH_OPEN, kernel)

    blurred = cv2.GaussianBlur(white_mask, (3, 3), 0)
    edges = cv2.Canny(blurred, 30, 120, apertureSize=3)

    lines = cv2.HoughLinesP(
        edges, rho=1, theta=np.pi / 180, threshold=40, minLineLength=25, maxLineGap=10
    )

    out: List[LineDet] = []
    if lines is not None:
        for ln in lines:
            x1, y1, x2, y2 = ln[0]
            length = float(np.hypot(x2 - x1, y2 - y1))
            if length < 15:
                continue
            angle = float(np.degrees(np.arctan2(y2 - y1, x2 - x1)))
            is_h = abs(angle) < 25 or abs(angle) > 155
            is_v = 65 < abs(angle) < 115
            out.append(LineDet(start=(x1, y1), end=(x2, y2), length=length, angle_deg=angle, is_horizontal=is_h, is_vertical=is_v))
    return out


def create_spots_from_vertical_dividers(lines: List[LineDet], width: int, height: int) -> List[Spot]:
    vlines = [l for l in lines if l.is_vertical]
    if len(vlines) < 2:
        return []

    vlines.sort(key=lambda l: (l.start[0] + l.end[0]) / 2.0)
    spots: List[Spot] = []
    for i in range(len(vlines) - 1):
        l = vlines[i]
        r = vlines[i + 1]
        lx = (l.start[0] + l.end[0]) / 2.0
        rx = (r.start[0] + r.end[0]) / 2.0
        w = rx - lx
        if not (25 <= w <= 150):
            continue

        ly1, ly2 = sorted([l.start[1], l.end[1]])
        ry1, ry2 = sorted([r.start[1], r.end[1]])
        y_top = max(ly1, ry1)
        y_bot = min(ly2, ry2)
        h = y_bot - y_top
        if h <= 50:
            continue

        margin = min(4.0, w * 0.08)
        x1 = max(0.0, lx + margin)
        x2 = min(float(width), rx - margin)
        if (x2 - x1) <= 20:
            x1, x2 = lx, rx

        x1, y_top, x2, y_bot = float(x1), float(y_top), float(x2), float(y_bot)
        area = (x2 - x1) * (y_bot - y_top)
        ar = (x2 - x1) / max(1.0, (y_bot - y_top))
        cx, cy = (x1 + x2) / 2.0, (y_top + y_bot) / 2.0
        spots.append(Spot(bbox=(x1, y_top, x2, y_bot), area=area, aspect_ratio=ar, center=(cx, cy), type="vertical_divider"))
    return spots


def create_spots_from_horizontal_pairs(lines: List[LineDet], width: int, height: int) -> List[Spot]:
    hlines = [l for l in lines if l.is_horizontal]
    if len(hlines) < 2:
        return []

    hlines.sort(key=lambda l: (l.start[1] + l.end[1]) / 2.0)
    spots: List[Spot] = []
    for i in range(len(hlines) - 1):
        top = hlines[i]
        bot = hlines[i + 1]
        ty = (top.start[1] + top.end[1]) / 2.0
        by = (bot.start[1] + bot.end[1]) / 2.0
        h = by - ty
        if not (40 <= h <= 150):
            continue

        tx1, tx2 = sorted([top.start[0], top.end[0]])
        bx1, bx2 = sorted([bot.start[0], bot.end[0]])
        x_left = max(tx1, bx1)
        x_right = min(tx2, bx2)
        w = x_right - x_left
        if w <= 100:
            continue

        x1, y1, x2, y2 = float(x_left), float(ty), float(x_right), float(by)
        area = (x2 - x1) * (y2 - y1)
        ar = (x2 - x1) / max(1.0, (y2 - y1))
        cx, cy = (x1 + x2) / 2.0, (y1 + y2) / 2.0
        spots.append(Spot(bbox=(x1, y1, x2, y2), area=area, aspect_ratio=ar, center=(cx, cy), type="horizontal_row"))
    return spots


def iou(b1: Tuple[float, float, float, float], b2: Tuple[float, float, float, float]) -> float:
    x1 = max(b1[0], b2[0])
    y1 = max(b1[1], b2[1])
    x2 = min(b1[2], b2[2])
    y2 = min(b1[3], b2[3])
    if x2 <= x1 or y2 <= y1:
        return 0.0
    inter = (x2 - x1) * (y2 - y1)
    a1 = (b1[2] - b1[0]) * (b1[3] - b1[1])
    a2 = (b2[2] - b2[0]) * (b2[3] - b2[1])
    union = a1 + a2 - inter
    return float(inter / union) if union > 0 else 0.0


def filter_and_merge_spots(spots: List[Spot], max_spots: int = 60) -> List[Spot]:
    if not spots:
        return spots

    def priority(s: Spot) -> int:
        if s.type == "vertical_divider":
            return 3
        if s.type == "horizontal_row":
            return 2
        return 1

    spots = [s for s in spots if 800 < s.area < 50000]
    spots.sort(key=lambda s: (priority(s), s.area), reverse=True)

    final: List[Spot] = []
    for s in spots:
        if not any(iou(s.bbox, e.bbox) > 0.4 for e in final):
            final.append(s)
    return final[:max_spots]


def draw_overlay(image: np.ndarray, lines: List[LineDet], spots: List[Spot]) -> np.ndarray:
    out = image.copy()

    for l in lines:
        color = (255, 255, 0)  # cyan
        cv2.line(out, l.start, l.end, color, 2)

    for i, s in enumerate(spots):
        x1, y1, x2, y2 = map(int, s.bbox)
        color = (0, 255, 255) if s.type == "vertical_divider" else (255, 0, 255)
        cv2.rectangle(out, (x1, y1), (x2, y2), color, 3)
        cx, cy = int((x1 + x2) / 2), int((y1 + y2) / 2)
        cv2.circle(out, (cx, cy), 12, (0, 0, 0), -1)
        cv2.circle(out, (cx, cy), 12, color, 2)
        cv2.putText(out, f"{i+1}", (cx - 6, cy + 4), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
    return out


def segment_parking(image: np.ndarray) -> Dict[str, Any]:
    h, w = image.shape[:2]
    lines = detect_white_lines(image)
    spots_v = create_spots_from_vertical_dividers(lines, w, h)
    spots_h = create_spots_from_horizontal_pairs(lines, w, h)
    spots_all = filter_and_merge_spots(spots_v + spots_h)

    return {
        "lines": [asdict(l) for l in lines],
        "spots": [asdict(s) for s in spots_all],
        "counts": {
            "lines_total": len(lines),
            "spots_total": len(spots_all),
            "spots_vertical": len(spots_v),
            "spots_horizontal": len(spots_h),
        },
        "image_size": {"width": w, "height": h},
    }


def process_image_file(img_path: Path, out_dir: Path) -> Dict[str, Any]:
    img = load_image(img_path)
    result = segment_parking(img)
    overlay = draw_overlay(img, [LineDet(**l) for l in result["lines"]], [Spot(**s) for s in result["spots"]])

    out_dir.mkdir(parents=True, exist_ok=True)
    base = img_path.stem
    overlay_path = out_dir / f"{base}_segmented.jpg"
    json_path = out_dir / f"{base}_segmentation.json"

    cv2.imwrite(str(overlay_path), overlay)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "image": str(img_path),
                "overlay": str(overlay_path),
                **result,
            },
            f,
            ensure_ascii=False,
            indent=2,
        )

    print(f"Saved overlay: {overlay_path}")
    print(f"Saved JSON:    {json_path}")
    return result


def main():
    parser = argparse.ArgumentParser(description="Segment parking zones using classical CV (OpenCV)")
    g = parser.add_mutually_exclusive_group(required=True)
    g.add_argument("--image", type=Path, help="Path to a single image")
    g.add_argument("--dir", type=Path, help="Directory of images to process (recursively)")

    parser.add_argument("--out", type=Path, default=Path("outputs/segmentation"), help="Output directory")
    parser.add_argument(
        "--glob", type=str, default="**/*.jpg", help="Glob pattern when using --dir (default: **/*.jpg)"
    )

    args = parser.parse_args()

    if args.image:
        process_image_file(args.image, args.out)
    else:
        imgs = [p for p in args.dir.rglob(args.glob) if p.is_file()]
        if not imgs:
            print(f"No images found under {args.dir} with pattern {args.glob}")
            return
        for p in imgs:
            try:
                process_image_file(p, args.out)
            except Exception as e:
                print(f"Failed to process {p}: {e}")


if __name__ == "__main__":
    main()
import argparse
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Tuple, Dict, Any

import cv2
import numpy as np


@dataclass
class LineDet:
    start: Tuple[int, int]
    end: Tuple[int, int]
    length: float
    angle_deg: float
    is_horizontal: bool
    is_vertical: bool


@dataclass
class Spot:
    bbox: Tuple[float, float, float, float]  # x1, y1, x2, y2
    area: float
    aspect_ratio: float
    center: Tuple[float, float]
    type: str


def load_image(path: Path) -> np.ndarray:
    img = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError(f"Failed to read image: {path}")
    return img


def detect_white_lines(image: np.ndarray) -> List[LineDet]:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    white_mask = cv2.inRange(gray, 170, 255)

    kernel = np.ones((2, 2), np.uint8)
    white_mask = cv2.morphologyEx(white_mask, cv2.MORPH_CLOSE, kernel)
    white_mask = cv2.morphologyEx(white_mask, cv2.MORPH_OPEN, kernel)

    blurred = cv2.GaussianBlur(white_mask, (3, 3), 0)
    edges = cv2.Canny(blurred, 30, 120, apertureSize=3)

    lines = cv2.HoughLinesP(
        edges, rho=1, theta=np.pi / 180, threshold=40, minLineLength=25, maxLineGap=10
    )

    out: List[LineDet] = []
    if lines is not None:
        for ln in lines:
            x1, y1, x2, y2 = ln[0]
            length = float(np.hypot(x2 - x1, y2 - y1))
            if length < 15:
                continue
            angle = float(np.degrees(np.arctan2(y2 - y1, x2 - x1)))
            is_h = abs(angle) < 25 or abs(angle) > 155
            is_v = 65 < abs(angle) < 115
            out.append(LineDet(start=(x1, y1), end=(x2, y2), length=length, angle_deg=angle, is_horizontal=is_h, is_vertical=is_v))
    return out


def create_spots_from_vertical_dividers(lines: List[LineDet], width: int, height: int) -> List[Spot]:
    vlines = [l for l in lines if l.is_vertical]
    if len(vlines) < 2:
        return []

    # sort left->right by x-midpoint
    vlines.sort(key=lambda l: (l.start[0] + l.end[0]) / 2.0)
    spots: List[Spot] = []
    for i in range(len(vlines) - 1):
        l = vlines[i]
        r = vlines[i + 1]
        lx = (l.start[0] + l.end[0]) / 2.0
        rx = (r.start[0] + r.end[0]) / 2.0
        w = rx - lx
        if not (25 <= w <= 150):
            continue

        ly1, ly2 = sorted([l.start[1], l.end[1]])
        ry1, ry2 = sorted([r.start[1], r.end[1]])
        y_top = max(ly1, ry1)
        y_bot = min(ly2, ry2)
        h = y_bot - y_top
        if h <= 50:
            continue

        margin = min(4.0, w * 0.08)
        x1 = max(0.0, lx + margin)
        x2 = min(float(width), rx - margin)
        if (x2 - x1) <= 20:
            x1, x2 = lx, rx

        x1, y_top, x2, y_bot = float(x1), float(y_top), float(x2), float(y_bot)
        area = (x2 - x1) * (y_bot - y_top)
        ar = (x2 - x1) / max(1.0, (y_bot - y_top))
        cx, cy = (x1 + x2) / 2.0, (y_top + y_bot) / 2.0
        spots.append(Spot(bbox=(x1, y_top, x2, y_bot), area=area, aspect_ratio=ar, center=(cx, cy), type="vertical_divider"))
    return spots


def create_spots_from_horizontal_pairs(lines: List[LineDet], width: int, height: int) -> List[Spot]:
    hlines = [l for l in lines if l.is_horizontal]
    if len(hlines) < 2:
        return []

    hlines.sort(key=lambda l: (l.start[1] + l.end[1]) / 2.0)
    spots: List[Spot] = []
    for i in range(len(hlines) - 1):
        top = hlines[i]
        bot = hlines[i + 1]
        ty = (top.start[1] + top.end[1]) / 2.0
        by = (bot.start[1] + bot.end[1]) / 2.0
        h = by - ty
        if not (40 <= h <= 150):
            continue

        tx1, tx2 = sorted([top.start[0], top.end[0]])
        bx1, bx2 = sorted([bot.start[0], bot.end[0]])
        x_left = max(tx1, bx1)
        x_right = min(tx2, bx2)
        w = x_right - x_left
        if w <= 100:
            continue

        x1, y1, x2, y2 = float(x_left), float(ty), float(x_right), float(by)
        area = (x2 - x1) * (y2 - y1)
        ar = (x2 - x1) / max(1.0, (y2 - y1))
        cx, cy = (x1 + x2) / 2.0, (y1 + y2) / 2.0
        spots.append(Spot(bbox=(x1, y1, x2, y2), area=area, aspect_ratio=ar, center=(cx, cy), type="horizontal_row"))
    return spots


def iou(b1: Tuple[float, float, float, float], b2: Tuple[float, float, float, float]) -> float:
    x1 = max(b1[0], b2[0])
    y1 = max(b1[1], b2[1])
    x2 = min(b1[2], b2[2])
    y2 = min(b1[3], b2[3])
    if x2 <= x1 or y2 <= y1:
        return 0.0
    inter = (x2 - x1) * (y2 - y1)
    a1 = (b1[2] - b1[0]) * (b1[3] - b1[1])
    a2 = (b2[2] - b2[0]) * (b2[3] - b2[1])
    union = a1 + a2 - inter
    return float(inter / union) if union > 0 else 0.0


def filter_and_merge_spots(spots: List[Spot], max_spots: int = 60) -> List[Spot]:
    if not spots:
        return spots

    def priority(s: Spot) -> int:
        if s.type == "vertical_divider":
            return 3
        if s.type == "horizontal_row":
            return 2
        return 1

    spots = [s for s in spots if 800 < s.area < 50000]
    spots.sort(key=lambda s: (priority(s), s.area), reverse=True)

    final: List[Spot] = []
    for s in spots:
        if not any(iou(s.bbox, e.bbox) > 0.4 for e in final):
            final.append(s)
    return final[:max_spots]


def draw_overlay(image: np.ndarray, lines: List[LineDet], spots: List[Spot]) -> np.ndarray:
    out = image.copy()

    # Draw lines
    for l in lines:
        color = (255, 255, 0)  # cyan
        cv2.line(out, l.start, l.end, color, 2)

    # Draw spots
    for i, s in enumerate(spots):
        x1, y1, x2, y2 = map(int, s.bbox)
        color = (0, 255, 255) if s.type == "vertical_divider" else (255, 0, 255)
        cv2.rectangle(out, (x1, y1), (x2, y2), color, 3)
        cx, cy = int((x1 + x2) / 2), int((y1 + y2) / 2)
        cv2.circle(out, (cx, cy), 12, (0, 0, 0), -1)
        cv2.circle(out, (cx, cy), 12, color, 2)
        cv2.putText(out, f"{i+1}", (cx - 6, cy + 4), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
    return out


def segment_parking(image: np.ndarray) -> Dict[str, Any]:
    h, w = image.shape[:2]
    lines = detect_white_lines(image)
    spots_v = create_spots_from_vertical_dividers(lines, w, h)
    spots_h = create_spots_from_horizontal_pairs(lines, w, h)
    spots_all = filter_and_merge_spots(spots_v + spots_h)

    return {
        "lines": [asdict(l) for l in lines],
        "spots": [asdict(s) for s in spots_all],
        "counts": {
            "lines_total": len(lines),
            "spots_total": len(spots_all),
            "spots_vertical": len(spots_v),
            "spots_horizontal": len(spots_h),
        },
        "image_size": {"width": w, "height": h},
    }


def process_image_file(img_path: Path, out_dir: Path) -> Dict[str, Any]:
    img = load_image(img_path)
    result = segment_parking(img)
    overlay = draw_overlay(img, [LineDet(**l) for l in result["lines"]], [Spot(**s) for s in result["spots"]])

    out_dir.mkdir(parents=True, exist_ok=True)
    base = img_path.stem
    overlay_path = out_dir / f"{base}_segmented.jpg"
    json_path = out_dir / f"{base}_segmentation.json"

    cv2.imwrite(str(overlay_path), overlay)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "image": str(img_path),
                "overlay": str(overlay_path),
                **result,
            },
            f,
            ensure_ascii=False,
            indent=2,
        )

    print(f"Saved overlay: {overlay_path}")
    print(f"Saved JSON:    {json_path}")
    return result


def main():
    parser = argparse.ArgumentParser(description="Segment parking zones using classical CV (OpenCV)")
    g = parser.add_mutually_exclusive_group(required=True)
    g.add_argument("--image", type=Path, help="Path to a single image")
    g.add_argument("--dir", type=Path, help="Directory of images to process (recursively)")

    parser.add_argument("--out", type=Path, default=Path("outputs/segmentation"), help="Output directory")
    parser.add_argument(
        "--glob", type=str, default="**/*.jpg", help="Glob pattern when using --dir (default: **/*.jpg)"
    )

    args = parser.parse_args()

    if args.image:
        process_image_file(args.image, args.out)
    else:
        imgs = [p for p in args.dir.rglob(args.glob) if p.is_file()]
        if not imgs:
            print(f"No images found under {args.dir} with pattern {args.glob}")
            return
        for p in imgs:
            try:
                process_image_file(p, args.out)
            except Exception as e:
                print(f"Failed to process {p}: {e}")


if __name__ == "__main__":
    main()
