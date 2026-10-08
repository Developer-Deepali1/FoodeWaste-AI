"""
FoodWaste AI - Model Training & Fine-Tuning Pipeline
Uses Ultralytics YOLOv8 / YOLOv11 for multi-object waste detection.
Optimized for Odisha/India regional waste conditions:
- Heavy augmentations for crushed packaging, greasy plates, and dim lighting
- Evaluates mAP@50 and mAP@50:95 across the 5 primary waste categories
"""
import os
from pathlib import Path

def train_model():
    try:
        from ultralytics import YOLO
    except ImportError:
        print("[!] Ultralytics not installed. Install via: pip install ultralytics torch")
        return

    # Base configuration
    dataset_yaml = Path("dataset/data.yaml")
    output_dir = Path("runs/train")
    target_weights_dir = Path("app/models/waste_detector")
    target_weights_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("🌱 FoodWaste AI - Initiating YOLO Multi-Object Training Pipeline")
    print("=" * 60)

    # Load pre-trained nano or small model for fast convergence
    model = YOLO("yolov8n.pt")

    # Hyperparameters tuned for messy canteen & street food waste
    results = model.train(
        data=str(dataset_yaml) if dataset_yaml.exists() else "coco8.yaml",
        epochs=50,
        imgsz=640,
        batch=16,
        patience=10,
        save=True,
        device=0 if os.environ.get("CUDA_VISIBLE_DEVICES") else "cpu",
        
        # Heavy real-world augmentations (simulates crushed and dirty waste)
        hsv_h=0.015,     # Color variation
        hsv_s=0.7,       # Saturation variation
        hsv_v=0.4,       # Brightness variation (simulates dim canteen lighting)
        degrees=15.0,    # Rotation
        translate=0.1,   # Translation
        scale=0.5,       # Scaling
        shear=2.0,       # Shearing (crushed cans/cartons)
        perspective=0.0005,
        flipud=0.2,
        fliplr=0.5,
        mosaic=1.0,      # Combines multiple objects into one scene
        mixup=0.15       # Overlapping transparency
    )

    print("\n✅ Training complete! Evaluating test metrics...")
    metrics = model.val()
    print(f"📊 mAP@50:    {metrics.box.map50:.4f}")
    print(f"📊 mAP@50-95: {metrics.box.map:.4f}")

    # Copy best weights to app model directory
    best_pt = output_dir / "weights" / "best.pt"
    if best_pt.exists():
        import shutil
        dest = target_weights_dir / "best.pt"
        shutil.copy(best_pt, dest)
        print(f"🎯 Saved best weights to: {dest}")

if __name__ == "__main__":
    train_model()
