"""Download the training data used by the VisionOps safety detection model.

The production dataset is the public "Construction Site Safety Image Dataset"
hosted on Roboflow Universe. It contains ten classes covering PPE compliance
(hardhat, mask, safety vest) and their violation counterparts (NO-Hardhat,
NO-Mask, NO-Safety Vest), plus person, safety cone, machinery and vehicle.

Downloading the full dataset requires a free Roboflow account and API key
(https://app.roboflow.com), because Roboflow gates programmatic export behind
authentication even for public projects. Set ROBOFLOW_API_KEY in the
environment or in a .env file before running with --source roboflow.

For environments without a Roboflow key (CI, quick smoke tests, first time
setup) this script also supports --source sample, which pulls a small,
publicly hosted subset of COCO (COCO128, ~7 MB, no authentication required)
so the rest of the pipeline (prepare, train, evaluate, export) can be
exercised end to end without any external credentials.

Usage:
    python scripts/download_dataset.py --source roboflow --output-dir ../data/raw
    python scripts/download_dataset.py --source sample --output-dir ../data/raw
"""

import argparse
import os
import sys
import urllib.request
import zipfile
from pathlib import Path

import yaml

SAMPLE_DATASET_URL = "https://ultralytics.com/assets/coco128.zip"

ROBOFLOW_WORKSPACE = "roboflow-universe-projects"
ROBOFLOW_PROJECT = "construction-site-safety"
ROBOFLOW_VERSION = 27


def write_sample_dataset_yaml(dataset_dir: Path) -> None:
    """Write the small data.yaml describing COCO128, mirroring the one shipped
    inside the ultralytics package. The public zip only contains images and
    labels, so prepare_dataset.py needs this file to discover the split."""
    coco_names = [
        "person", "bicycle", "car", "motorcycle", "airplane", "bus", "train", "truck", "boat",
        "traffic light", "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat", "dog",
        "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe", "backpack", "umbrella",
        "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball", "kite",
        "baseball bat", "baseball glove", "skateboard", "surfboard", "tennis racket", "bottle",
        "wine glass", "cup", "fork", "knife", "spoon", "bowl", "banana", "apple", "sandwich",
        "orange", "broccoli", "carrot", "hot dog", "pizza", "donut", "cake", "chair", "couch",
        "potted plant", "bed", "dining table", "toilet", "tv", "laptop", "mouse", "remote",
        "keyboard", "cell phone", "microwave", "oven", "toaster", "sink", "refrigerator", "book",
        "clock", "vase", "scissors", "teddy bear", "hair drier", "toothbrush",
    ]
    data = {
        "path": str(dataset_dir),
        "train": "images/train2017",
        "val": "images/train2017",
        "names": {i: name for i, name in enumerate(coco_names)},
    }
    with open(dataset_dir / "data.yaml", "w", encoding="utf-8") as handle:
        yaml.safe_dump(data, handle, sort_keys=False)


def download_sample(output_dir: Path) -> None:
    """Download the small no-auth COCO128 sample used for smoke testing."""
    output_dir.mkdir(parents=True, exist_ok=True)
    zip_path = output_dir / "coco128.zip"

    print(f"Downloading sample dataset from {SAMPLE_DATASET_URL} ...")
    urllib.request.urlretrieve(SAMPLE_DATASET_URL, zip_path)

    print(f"Extracting to {output_dir} ...")
    with zipfile.ZipFile(zip_path, "r") as archive:
        archive.extractall(output_dir)

    zip_path.unlink()
    write_sample_dataset_yaml(output_dir / "coco128")

    print("Sample dataset ready. This is a generic-object smoke test set, not")
    print("the safety/PPE dataset. It is used only to verify the training and")
    print("evaluation pipeline runs correctly end to end.")


def download_roboflow(output_dir: Path) -> None:
    """Download the real PPE safety dataset from Roboflow Universe."""
    try:
        from roboflow import Roboflow
    except ImportError:
        print("The 'roboflow' package is required for this source. Install it")
        print("with: pip install -r requirements.txt")
        sys.exit(1)

    api_key = os.environ.get("ROBOFLOW_API_KEY")
    if not api_key:
        print("ROBOFLOW_API_KEY is not set. Create a free account at")
        print("https://app.roboflow.com, generate an API key, and export it:")
        print("  export ROBOFLOW_API_KEY=your_key_here   (Linux / macOS)")
        print("  $env:ROBOFLOW_API_KEY = 'your_key_here'  (PowerShell)")
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)
    rf = Roboflow(api_key=api_key)
    project = rf.workspace(ROBOFLOW_WORKSPACE).project(ROBOFLOW_PROJECT)
    version = project.version(ROBOFLOW_VERSION)

    print(f"Downloading {ROBOFLOW_WORKSPACE}/{ROBOFLOW_PROJECT} v{ROBOFLOW_VERSION} ...")
    dataset = version.download("yolov8", location=str(output_dir))
    print(f"Dataset downloaded to {dataset.location}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        choices=["roboflow", "sample"],
        default="sample",
        help="Where to download data from. 'roboflow' requires ROBOFLOW_API_KEY "
        "and downloads the full PPE dataset. 'sample' downloads a small, "
        "public, no-auth dataset for smoke testing (default).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "data" / "raw",
        help="Directory to store the downloaded dataset (default: ml/data/raw).",
    )
    args = parser.parse_args()

    if args.output_dir.exists() and any(args.output_dir.iterdir()):
        print(f"{args.output_dir} already contains files, skipping download.")
        print("Delete the directory first to force a re-download.")
        return

    if args.source == "sample":
        download_sample(args.output_dir)
    else:
        download_roboflow(args.output_dir)


if __name__ == "__main__":
    main()
