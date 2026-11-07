"""Configuration loading for the FMPPI ML pipeline.

Loads a YAML config file and exposes a small, attribute-style settings object.
All paths are resolved relative to the project root (repository root) so the
pipeline is runnable from any working directory.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field, fields
from typing import Any, Dict, List, get_origin, get_type_hints

import yaml

_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))


def _resolve(path: str | None) -> str | None:
    if path is None:
        return None
    if os.path.isabs(path):
        return path
    return os.path.normpath(os.path.join(_PROJECT_ROOT, path))


@dataclass
class ImageConfig:
    size: List[int] = field(default_factory=lambda: [112, 112])
    channels: int = 3
    embedding_dim: int = 512
    normalization: str = "mean_std"

    @property
    def width(self) -> int:
        return int(self.size[0])

    @property
    def height(self) -> int:
        return int(self.size[1])


@dataclass
class DatasetConfig:
    kinfacew_root: str = "data/raw/kinfacew"
    lfw_root: str = "data/raw/lfw"
    youtube_facedb_root: str = "data/raw/youtube_facedb"
    cctv_root: str = "data/raw/cctv"
    orl_faces_root: str = "data/raw/orl_faces"
    manifests_dir: str = "data/manifests"
    synthetic_fallback: bool = True


@dataclass
class DetectorConfig:
    name: str = "yolo_face"
    yolo_weights: str = "models/registry/yoloface.pt"
    conf_threshold: float = 0.45
    input_size: int = 640
    device: str = "cpu"


@dataclass
class EmbedderConfig:
    name: str = "deepface"
    deepface_model_name: str = "Facenet"
    deepface_detector_backend: str = "opencv"
    enforce_detection: bool = False
    alignment: bool = True


@dataclass
class FMPPIConfig:
    encoder: str = "cnn"
    loss: str = "contrastive"
    margin: float = 1.0
    learning_rate: float = 1e-3
    lr_schedule: str = "cosine"
    epochs: int = 40
    batch_size: int = 32
    val_split: float = 0.15
    test_split: float = 0.15
    early_stopping_patience: int = 7
    augmentation: bool = True
    synthetic_samples_per_class: int = 64


@dataclass
class MLflowConfig:
    tracking_uri: str = "./mlruns"
    experiment_name: str = "fmppi"
    register_model: bool = True
    model_name: str = "fmppt-siamese"
    artifact_root: str = "models/registry"


@dataclass
class ONNXConfig:
    export: bool = True
    output_path: str = "models/registry/fmppt.onnx"
    opset: int = 13
    batch_size: int = 1


@dataclass
class SearchConfig:
    index_path: str = "models/registry/search_index.json"
    top_k: int = 10
    distance: str = "cosine"
    threshold: float = 0.4


@dataclass
class RobustnessConfig:
    severities: List[str] = field(default_factory=lambda: ["mild", "moderate", "severe"])
    degradations: List[str] = field(
        default_factory=lambda: ["blur", "noise", "low_res", "pose", "illum", "occlusion", "aging"]
    )
    gate_min_accuracy: float = 0.60


@dataclass
class GatesConfig:
    g2_tar_at_far_1e_3: float = 0.99
    g3_kinship_accuracy: float = 0.75
    g4_robustness_accuracy: float = 0.60


@dataclass
class ServingConfig:
    p95_target_seconds: float = 2.0
    batch_inference: bool = True


@dataclass
class Settings:
    project: str = "fmppi"
    seed: int = 42
    image: ImageConfig = field(default_factory=ImageConfig)
    datasets: DatasetConfig = field(default_factory=DatasetConfig)
    detector: DetectorConfig = field(default_factory=DetectorConfig)
    embedder: EmbedderConfig = field(default_factory=EmbedderConfig)
    fmppt: FMPPIConfig = field(default_factory=FMPPIConfig)
    mlflow: MLflowConfig = field(default_factory=MLflowConfig)
    onnx: ONNXConfig = field(default_factory=ONNXConfig)
    search: SearchConfig = field(default_factory=SearchConfig)
    robustness: RobustnessConfig = field(default_factory=RobustnessConfig)
    gates: GatesConfig = field(default_factory=GatesConfig)
    serving: ServingConfig = field(default_factory=ServingConfig)
    _raw: Dict[str, Any] = field(default_factory=dict, repr=False)


def load_config(path: str | os.PathLike[str] = "config/default.yaml") -> Settings:
    """Load a YAML config file into a :class:`Settings` object.

    Missing keys fall back to the dataclass defaults. Paths that are relative
    are resolved against the repository root.
    """
    config_path = _resolve(str(path)) if not os.path.isabs(str(path)) else str(path)
    with open(config_path, "r", encoding="utf-8") as fh:
        raw = yaml.safe_load(fh) or {}

    settings = Settings(
        project=str(raw.get("project", "fmppi")),
        seed=int(raw.get("seed", 42)),
    )

    def _set(section: str, cls: type, defaults: Dict[str, Any]) -> None:
        block = raw.get(section, {}) or {}
        merged = {**defaults, **block}
        merged = _coerce(cls, merged)
        obj = cls(**merged)
        setattr(settings, section, obj)

    _set("image", ImageConfig, {
        "size": list(raw.get("image", {}).get("size", [112, 112])),
        "channels": int(raw.get("image", {}).get("channels", 3)),
        "embedding_dim": int(raw.get("image", {}).get("embedding_dim", 512)),
        "normalization": str(raw.get("image", {}).get("normalization", "mean_std")),
    })
    _set("datasets", DatasetConfig, {})
    _set("detector", DetectorConfig, {})
    _set("embedder", EmbedderConfig, {})
    _set("fmppt", FMPPIConfig, {})
    _set("mlflow", MLflowConfig, {})
    _set("onnx", ONNXConfig, {})
    _set("search", SearchConfig, {})
    _set("robustness", RobustnessConfig, {})
    _set("gates", GatesConfig, {})
    _set("serving", ServingConfig, {})

    settings._raw = raw
    return settings


def _coerce(cls: type, merged: Dict[str, Any]) -> Dict[str, Any]:
    """Cast config values to the dataclass-declared field types (PyYAML parses
    scientific notation such as ``1e-3`` as a string)."""
    out = dict(merged)
    hints = get_type_hints(cls)
    for f in fields(cls):
        if f.name not in out:
            continue
        v = out[f.name]
        t = hints.get(f.name, f.type)
        origin = get_origin(t)
        if origin is not None:
            continue
        if isinstance(v, str):
            if t is float:
                try:
                    out[f.name] = float(v)
                except ValueError:
                    pass
            elif t is int:
                try:
                    out[f.name] = int(float(v))
                except ValueError:
                    pass
            elif t is bool:
                out[f.name] = str(v).lower() in ("true", "1", "yes", "y")
    return out


def resolve(path: str) -> str:
    """Resolve a (possibly relative) path against the repository root."""
    return _resolve(path)
