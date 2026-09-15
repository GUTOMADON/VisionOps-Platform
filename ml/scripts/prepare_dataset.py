"""Normalize a downloaded YOLO-format dataset into the layout expected by
train.py and configs/dataset.yaml.

Both download sources (Roboflow export and the COCO128 sample) ship images
and labels in YOLO txt format but with different folder conventions
(Roboflow uses train/valid/test, COCO128 ships a single train2017 split with
no validation set). This script normalizes either one into:

    ml/data/processed/images/{train,val,test}/*.jpg
    ml/data/processed/labels/{train,val,test}/*.txt

and rewrites configs/dataset.yaml with the class names discovered in the
source dataset, so downstream scripts never need to know which source was
used.

Usage:
    python scripts/prepare_dataset.py --raw-dir ../data/raw --output-dir ../data/processed
"""

import argparse
import random
import shutil
from pathlib import Path

import yaml

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp"}


def find_source_yaml(raw_dir: Path) -> Path:
    """Locate the dataset descriptor YAML shipped by the download source."""
    candidates = list(raw_dir.rglob("data.yaml")) + list(raw_dir.rglob("*.yaml"))
    if not candidates:
        raise FileNotFoundError(
            f"No dataset yaml found under {raw_dir}. Run download_dataset.py first."
        )
    return candidates[0]


def collect_split_pairs(base_dir: Path, split_dir: str) -> list[tuple[Path, Path]]:
    """Return (image_path, label_path) pairs for a given split folder."""
    images_dir = base_dir / split_dir if (base_dir / split_dir).exists() else None
    if images_dir is None:
        # Roboflow layout nests an extra "images" folder per split.
        alt = base_dir / split_dir.replace("images", "").strip("/") / "images"
        images_dir = alt if alt.exists() else None
    if images_dir is None or not images_dir.exists():
        return []

    labels_dir = Path(str(images_dir).replace("images", "labels"))
    pairs = []
    for image_path in sorted(images_dir.iterdir()):
        if image_path.suffix.lower() not in IMAGE_EXTENSIONS:
            continue
        label_path = labels_dir / f"{image_path.stem}.txt"
        pairs.append((image_path, label_path if label_path.exists() else None))
    return pairs


def copy_pairs(pairs: list[tuple[Path, Path]], output_dir: Path, split: str) -> None:
    images_out = output_dir / "images" / split
    labels_out = output_dir / "labels" / split
    images_out.mkdir(parents=True, exist_ok=True)
    labels_out.mkdir(parents=True, exist_ok=True)

    for image_path, label_path in pairs:
        shutil.copy2(image_path, images_out / image_path.name)
        if label_path is not None:
            shutil.copy2(label_path, labels_out / f"{image_path.stem}.txt")
        else:
            # No annotation file means "no objects in this image" in YOLO format.
            (labels_out / f"{image_path.stem}.txt").touch()

    print(f"  {split}: {len(pairs)} images")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, default=Path(__file__).resolve().parent.parent / "data" / "raw")
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent.parent / "data" / "processed")
    parser.add_argument("--val-split", type=float, default=0.15, help="Fraction reserved for validation when the source has no val split.")
    parser.add_argument("--test-split", type=float, default=0.05, help="Fraction reserved for testing when the source has no test split.")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    random.seed(args.seed)

    source_yaml_path = find_source_yaml(args.raw_dir)
    with open(source_yaml_path, "r", encoding="utf-8") as handle:
        source_meta = yaml.safe_load(handle)

    class_names = source_meta.get("names")
    if isinstance(class_names, list):
        class_names = {i: name for i, name in enumerate(class_names)}
    if not class_names:
        raise ValueError(f"Could not find class names in {source_yaml_path}")

    base_dir = source_yaml_path.parent
    train_pairs = collect_split_pairs(base_dir, source_meta.get("train", "images/train"))
    val_pairs = collect_split_pairs(base_dir, source_meta.get("val", "images/val"))
    test_pairs = collect_split_pairs(base_dir, source_meta.get("test", "images/test"))

    if not val_pairs and train_pairs:
        print("No validation split found in source dataset, splitting train set.")
        random.shuffle(train_pairs)
        n_val = max(1, int(len(train_pairs) * args.val_split))
        n_test = max(0, int(len(train_pairs) * args.test_split))
        val_pairs = train_pairs[:n_val]
        test_pairs = train_pairs[n_val:n_val + n_test] if not test_pairs else test_pairs
        train_pairs = train_pairs[n_val + n_test:]

    if args.output_dir.exists():
        shutil.rmtree(args.output_dir)

    print(f"Writing processed dataset to {args.output_dir}")
    copy_pairs(train_pairs, args.output_dir, "train")
    copy_pairs(val_pairs, args.output_dir, "val")
    copy_pairs(test_pairs, args.output_dir, "test")

    dataset_yaml_path = Path(__file__).resolve().parent.parent / "configs" / "dataset.yaml"
    dataset_yaml = {
        "path": str(args.output_dir.resolve()),
        "train": "images/train",
        "val": "images/val",
        "test": "images/test",
        "names": class_names,
    }
    with open(dataset_yaml_path, "w", encoding="utf-8") as handle:
        yaml.safe_dump(dataset_yaml, handle, sort_keys=False)

    print(f"Wrote {dataset_yaml_path} with {len(class_names)} classes.")


if __name__ == "__main__":
    main()
