"""Optimized dataset verification script."""
from __future__ import annotations

import json
from pathlib import Path
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATASET_DIR = PROJECT_ROOT / "dataset" / "ai_museum_cnn"
MODEL_DIR = PROJECT_ROOT / "cnn" / "model"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

EXPECTED_CLASSES = [
    "expressionism",
    "impressionism",
    "post-impressionism",
    "realism",
    "romanticism",
    "surrealism",
]


def verify_dataset():
    print(f"Scanning dataset at: {DATASET_DIR.resolve()}")
    if not DATASET_DIR.exists():
        raise FileNotFoundError(f"Dataset directory {DATASET_DIR} does not exist!")

    splits = ["train", "validation", "test"]
    stats = {}
    corrupt_images = []
    total_valid_images = 0

    for split in splits:
        split_dir = DATASET_DIR / split
        stats[split] = {}
        if not split_dir.exists():
            print(f"Warning: Split directory {split_dir} does not exist!")
            continue

        for cls_name in EXPECTED_CLASSES:
            cls_dir = split_dir / cls_name
            if not cls_dir.exists():
                matching = [d for d in split_dir.glob("*") if d.name.lower() == cls_name.lower()]
                if matching:
                    cls_dir = matching[0]

            valid_count = 0
            if cls_dir.exists():
                for img_path in cls_dir.glob("*"):
                    if img_path.is_file() and not img_path.name.startswith("."):
                        try:
                            # Fast header check
                            with Image.open(img_path) as img:
                                img.draft(None, (1, 1))
                            valid_count += 1
                        except Exception as e:
                            print(f"[CORRUPT IMAGE] {img_path}: {e}")
                            corrupt_images.append(str(img_path))

            stats[split][cls_name] = valid_count
            total_valid_images += valid_count

    class_names = sorted(EXPECTED_CLASSES)
    class_mapping_path = MODEL_DIR / "class_names.json"
    class_mapping_path.write_text(json.dumps(class_names, indent=2))

    results = {
        "dataset_dir": str(DATASET_DIR),
        "total_valid_images": total_valid_images,
        "corrupt_images_count": len(corrupt_images),
        "corrupt_images": corrupt_images,
        "split_counts": stats,
        "classes": class_names,
    }

    report_path = MODEL_DIR / "dataset_stats.json"
    report_path.write_text(json.dumps(results, indent=2), encoding="utf-8")

    print("\n--- DATASET VERIFICATION COMPLETE ---")
    print(f"Total Valid Images: {total_valid_images}")
    print(f"Corrupt Images Found: {len(corrupt_images)}")
    print("\nPer-Split & Per-Class Counts:")
    for split, counts in stats.items():
        print(f"  [{split.upper()}] (Total: {sum(counts.values())})")
        for cls, count in counts.items():
            print(f"    - {cls}: {count}")

    print(f"\nSaved class mapping to: {class_mapping_path}")
    print(f"Saved stats report to: {report_path}")
    return results


if __name__ == "__main__":
    verify_dataset()
