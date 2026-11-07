"""Additional tests for config.py edge cases."""

import os
from dataclasses import dataclass

from ml.config import _coerce, _resolve, Settings


def test_resolve_none():
    assert _resolve(None) is None


def test_resolve_absolute():
    assert _resolve("/abs/path") == "/abs/path"


def test_resolve_relative():
    result = _resolve("data/raw/lfw")
    assert result.endswith(os.path.join("data", "raw", "lfw"))


@dataclass
class _FloatTest:
    lr: float = 0.001


def test_coerce_float_conversion():
    merged = {"lr": "1e-3"}
    out = _coerce(_FloatTest, merged)
    assert out["lr"] == 0.001


@dataclass
class _IntTest:
    epochs: int = 40


def test_coerce_int_conversion():
    merged = {"epochs": "100"}
    out = _coerce(_IntTest, merged)
    assert out["epochs"] == 100


@dataclass
class _BoolTest:
    aug: bool = True


def test_coerce_bool_conversion():
    merged = {"aug": "false"}
    out = _coerce(_BoolTest, merged)
    assert out["aug"] is False

    merged2 = {"aug": "true"}
    out2 = _coerce(_BoolTest, merged2)
    assert out2["aug"] is True


def test_settings_defaults():
    s = Settings()
    assert s.project == "fmppi"
    assert s.seed == 42
    assert s.image.size == [112, 112]
    assert s.datasets.synthetic_fallback is True
