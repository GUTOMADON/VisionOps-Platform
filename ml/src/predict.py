"""Run a trained model on a folder of images or a video and save annotated
output. Used to produce the sample predictions and demo GIF embedded in the
root README, and doubles as a quick manual sanity check after training.

Usage:
    python src/predict.py --weights ml/models/visionops_ppe.pt --source samples/images --out reports/sample_predictions
    python src/predict.py --weights ml/models/visionops_ppe.pt --source samples/clip.mp4 --out reports --gif
"""

import argparse
from pathlib import Path

import imageio.v2 as imageio
import numpy as np
from PIL import Image
from ultralytics import YOLO

GIF_FRAME_SIZE = (640, 480)


def build_gif(frames_dir: Path, gif_path: Path, fps: int = 2) -> None:
    """Assemble annotated frames into a GIF, resizing to a common size first
    since source images keep their original, varying aspect ratio."""
    frame_paths = sorted(frames_dir.glob("*.jpg")) + sorted(frames_dir.glob("*.png"))
    if not frame_paths:
        print(f"No frames found in {frames_dir}, skipping GIF creation.")
        return

    images = []
    for path in frame_paths:
        with Image.open(path) as image:
            resized = image.convert("RGB").resize(GIF_FRAME_SIZE)
            images.append(np.array(resized))

    imageio.mimsave(gif_path, images, fps=fps)
    print(f"Wrote demo GIF to {gif_path} from {len(images)} frames.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--weights", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True, help="Image, folder of images, or video file.")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--conf", type=float, default=0.35)
    parser.add_argument("--gif", action="store_true", help="Also assemble a GIF from the annotated frames.")
    args = parser.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)

    model = YOLO(str(args.weights))
    results = model.predict(
        source=str(args.source),
        conf=args.conf,
        save=True,
        project=str(args.out.parent),
        name=args.out.name,
        exist_ok=True,
    )
    print(f"Saved {len(results)} annotated results to {args.out}")

    if args.gif:
        build_gif(args.out, args.out / "demo.gif")


if __name__ == "__main__":
    main()
