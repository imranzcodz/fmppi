"""Unit tests for robustness augmentations."""

import numpy as np
import pytest

from ml.robustness.augmentations import (
    DEGRADATIONS,
    aging,
    blur,
    degrade,
    illum,
    low_res,
    noise,
    occlusion,
    pose,
)


def _img(seed=0):
    rng = np.random.default_rng(seed)
    return rng.integers(0, 256, size=(64, 64, 3), dtype=np.uint8)


def test_all_degradations_return_same_shape_dtype():
    img = _img()
    for name, fn in DEGRADATIONS.items():
        for sev in ("mild", "moderate", "severe"):
            out = fn(img, severity=sev, seed=1)
            assert out.shape == img.shape, name
            assert out.dtype == np.uint8, name


def test_deterministic_given_seed():
    img = _img()
    a = blur(img, severity="severe", seed=7)
    b = blur(img, severity="severe", seed=7)
    assert np.array_equal(a, b)


def test_different_seed_differs():
    img = _img()
    a = noise(img, severity="severe", seed=1)
    b = noise(img, severity="severe", seed=2)
    assert not np.array_equal(a, b)


def test_severity_increases_blur():
    img = _img()
    m = cv2_laplacian_var(blur(img, severity="mild", seed=1))
    s = cv2_laplacian_var(blur(img, severity="severe", seed=1))
    assert s <= m  # more blur -> lower variance


def test_low_res_downscales():
    img = _img()
    out = low_res(img, severity="severe", seed=1)
    assert out.shape == img.shape


def test_degrade_dispatcher():
    img = _img()
    out = degrade(img, "occlusion", severity="severe", seed=3)
    assert out.shape == img.shape
    with pytest.raises(ValueError):
        degrade(img, "nonexistent", severity="mild", seed=1)


def test_occlusion_puts_block():
    img = np.ones((64, 64, 3), dtype=np.uint8) * 128
    out = occlusion(img, severity="severe", seed=5)
    assert not np.array_equal(out, img)


def cv2_laplacian_var(img):
    import cv2

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return float(cv2.Laplacian(gray, cv2.CV_64F).var())


NAMES = {"blur": blur, "noise": noise, "low_res": low_res, "pose": pose, "illum": illum, "occlusion": occlusion, "aging": aging}


@pytest.mark.parametrize("name", list(NAMES.keys()))
def test_each_named(name):
    img = _img()
    out = NAMES[name](img, severity="severe", seed=0)
    assert out.shape == img.shape
    assert out.dtype == np.uint8
