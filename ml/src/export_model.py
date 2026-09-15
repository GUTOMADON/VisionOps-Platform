"""Export a trained checkpoint for serving and copy it into ml/models.

The backend loads whatever file is in ml/models/production. Exporting to
ONNX is optional (useful for non-torch runtimes) but the PyTorch checkpoint
is what the FastAPI service loads by default through the ultralytics
runtime, since it keeps pre and post processing identical to training.

Usage:
    python src/export_model.py --weights runs/visionops_ppe/weights/best.pt
    python src/export_model.py --weights runs/visionops_ppe/weights/best.pt --format onnx
"""

import argparse
import shutil
from pathlib import Path

from ultralytics import YOLO

DEFAULT_MODELS_DIR = Path(__file__).resolve().parent.parent / "models"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--weights", type=Path, required=True, help="Path to a trained .pt checkpoint.")
    parser.add_argument("--format", type=str, default="pt", choices=["pt", "onnx"], help="Export format.")
    parser.add_argument("--models-dir", type=Path, default=DEFAULT_MODELS_DIR)
    parser.add_argument("--name", type=str, default="visionops_ppe", help="Base filename for the exported model.")
    args = parser.parse_args()

    args.models_dir.mkdir(parents=True, exist_ok=True)

    if args.format == "pt":
        destination = args.models_dir / f"{args.name}.pt"
        shutil.copy2(args.weights, destination)
        print(f"Copied checkpoint to {destination}")
    else:
        model = YOLO(str(args.weights))
        exported_path = Path(model.export(format="onnx"))
        destination = args.models_dir / f"{args.name}.onnx"
        shutil.copy2(exported_path, destination)
        print(f"Exported ONNX model to {destination}")

    print("Point MODEL_PATH in the backend .env to this file to serve it.")


if __name__ == "__main__":
    main()
