"""Train the VisionOps safety detection model.

Fine-tunes a YOLOv8 checkpoint (pretrained on COCO) on the construction site
safety dataset prepared by scripts/prepare_dataset.py. YOLOv8 was chosen
because it gives a strong accuracy/latency trade-off for real time video
inference on commodity hardware and ships with a stable, well documented
Python API (ultralytics) that the backend can reuse directly for serving.

Usage:
    python src/train.py --epochs 50 --model yolov8n.pt --imgsz 640
"""

import argparse
from pathlib import Path

from ultralytics import YOLO

DEFAULT_DATA_YAML = Path(__file__).resolve().parent.parent / "configs" / "dataset.yaml"
DEFAULT_RUNS_DIR = Path(__file__).resolve().parent.parent / "runs"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA_YAML, help="Path to the dataset yaml.")
    parser.add_argument("--model", type=str, default="yolov8n.pt", help="Base checkpoint to fine-tune from.")
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--batch", type=int, default=16)
    parser.add_argument("--patience", type=int, default=15, help="Early stopping patience in epochs.")
    parser.add_argument("--device", type=str, default=None, help="cuda device id, 'cpu', or None for auto-detect.")
    parser.add_argument("--run-name", type=str, default="visionops_ppe", help="Name of the training run folder.")
    parser.add_argument("--project", type=Path, default=DEFAULT_RUNS_DIR)
    args = parser.parse_args()

    model = YOLO(args.model)

    model.train(
        data=str(args.data),
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        patience=args.patience,
        device=args.device,
        project=str(args.project),
        name=args.run_name,
        exist_ok=True,
        plots=True,
    )

    best_weights = args.project / args.run_name / "weights" / "best.pt"
    print(f"\nTraining complete. Best weights saved to: {best_weights}")


if __name__ == "__main__":
    main()
