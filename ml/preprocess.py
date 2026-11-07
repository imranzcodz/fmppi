"""Face preprocessing: detection alignment, cropping, normalization.

The FMPPI model operates on aligned face chips (112x112 or 160x160) with
mean/std normalization. This module is detector-agnostic: it accepts bounding
boxes from any :class:`ml.detection.base.FaceDetector` implementation and
produces normalized chips ready for the encoder.
"""

from __future__ import annotations

import cv2
import numpy as np


class FaceChip:
    """A detected and aligned face chip with metadata."""

    def __init__(
        self,
        image: np.ndarray,
        bbox: np.ndarray | list | tuple,
        landmarks: np.ndarray | None = None,
        confidence: float = 1.0,
    ) -> None:
        self.image = np.asarray(image, dtype=np.float32)
        self.bbox = np.asarray(bbox, dtype=np.float32).reshape(4)
        self.landmarks = (
            np.asarray(landmarks, dtype=np.float32).reshape(-1, 2)
            if landmarks is not None
            else None
        )
        self.confidence = float(confidence)


def xywh_to_xyxy(bbox: np.ndarray | list | tuple) -> np.ndarray:
    """Convert [x, y, w, h] to [x1, y1, x2, y2]."""
    b = np.asarray(bbox, dtype=np.float32).reshape(4)
    return np.array([b[0], b[1], b[0] + b[2], b[1] + b[3]], dtype=np.float32)


def clip_bbox(bbox: np.ndarray, width: int, height: int) -> np.ndarray:
    """Clip a bounding box to image bounds."""
    b = np.asarray(bbox, dtype=np.float32).reshape(4)
    b[0] = float(min(max(b[0], 0), width - 1))
    b[1] = float(min(max(b[1], 0), height - 1))
    b[2] = float(min(max(b[2], b[0] + 1), width))
    b[3] = float(min(max(b[3], b[1] + 1), height))
    return b


def expand_bbox(
    bbox: np.ndarray, scale: float = 1.2, width: int | None = None, height: int | None = None
) -> np.ndarray:
    """Expand a bbox around its center by ``scale`` (optionally clipped)."""
    b = np.asarray(bbox, dtype=np.float32).reshape(4)
    cx = (b[0] + b[2]) / 2.0
    cy = (b[1] + b[3]) / 2.0
    w = (b[2] - b[0]) * scale
    h = (b[3] - b[1]) * scale
    out = np.array([cx - w / 2.0, cy - h / 2.0, cx + w / 2.0, cy + h / 2.0], dtype=np.float32)
    if width is not None and height is not None:
        out = clip_bbox(out, width, height)
    return out


def estimate_affine_transform(
    landmarks: np.ndarray, target_size: int | tuple[int, int] = 112
) -> np.ndarray:
    """Estimate a similarity transform aligning 5 landmarks to a reference.

    Reference landmarks (for 112x112) approximated from a standard frontal
    face template; scaled for other sizes.
    """
    if landmarks is None or landmarks.shape[0] < 5:
        return None
    ref = np.array(
        [
            [0.3488, 0.4046],  # left eye
            [0.6512, 0.4046],  # right eye
            [0.5000, 0.5600],  # nose
            [0.3700, 0.7200],  # left mouth
            [0.6300, 0.7200],  # right mouth
        ],
        dtype=np.float32,
    )
    size = (target_size, target_size) if isinstance(target_size, int) else target_size
    ref = ref * np.array([size[0], size[1]], dtype=np.float32)
    src = landmarks[:5].astype(np.float32)
    # Use OpenCV estimateAffinePartial2D (similarity: scale + rotation + translation)
    M, _ = cv2.estimateAffinePartial2D(src, ref, method=cv2.LMEDS)
    return M


def align_and_crop(
    image: np.ndarray,
    bbox: np.ndarray | list | tuple | None = None,
    landmarks: np.ndarray | None = None,
    size: int | tuple[int, int] = 112,
    expand_scale: float = 1.2,
) -> np.ndarray:
    """Detect-align a face chip.

    If landmarks are available, align via similarity transform; otherwise crop
    the (expanded) bounding box and resize.
    """
    img = np.asarray(image)
    h, w = img.shape[:2]
    size = (size, size) if isinstance(size, int) else tuple(size)

    if landmarks is not None and landmarks.shape[0] >= 5:
        M = estimate_affine_transform(landmarks, size)
        if M is not None:
            chip = cv2.warpAffine(img, M, size, flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
            return chip

    if bbox is not None:
        b = clip_bbox(xywh_to_xyxy(bbox) if len(np.asarray(bbox).reshape(-1)) == 4 else np.asarray(bbox).reshape(4), w, h)
        if np.any(b[2:] <= b[:2]):
            # Degenerate box: fall back to center crop
            cw, ch = min(w, size[0]), min(h, size[1])
            x0 = (w - cw) // 2
            y0 = (h - ch) // 2
            chip = img[y0 : y0 + ch, x0 : x0 + cw]
        else:
            b = expand_bbox(b, expand_scale, w, h)
            chip = img[int(b[1]) : int(b[3]), int(b[0]) : int(b[2])]
    else:
        chip = img

    if chip.size == 0:
        chip = img
    return cv2.resize(chip, size, interpolation=cv2.INTER_LINEAR)


def normalize(image: np.ndarray, mode: str = "mean_std") -> np.ndarray:
    """Normalize a face chip to float32 in a model-friendly range."""
    img = np.asarray(image, dtype=np.float32)
    if mode == "zero_one":
        return img / 255.0
    if mode == "mean_std":
        # ImageNet-style per-channel mean/std on BGR (OpenCV default)
        mean = np.array([123.675, 116.28, 103.53], dtype=np.float32)
        std = np.array([58.395, 57.12, 57.375], dtype=np.float32)
        return (img - mean) / std
    if mode == "none":
        return img
    raise ValueError(f"Unknown normalization mode: {mode}")


def preprocess(
    image: np.ndarray,
    bbox: np.ndarray | list | tuple | None = None,
    landmarks: np.ndarray | None = None,
    size: int | tuple[int, int] = 112,
    normalization: str = "mean_std",
    expand_scale: float = 1.2,
) -> np.ndarray:
    """End-to-end chip extraction + normalization, ready for the encoder."""
    chip = align_and_crop(image, bbox=bbox, landmarks=landmarks, size=size, expand_scale=expand_scale)
    return normalize(chip, mode=normalization)
