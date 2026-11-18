import itertools
import json
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from src.generator import GenerationEngine

RESULTS = PROJECT_ROOT / "data" / "processed" / "colab_v1_img2img_sin_preservacion"
OUTPUT = Path(__file__).resolve().parent / "datos" / "metricas_imagenes.json"


def load(path: Path) -> np.ndarray:
    return np.asarray(Image.open(path).convert("RGB").resize((512, 512)))


def face_region(image: np.ndarray, box) -> np.ndarray:
    x, y, w, h = box
    return image[y + int(0.30 * h): y + int(0.75 * h), x + int(0.25 * w): x + int(0.75 * w)]


def lab_mean(region: np.ndarray) -> np.ndarray:
    lab = cv2.cvtColor(region, cv2.COLOR_RGB2LAB).astype(np.float32)
    lab[..., 0] *= 100.0 / 255.0
    lab[..., 1:] -= 128.0
    return lab.reshape(-1, 3).mean(axis=0)


def pairwise_diversity(images) -> float:
    small = [cv2.resize(img, (128, 128)).astype(np.float32) / 255.0 for img in images]
    distances = [float(np.abs(a - b).mean()) for a, b in itertools.combinations(small, 2)]
    return round(float(np.mean(distances)), 4)


def main() -> None:
    reference = load(RESULTS / "01_entrada_512.png")
    box = GenerationEngine().detect_face(reference)
    reference_lab = lab_mean(face_region(reference, box))
    metrics = json.loads((RESULTS / "metricas.json").read_text(encoding="utf-8"))

    rows = []
    groups = {}
    for record in metrics["records"]:
        image = load(RESULTS / record["file"])
        lab = lab_mean(face_region(image, box))
        delta = lab - reference_lab
        row = {
            "group": record["group"],
            "file": record["file"],
            "preset_id": record["preset_id"],
            "strength": record["strength"],
            "seconds": record["elapsed_seconds"],
            "delta_L": round(float(delta[0]), 2),
            "delta_E": round(float(np.linalg.norm(delta)), 2),
        }
        rows.append(row)
        groups.setdefault(record["group"], []).append((row, image))

    summary = {"face_box_512": box, "reference_L": round(float(reference_lab[0]), 2), "groups": {}}
    for group, items in groups.items():
        group_rows = [row for row, _ in items]
        summary["groups"][group] = {
            "n": len(group_rows),
            "mean_seconds": round(float(np.mean([r["seconds"] for r in group_rows])), 2),
            "mean_delta_L": round(float(np.mean([r["delta_L"] for r in group_rows])), 2),
            "mean_delta_E": round(float(np.mean([r["delta_E"] for r in group_rows])), 2),
            "pairwise_diversity": pairwise_diversity([img for _, img in items]) if len(items) > 2 else None,
        }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps({"summary": summary, "images": rows}, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    for row in rows:
        print(row)


if __name__ == "__main__":
    main()
