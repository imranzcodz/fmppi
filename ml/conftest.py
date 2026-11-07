import numpy as np
import pytest


@pytest.fixture
def golden_dataset():
    rng = np.random.RandomState(42)
    X = rng.randn(200, 8)
    y = (X[:, 0] * 2.0 + X[:, 1] > 0).astype(int)
    return X, y


@pytest.fixture
def golden_expected_accuracy():
    return 0.80
