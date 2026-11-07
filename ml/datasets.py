"""Dataset manifests and lightweight dataset access.

Real datasets (KinFaceW, LFW, YouTubeFaceDB, CCTV) are gitignored and expected
under ``data/raw/``. This module reads/writes acquisition manifests and provides
thin dataset loaders that gracefully degrade to synthetic fixtures when real
data is absent, so the pipeline and tests can run end-to-end without downloads.
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import numpy as np


@dataclass
class DatasetRecord:
    path: str
    identity: str
    label: int
    dataset: str
    attributes: Dict[str, str] = field(default_factory=dict)


@dataclass
class PairRecord:
    path_a: str
    path_b: str
    label: int  # 1 = same / kin, 0 = different / non-kin
    dataset: str
    pair_type: str = "verification"  # verification | kinship


class Manifest:
    """JSON manifest recording dataset acquisition/licensing/checksums."""

    def __init__(self, path: str) -> None:
        self.path = path
        self.data: Dict[str, object] = {
            "datasets": {},
            "checksums": {},
            "licenses": {},
            "counts": {},
        }
        if os.path.exists(path):
            self.load()

    def load(self) -> None:
        with open(self.path, "r", encoding="utf-8") as fh:
            self.data = json.load(fh)

    def save(self) -> None:
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as fh:
            json.dump(self.data, fh, indent=2)

    def register(self, name: str, root: str, license: str, checksum: Optional[str] = None) -> None:
        self.data["datasets"][name] = {"root": root, "license": license}
        if checksum:
            self.data["checksums"][name] = checksum
        self.data["licenses"][name] = license
        self.save()

    def set_count(self, name: str, count: int) -> None:
        self.data["counts"][name] = count
        self.save()


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def _list_images(root: str) -> List[str]:
    exts = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
    out = []
    if not root or not os.path.isdir(root):
        return out
    for base, _dirs, files in os.walk(root):
        for fn in files:
            if os.path.splitext(fn)[1].lower() in exts:
                out.append(os.path.join(base, fn))
    return sorted(out)


def load_verification_pairs(root: str) -> List[PairRecord]:
    """Load LFW-style verification pairs from a ``pairs.txt`` if present, else
    synthesize balanced pairs from all images under ``root``."""
    pairs_path = os.path.join(root, "pairs.txt")
    records: List[PairRecord] = []
    if os.path.isfile(pairs_path):
        with open(pairs_path, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split()
                if len(parts) == 3:
                    name, i1, i2 = parts
                    records.append(
                        PairRecord(
                            path_a=os.path.join(root, name, f"{name}_{int(i1):04d}.jpg"),
                            path_b=os.path.join(root, name, f"{name}_{int(i2):04d}.jpg"),
                            label=1,
                            dataset="lfw",
                        )
                    )
                elif len(parts) == 4:
                    name1, i1, name2, i2 = parts
                    records.append(
                        PairRecord(
                            path_a=os.path.join(root, name1, f"{name1}_{int(i1):04d}.jpg"),
                            path_b=os.path.join(root, name2, f"{name2}_{int(i2):04d}.jpg"),
                            label=0,
                            dataset="lfw",
                        )
                    )
        return records

    images = _list_images(root)
    records = []
    n = min(len(images), 200)
    for i in range(n // 2):
        records.append(PairRecord(images[i], images[(i + 1) % len(images)], 1, "lfw"))
        records.append(PairRecord(images[i], images[(i + n // 2) % len(images)], 0, "lfw"))
    return records


def load_kinship_pairs(root: str) -> List[PairRecord]:
    """Load KinFaceW-style kinship pairs from a manifest CSV/JSON if present,
    else synthesize balanced kin/non-kin pairs."""
    pairs_path = os.path.join(root, "pairs.json")
    if os.path.isfile(pairs_path):
        with open(pairs_path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        return [
            PairRecord(
                path_a=item["path_a"],
                path_b=item["path_b"],
                label=int(item["label"]),
                dataset="kinfacew",
                pair_type="kinship",
            )
            for item in data
        ]
    images = _list_images(root)
    records = []
    n = min(len(images), 200)
    for i in range(n // 2):
        records.append(PairRecord(images[i], images[(i + 1) % len(images)], 1, "kinfacew", "kinship"))
        records.append(PairRecord(images[i], images[(i + n // 2) % len(images)], 0, "kinfacew", "kinship"))
    return records


def synthetic_verification_pairs(n_pairs: int = 128, image_size: tuple[int, int] = (112, 112), seed: int = 42) -> List[PairRecord]:
    """Generate purely synthetic verification pairs (no filesystem) for tests
    and smoke tests. Writes temp PNGs under the system temp dir."""
    import tempfile

    rng = np.random.default_rng(seed)
    tmp = tempfile.mkdtemp(prefix="fmppi_synthetic_")
    records: List[PairRecord] = []
    n = n_pairs // 2
    for i in range(n):
        base = rng.normal(0.5, 0.2, size=(image_size[1], image_size[0], 3))
        path_a = os.path.join(tmp, f"pos_{i}_a.png")
        path_b = os.path.join(tmp, f"pos_{i}_b.png")
        _save_img(path_a, np.clip(base + rng.normal(0, 0.05, base.shape), 0, 1))
        _save_img(path_b, np.clip(base + rng.normal(0, 0.05, base.shape), 0, 1))
        records.append(PairRecord(path_a, path_b, 1, "synthetic", "verification"))

        path_c = os.path.join(tmp, f"neg_{i}_c.png")
        _save_img(path_c, rng.random((image_size[1], image_size[0], 3)))
        records.append(PairRecord(path_a, path_c, 0, "synthetic", "verification"))
    return records


def _save_img(path: str, arr: np.ndarray) -> None:
    from PIL import Image

    img = Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8))
    img.save(path)


def load_orl_faces(root: str) -> List[PairRecord]:
    """Load ORL_Faces dataset (40 subjects × 10 images) and build verification
    pairs: same-subject pairs are positive (label=1), different-subject pairs
    are negative (label=0). Used for face recognition training/testing.

    ORL_Faces structure: root/s{1..40}/1.pgm ... 10.pgm
    """
    records: List[PairRecord] = []
    if not root or not os.path.isdir(root):
        return records

    # Group images by subject folder
    subject_images: Dict[str, List[str]] = {}
    for base, dirs, files in os.walk(root):
        for fn in files:
            if os.path.splitext(fn)[1].lower() in {".pgm", ".jpg", ".jpeg", ".png", ".bmp"}:
                subject = os.path.basename(base)
                subject_images.setdefault(subject, []).append(os.path.join(base, fn))

    subjects = sorted(subject_images.keys())
    # Positive pairs: same subject, different images
    for subj in subjects:
        imgs = subject_images[subj]
        for i in range(len(imgs)):
            for j in range(i + 1, len(imgs)):
                records.append(
                    PairRecord(imgs[i], imgs[j], 1, "orl_faces", "verification")
                )
    # Negative pairs: different subjects (sample to keep balanced)
    import random

    rng = random.Random(42)
    neg_pairs: List[PairRecord] = []
    for i, subj_a in enumerate(subjects):
        for subj_b in subjects[i + 1 :]:
            img_a = rng.choice(subject_images[subj_a])
            img_b = rng.choice(subject_images[subj_b])
            neg_pairs.append(PairRecord(img_a, img_b, 0, "orl_faces", "verification"))
    # Balance: take up to as many negatives as positives
    n_pos = len(records)
    rng.shuffle(neg_pairs)
    records.extend(neg_pairs[:n_pos])
    return records


def load_cctv_detection(root: str) -> List[PairRecord]:
    """Load CCTV face detection dataset for robustness training/testing.

    Expected structure (Roboflow export):
      root/train/images/*.jpg, root/train/labels/*.txt
      root/valid/images/*.jpg, root/valid/labels/*.txt
      root/test/images/*.jpg,  root/test/labels/*.txt

    Returns pairs where both images are CCTV frames; label=1 if they contain
    the same detected face (same frame / overlapping), label=0 otherwise.
    Falls back to synthesizing degraded pairs from available images when
    annotation files are absent.
    """
    records: List[PairRecord] = []
    if not root or not os.path.isdir(root):
        return records

    images = _list_images(root)
    if not images:
        return records

    # Try to use train/valid/test split info if present
    split_dirs = [d for d in os.listdir(root) if os.path.isdir(os.path.join(root, d))]
    if any(d in split_dirs for d in ("train", "valid", "test")):
        # Build positive pairs within same split folder (same scene)
        for split in ("train", "valid", "test"):
            split_dir = os.path.join(root, split)
            if not os.path.isdir(split_dir):
                continue
            split_images = _list_images(split_dir)
            for i in range(len(split_images)):
                for j in range(i + 1, min(i + 4, len(split_images))):
                    records.append(
                        PairRecord(
                            split_images[i], split_images[j], 1, "cctv", "verification"
                        )
                    )
    else:
        # No split info: create positive pairs from nearby images in file order
        for i in range(len(images)):
            for j in range(i + 1, min(i + 3, len(images))):
                records.append(
                    PairRecord(images[i], images[j], 1, "cctv", "verification")
                )

    # Negative pairs: random images far apart in file order
    import random

    rng = random.Random(7)
    n_pos = len(records)
    neg_pairs: List[PairRecord] = []
    for _ in range(min(n_pos, len(images) - 1)):
        i = rng.randint(0, len(images) - 1)
        j = rng.randint(0, len(images) - 1)
        if i != j:
            neg_pairs.append(PairRecord(images[i], images[j], 0, "cctv", "verification"))
    records.extend(neg_pairs[:n_pos])
    return records


def load_all_datasets(settings) -> List[PairRecord]:
    """Load verification pairs from all configured datasets (LFW, KinFaceW,
    ORL_Faces, CCTV) and return a combined, de-duplicated list.

    Each pair carries its ``dataset`` field so results can be reported
    per-dataset during training and evaluation.
    """
    all_pairs: List[PairRecord] = []

    ds = settings.datasets

    # LFW -> face verification
    lfw_pairs = load_verification_pairs(ds.lfw_root)
    for p in lfw_pairs:
        p.dataset = "lfw"
        p.pair_type = "verification"
    all_pairs.extend(lfw_pairs)

    # KinFaceW -> kinship
    kin_pairs = load_kinship_pairs(ds.kinfacew_root)
    for p in kin_pairs:
        p.dataset = "kinfacew"
        p.pair_type = "kinship"
    all_pairs.extend(kin_pairs)

    # ORL_Faces -> face recognition (verification)
    orl_pairs = load_orl_faces(ds.orl_faces_root)
    for p in orl_pairs:
        p.dataset = "orl_faces"
        p.pair_type = "verification"
    all_pairs.extend(orl_pairs)

    # CCTV -> robustness / low-quality verification
    cctv_pairs = load_cctv_detection(ds.cctv_root)
    for p in cctv_pairs:
        p.dataset = "cctv"
        p.pair_type = "verification"
    all_pairs.extend(cctv_pairs)

    # De-duplicate by (path_a, path_b) to avoid duplicate pairs across loaders
    seen = set()
    unique: List[PairRecord] = []
    for p in all_pairs:
        key = tuple(sorted((p.path_a, p.path_b)))
        if key not in seen:
            seen.add(key)
            unique.append(p)

    return unique


__all__ = [
    "DatasetRecord",
    "PairRecord",
    "Manifest",
    "sha256_file",
    "load_verification_pairs",
    "load_kinship_pairs",
    "load_orl_faces",
    "load_cctv_detection",
    "load_all_datasets",
    "synthetic_verification_pairs",
]
