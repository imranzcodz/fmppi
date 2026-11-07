"""Robustness degradation augmentations.

Applies synthetic degradations (blur, noise, low-res, pose, illumination,
occlusion, aging) at mild/moderate/severe severity. All functions accept and
return uint8 HWC images (BGR) and are deterministic given a seed.
"""

from __future__ import annotations

import cv2
import numpy as np

_SEVERITY_FACTORS = {"mild": 1.0, "moderate": 2.0, "severe": 3.0}


def _factor(severity: str) -> float:
    return _SEVERITY_FACTORS.get(severity, 1.0)


def to_uint8(img: np.ndarray) -> np.ndarray:
    arr = np.asarray(img)
    if arr.dtype != np.uint8:
        arr = np.clip(arr, 0, 255).astype(np.uint8)
    return arr


def blur(img: np.ndarray, severity: str = "mild", seed: int = 0) -> np.ndarray:
    """Gaussian blur; kernel grows with severity."""
    img = to_uint8(img)
    k = int(3 + 2 * _factor(severity)) | 1  # odd
    rng = np.random.default_rng(seed)
    # add slight randomness to kernel
    k = int(k + rng.integers(0, 2)) | 1
    return cv2.GaussianBlur(img, (k, k), 0)


def noise(img: np.ndarray, severity: str = "mild", seed: int = 0) -> np.ndarray:
    """Gaussian + salt-and-pepper noise."""
    img = to_uint8(img).astype(np.float32)
    rng = np.random.default_rng(seed)
    scale = {"mild": 0.02, "moderate": 0.06, "severe": 0.12}[severity]
    gauss = rng.normal(0, scale * 255, img.shape).astype(np.float32)
    out = np.clip(img + gauss, 0, 255).astype(np.uint8)
    # salt & pepper
    n_pixels = int(img.size * ({"mild": 0.005, "moderate": 0.015, "severe": 0.03}[severity]))
    coords = [rng.integers(0, dim, n_pixels) for dim in out.shape[:2]]
    vals = rng.choice([0, 255], size=n_pixels)
    out[coords[0], coords[1], :] = vals[:, None]
    return out


def low_res(img: np.ndarray, severity: str = "mild", seed: int = 0) -> np.ndarray:
    """Downscale then upscale (simulating low-resolution capture)."""
    img = to_uint8(img)
    h, w = img.shape[:2]
    scale = {"mild": 0.5, "moderate": 0.33, "severe": 0.25}[severity]
    small = cv2.resize(img, (max(1, int(w * scale)), max(1, int(h * scale))), interpolation=cv2.INTER_AREA)
    return cv2.resize(small, (w, h), interpolation=cv2.INTER_LINEAR)


def pose(img: np.ndarray, severity: str = "mild", seed: int = 0) -> np.ndarray:
    """Simulate out-of-plane pose via rotation + perspective warp."""
    img = to_uint8(img)
    h, w = img.shape[:2]
    angle = {"mild": 10, "moderate": 25, "severe": 45}[severity]
    rng = np.random.default_rng(seed)
    angle = float(rng.uniform(-angle, angle))
    M = cv2.getRotationMatrix2D((w / 2, h / 2), angle, 1.0)
    return cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)


def illum(img: np.ndarray, severity: str = "mild", seed: int = 0) -> np.ndarray:
    """Illumination change: brightness/contrast + gamma + vignette."""
    img = to_uint8(img).astype(np.float32)
    rng = np.random.default_rng(seed)
    alpha = 1.0 + rng.uniform(-{"mild": 0.3, "moderate": 0.6, "severe": 0.9}[severity], {"mild": 0.3, "moderate": 0.6, "severe": 0.9}[severity])
    beta = rng.uniform(-{"mild": 40, "moderate": 80, "severe": 120}[severity], {"mild": 40, "moderate": 80, "severe": 120}[severity])
    out = np.clip(img * alpha + beta, 0, 255).astype(np.uint8)
    # gamma
    gamma = {"mild": 0.9, "moderate": 0.7, "severe": 0.5}[severity]
    inv_gamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in range(256)]).astype(np.uint8)
    out = cv2.LUT(out, table)
    # vignette
    h, w = out.shape[:2]
    X, Y = np.meshgrid(np.linspace(-1, 1, w), np.linspace(-1, 1, h))
    mask = 1.0 - 0.4 * _factor(severity) * (X ** 2 + Y ** 2)
    mask = np.clip(mask, 0, 1)[:, :, None]
    out = np.clip(out.astype(np.float32) * mask, 0, 255).astype(np.uint8)
    return out


def occlusion(img: np.ndarray, severity: str = "mild", seed: int = 0) -> np.ndarray:
    """Random rectangular occlusion (e.g. mask/sunglasses/hair)."""
    img = to_uint8(img).copy()
    h, w = img.shape[:2]
    rng = np.random.default_rng(seed)
    frac = {"mild": 0.08, "moderate": 0.18, "severe": 0.30}[severity]
    oh, ow = int(h * frac), int(w * frac)
    y = int(rng.integers(0, max(1, h - oh)))
    x = int(rng.integers(0, max(1, w - ow)))
    color = rng.integers(0, 256, size=(3,)).astype(np.uint8).tolist()
    img[y : y + oh, x : x + ow] = color
    return img


def aging(img: np.ndarray, severity: str = "mild", seed: int = 0) -> np.ndarray:
    """Synthetic aging: blur + contrast reduction + noise + slight warp."""
    img = blur(img, severity=severity, seed=seed)
    img = noise(img, severity="mild", seed=seed + 1)
    img = to_uint8(img).astype(np.float32)
    img = np.clip(img * 0.85 + 10, 0, 255).astype(np.uint8)
    img = pose(img, severity="mild", seed=seed + 2)
    return img


DEGRADATIONS = {
    "blur": blur,
    "noise": noise,
    "low_res": low_res,
    "pose": pose,
    "illum": illum,
    "occlusion": occlusion,
    "aging": aging,
}


def degrade(img: np.ndarray, degradation: str, severity: str = "mild", seed: int = 0) -> np.ndarray:
    fn = DEGRADATIONS.get(degradation)
    if fn is None:
        raise ValueError(f"Unknown degradation: {degradation}")
    return fn(img, severity=severity, seed=seed)
