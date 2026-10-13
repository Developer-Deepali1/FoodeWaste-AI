"""
FoodWaste AI - Model Training & Fine-Tuning Pipeline
Uses Ultralytics YOLOv8 / YOLOv11 for multi-object waste detection.
Optimized for Odisha/India regional waste conditions:
- Heavy augmentations for crushed packaging, greasy plates, and dim lighting
- Evaluates mAP@50 and mAP@50:95 across the 5 primary waste categories
"""
import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_DATASET = PROJECT_ROOT / "dataset" / "data.yaml"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "runs" / "train"
DEFAULT_TARGET_WEIGHTS_DIR = PROJECT_ROOT / "app" / "models" / "waste_detector"


def _select_device():
    """Use CUDA only when PyTorch confirms that it is available."""
    try:
        import torch
    except ImportError:
        return "cpu"
    return 0 if torch.cuda.is_available() else "cpu"


def train_model(
    dataset_yaml: Path = DEFAULT_DATASET,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    target_weights_dir: Path = DEFAULT_TARGET_WEIGHTS_DIR,
):
    try:
        from ultralytics import YOLO
    except ImportError:
        raise RuntimeError(
            "Ultralytics is not installed. Install training dependencies with: "
            "pip install ultralytics torch"
        ) from None

    dataset_yaml = Path(dataset_yaml).expanduser().resolve()
    output_dir = Path(output_dir).expanduser().resolve()
    target_weights_dir = Path(target_weights_dir).expanduser().resolve()
    if not dataset_yaml.is_file():
        raise FileNotFoundError(
            f"Dataset configuration not found: {dataset_yaml}. "
            "Create dataset/data.yaml before training."
        )

    target_weights_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("🌱 FoodWaste AI - Initiating YOLO Multi-Object Training Pipeline")
    print("=" * 60)

    # Load pre-trained nano or small model for fast convergence
    model = YOLO("yolov8n.pt")

    # Hyperparameters tuned for messy canteen & street food waste
    model.train(
        data=str(dataset_yaml),
        epochs=50,
        imgsz=640,
        batch=16,
        patience=10,
        save=True,
        project=str(output_dir),
        name="waste_detector",
        exist_ok=True,
        device=_select_device(),
        
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
    metrics = model.val(data=str(dataset_yaml))
    print(f"📊 mAP@50:    {metrics.box.map50:.4f}")
    print(f"📊 mAP@50-95: {metrics.box.map:.4f}")

    # Copy best weights to app model directory
    run_dir = Path(getattr(model.trainer, "save_dir", output_dir / "waste_detector"))
    best_pt = run_dir / "weights" / "best.pt"
    if best_pt.exists():
        dest = target_weights_dir / "best.pt"
        shutil.copy(best_pt, dest)
        print(f"🎯 Saved best weights to: {dest}")

if __name__ == "__main__":
    train_model()
