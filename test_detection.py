import cv2
import numpy as np
from ultralytics import YOLO
import requests

def test_yolo_detection():
    """Test YOLO detection with a simple test"""

    print("🔍 Testing YOLO Detection...")

    # Load model
    try:
        model = YOLO('yolov8m.pt')
        print("✅ Model loaded successfully")
        print(f"Model names: {model.names}")
    except Exception as e:
        print(f"❌ Model loading failed: {e}")
        # Try nano version
        try:
            model = YOLO('yolov8n.pt')
            print("✅ Nano model loaded as fallback")
        except Exception as e2:
            print(f"❌ All model loading failed: {e2}")
            return

    # Test with a simple image (create test image with shapes)
    print("\n📊 Testing with synthetic image...")
    test_image = np.zeros((480, 640, 3), dtype=np.uint8)
    # Draw some rectangles to simulate cars
    cv2.rectangle(test_image, (50, 50), (150, 100), (255, 255, 255), -1)
    cv2.rectangle(test_image, (200, 50), (300, 100), (128, 128, 128), -1)

    # Test detection
    results = model(test_image, conf=0.01, verbose=True)

    print(f"Results type: {type(results)}")
    print(f"Number of results: {len(results)}")

    for i, result in enumerate(results):
        print(f"\nResult {i}:")
        print(f"  Boxes: {result.boxes}")
        if result.boxes is not None:
            print(f"  Number of boxes: {len(result.boxes)}")
            for j, box in enumerate(result.boxes):
                class_id = int(box.cls[0])
                confidence = float(box.conf[0])
                class_name = model.names.get(class_id, "unknown")
                print(f"    Box {j}: Class {class_id} ({class_name}), Conf: {confidence:.3f}")
        else:
            print("  No boxes found")

    # Test with online image
    print("\n🌐 Testing with online car image...")
    try:
        # Download a test car image
        url = "https://images.unsplash.com/photo-1549317661-bd32c8ce0db2?w=640&h=480&fit=crop"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            nparr = np.frombuffer(response.content, np.uint8)
            online_image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if online_image is not None:
                print(f"Online image shape: {online_image.shape}")
                online_results = model(online_image, conf=0.1, verbose=True)

                for result in online_results:
                    if result.boxes is not None:
                        print(f"Online image detections: {len(result.boxes)}")
                        for box in result.boxes:
                            class_id = int(box.cls[0])
                            confidence = float(box.conf[0])
                            class_name = model.names.get(class_id, "unknown")
                            print(f"  Detected: {class_name} (conf: {confidence:.3f})")
                    else:
                        print("No detections in online image")
            else:
                print("Failed to decode online image")
    except Exception as e:
        print(f"Online image test failed: {e}")

    print("\n🎯 Vehicle classes in COCO dataset:")
    vehicle_classes = [2, 3, 5, 7]  # car, motorcycle, bus, truck
    for class_id in vehicle_classes:
        if class_id in model.names:
            print(f"  Class {class_id}: {model.names[class_id]}")

if __name__ == "__main__":
    test_yolo_detection()
