"""Unit tests for ORL_Faces, CCTV, and combined dataset loaders."""

import os
import tempfile

from ml.datasets import load_all_datasets, load_cctv_detection, load_orl_faces


def _make_orl_faces(tmp: str):
    """Create a minimal ORL_Faces-like structure: 3 subjects x 3 images."""
    for subj in range(1, 4):
        sdir = os.path.join(tmp, f"s{subj}")
        os.makedirs(sdir, exist_ok=True)
        for i in range(1, 4):
            from PIL import Image
            img = Image.new("RGB", (112, 112), color=(subj * 50, i * 40, 128))
            img.save(os.path.join(sdir, f"{i}.pgm"))


def test_load_orl_faces_creates_pairs():
    with tempfile.TemporaryDirectory() as tmp:
        _make_orl_faces(tmp)
        pairs = load_orl_faces(tmp)
        assert len(pairs) > 0
        # All should be verification pairs
        for p in pairs:
            assert p.dataset == "orl_faces"
            assert p.pair_type == "verification"
            assert p.label in (0, 1)
            assert os.path.exists(p.path_a)
            assert os.path.exists(p.path_b)
        # Positive pairs exist (same subject)
        pos = [p for p in pairs if p.label == 1]
        neg = [p for p in pairs if p.label == 0]
        assert len(pos) > 0
        assert len(neg) > 0


def test_load_orl_faces_missing_root():
    assert load_orl_faces("data/does_not_exist/orl_faces") == []


def test_load_cctv_detection_creates_pairs():
    with tempfile.TemporaryDirectory() as tmp:
        img_dir = os.path.join(tmp, "train", "images")
        os.makedirs(img_dir, exist_ok=True)
        from PIL import Image
        for i in range(6):
            img = Image.new("RGB", (640, 480), color=(i * 40, 50, 100))
            img.save(os.path.join(img_dir, f"img_{i}.jpg"))
        pairs = load_cctv_detection(tmp)
        assert len(pairs) > 0
        for p in pairs:
            assert p.dataset == "cctv"
            assert p.pair_type == "verification"
            assert p.label in (0, 1)


def test_load_cctv_detection_missing_root():
    assert load_cctv_detection("data/does_not_exist/cctv") == []


def test_load_all_datasets_returns_list():
    # All roots missing -> empty list with synthetic_fallback False behavior
    import tempfile
    from ml.config import load_config

    settings = load_config("ml/config/default.yaml")
    with tempfile.TemporaryDirectory() as tmp:
        settings.datasets.lfw_root = tmp
        settings.datasets.kinfacew_root = tmp
        settings.datasets.orl_faces_root = tmp
        settings.datasets.cctv_root = tmp
        settings.datasets.synthetic_fallback = False
        pairs = load_all_datasets(settings)
    # Should be a list (possibly empty)
    assert isinstance(pairs, list)


def test_load_all_datasets_with_synthetic_fallback():
    import tempfile
    from ml.config import load_config

    settings = load_config("ml/config/default.yaml")
    with tempfile.TemporaryDirectory() as tmp:
        settings.datasets.lfw_root = tmp
        settings.datasets.kinfacew_root = tmp
        settings.datasets.orl_faces_root = tmp
        settings.datasets.cctv_root = tmp
        settings.datasets.synthetic_fallback = True
        pairs = load_all_datasets(settings)
    # With synthetic fallback, should still return a list
    assert isinstance(pairs, list)
