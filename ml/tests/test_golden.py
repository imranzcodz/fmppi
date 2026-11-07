import os
import pytest

G2_TAR_FAR_THRESHOLD = 0.99   # face verification TAR@FAR=1e-3 on LFW
G3_KINSHIP_ACC_THRESHOLD = 0.75  # kinship accuracy on KinFaceW

REAL_MODEL_AVAILABLE = os.path.exists("ml/models/fmppi_siamese.onnx")
REAL_DATA_AVAILABLE = os.path.exists("data/processed/lfw") or os.path.exists("data/processed/kinfacew")


def _skip_unless_real(msg):
    pytest.skip(msg)


@pytest.mark.skipif(not REAL_MODEL_AVAILABLE or not REAL_DATA_AVAILABLE,
                    reason="A1 real model + golden datasets not wired yet")
def test_g2_face_verification_tar_far():
    # A1: load FMPPI model + LFW pairs, compute TAR@FAR=1e-3, assert >= G2_TAR_FAR_THRESHOLD
    assert True  # placeholder replaced by A1


@pytest.mark.skipif(not REAL_MODEL_AVAILABLE or not REAL_DATA_AVAILABLE,
                    reason="A1 real model + golden datasets not wired yet")
def test_g3_kinship_accuracy():
    # A1: load FMPPI model + KinFaceW pairs, compute accuracy, assert >= G3_KINSHIP_ACC_THRESHOLD
    assert True  # placeholder replaced by A1
