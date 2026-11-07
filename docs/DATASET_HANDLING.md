# Dataset Handling

## Datasets
- KinFaceW (I/II): kinship pairs (parent-child, siblings)
- LFW: face verification pairs
- YouTubeFaceDB: video frames, pose/illumination variation
- CCTV samples: low-quality, occlusion, aging

## Acquisition & Licensing
- Download via official sources; record license; store raw in `data/raw/` (gitignored)
- Checksum verification; metadata manifest (JSON)

### Dataset download sources
| Dataset | Source URL | License | Notes |
|---|---|---|---|
| LFW | http://vis-www.cs.umass.edu/lfw/ | Non-commercial research use | Face verification pairs |
| KinFaceW I & II | https://sites.google.com/site/kfacew/ | Research use | Kinship pairs (parent-child, siblings) |
| YouTubeFaceDB | https://www.cs.tau.ac.il/~wolf/ytfaces/ | Research use | Video frames, pose/illumination variation |
| CCTV samples | Curated internally / public CCTV datasets | Varies | Low-quality, occlusion, aging |

### Download script (`scripts/download_datasets.py`)
```python
"""Download and verify FMPPI datasets. Run: python scripts/download_datasets.py"""
import hashlib
from pathlib import Path
import urllib.request

RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)

DATASETS = {
    "lfw": {
        "url": "http://vis-www.cs.umass.edu/lfw/lfw.tgz",
        "sha256": None,  # fill in after download
        "description": "LFW face verification dataset",
    },
}

def download(url: str, dest: Path) -> None:
    print(f"Downloading {url} -> {dest}")
    urllib.request.urlretrieve(url, dest)

def verify_sha256(path: Path, expected: str | None) -> bool:
    if not expected:
        print(f"  [skip] no checksum for {path.name}")
        return True
    h = hashlib.sha256(path.read_bytes()).hexdigest()
    ok = h == expected
    print(f"  {'OK' if ok else 'FAIL'} sha256 {path.name}")
    return ok

if __name__ == "__main__":
    for name, meta in DATASETS.items():
        dest = RAW_DIR / f"{name}.tgz"
        if dest.exists():
            print(f"{name}: already downloaded")
        else:
            download(meta["url"], dest)
        verify_sha256(dest, meta["sha256"])
```

After download, extract archives into `data/raw/<dataset>/` and create a manifest:
```json
{
  "dataset": "lfw",
  "version": "1.0",
  "source": "http://vis-www.cs.umass.edu/lfw/",
  "license": "non-commercial research use",
  "sha256": "<checksum>",
  "n_pairs": 5749,
  "downloaded_at": "2026-11-07T00:00:00Z"
}
```

## Preprocessing
- Face detection (YoloFace/DeepFace), alignment (5-point landmarks), resize 112x112/160x160
- Quality filtering: blur score, min face size, occlusion estimate
- Normalization: mean/std per dataset; augmentation pipeline

## Stratification & Splits
- Split by identity (no leakage), stratified by age bin, pose, illumination, occlusion
- Train/val/test = 70/15/15; k-fold for kinship

## Augmentation
- Blur, Gaussian noise, JPEG compression, low-res downscale, random occlusion, brightness/contrast, pose perturbation, aging (synthetic)

## Versioning & Storage
- DVC for dataset versioning; manifests in `data/manifests/`
- Anonymization: remove PII, hash filenames, consent log

## Ethics & Compliance
- IRB/ethics review; bias audit across demographics; fairness metrics
