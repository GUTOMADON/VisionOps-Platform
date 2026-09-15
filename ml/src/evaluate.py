"""Evaluate a trained VisionOps model and export reporting artifacts.

Runs validation on the held-out split, then copies the confusion matrix and
precision-recall curve that Ultralytics generates internally into
ml/reports, and writes a metrics.json plus a metrics.md table that the root
README embeds directly. This keeps the "Results" section of the README
reproducible from a single command instead of hand-typed numbers.

Usage:
    python src/evaluate.py --weights runs/visionops_ppe/weights/best.pt
"""

import argparse
import json
import shutil
from pathlib import Path

from ultralytics import YOLO

DEFAULT_DATA_YAML = Path(__file__).resolve().parent.parent / "configs" / "dataset.yaml"
DEFAULT_REPORTS_DIR = Path(__file__).resolve().parent.parent / "reports"


def build_per_class_metrics(results) -> dict:
    """Map each class name to its precision, recall and mAP@0.5.

    Ultralytics only returns metric array entries for classes that actually
    appeared in the validation set, and `results.box.ap_class_index` gives
    the class id each array position corresponds to. Classes with no
    ground truth instances in the split are reported as None rather than
    being silently misaligned with the wrong class name.
    """
    class_names = results.names
    class_index_to_position = {int(class_id): pos for pos, class_id in enumerate(results.box.ap_class_index)}

    per_class = {}
    for class_id, name in class_names.items():
        position = class_index_to_position.get(int(class_id))
        if position is None:
            per_class[name] = {"precision": None, "recall": None, "ap50": None}
        else:
            per_class[name] = {
                "precision": float(results.box.p[position]),
                "recall": float(results.box.r[position]),
                "ap50": float(results.box.ap50[position]),
            }
    return per_class


def build_metrics_markdown(per_class: dict, overall: dict) -> str:
    lines = [
        "| Class | Precision | Recall | mAP@0.5 |",
        "|---|---|---|---|",
    ]
    for name, values in per_class.items():
        if values["precision"] is None:
            lines.append(f"| {name} | - | - | - |")
        else:
            lines.append(f"| {name} | {values['precision']:.3f} | {values['recall']:.3f} | {values['ap50']:.3f} |")

    lines.append("")
    lines.append(
        f"**Overall: mAP@0.5 = {overall['map50']:.3f}, mAP@0.5:0.95 = {overall['map']:.3f}, "
        f"precision = {overall['precision']:.3f}, recall = {overall['recall']:.3f}**"
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--weights", type=Path, required=True, help="Path to a trained .pt checkpoint.")
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA_YAML)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--reports-dir", type=Path, default=DEFAULT_REPORTS_DIR)
    parser.add_argument("--split", type=str, default="val", choices=["val", "test"])
    args = parser.parse_args()

    args.reports_dir.mkdir(parents=True, exist_ok=True)

    model = YOLO(str(args.weights))
    results = model.val(data=str(args.data), imgsz=args.imgsz, split=args.split, plots=True)

    save_dir = Path(results.save_dir)
    for artifact_name, dest_name in [
        ("confusion_matrix_normalized.png", "confusion_matrix.png"),
        ("PR_curve.png", "pr_curve.png"),
    ]:
        source = save_dir / artifact_name
        if source.exists():
            shutil.copy2(source, args.reports_dir / dest_name)
            print(f"Copied {source} -> {args.reports_dir / dest_name}")

    overall = {
        "map50": float(results.box.map50),
        "map": float(results.box.map),
        "precision": float(results.box.mp),
        "recall": float(results.box.mr),
    }
    per_class = build_per_class_metrics(results)

    metrics = {"overall": overall, "per_class": per_class}

    metrics_json_path = args.reports_dir / "metrics.json"
    with open(metrics_json_path, "w", encoding="utf-8") as handle:
        json.dump(metrics, handle, indent=2)
    print(f"Wrote {metrics_json_path}")

    metrics_md = build_metrics_markdown(per_class, overall)
    metrics_md_path = args.reports_dir / "metrics.md"
    with open(metrics_md_path, "w", encoding="utf-8") as handle:
        handle.write(metrics_md)
    print(f"Wrote {metrics_md_path}")


if __name__ == "__main__":
    main()
