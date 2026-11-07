"""Detection strategies: FaceDetector interface (Strategy pattern).

Interface:
    FaceDetector.detect(image) -> List[Detection]

Each Detection carries a bounding box (x1, y1, x2, y2), confidence, and optional
5-point landmarks. Implementations wrap YoloFace and DeepFace detectors and
degrade gracefully when their weights/backends are unavailable.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Protocol, runtime_checkable

import numpy as np


@dataclass
class Detection:
    bbox: np.ndarray  # [x1, y1, x2, y2]
    confidence: float
    landmarks: Optional[np.ndarray] = None  # (5, 2) or None


@runtime_checkable
class FaceDetector(Protocol):
    def detect(self, image: np.ndarray) -> List[Detection]:  # pragma: no cover - interface
        ...

    def name(self) -> str:  # pragma: no cover - interface
        ...


def detection_to_chip_inputs(detections: List[Detection]) -> List[tuple[np.ndarray, Optional[np.ndarray]]]:
    return [(d.bbox, d.landmarks) for d in detections]
