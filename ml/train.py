import numpy as np


def train_model(X, y, epochs=5, seed=42):
    rng = np.random.RandomState(seed)
    weights = rng.randn(X.shape[1]) * 0.1
    bias = 0.0
    lr = 0.1
    for _ in range(epochs):
        scores = X @ weights + bias
        preds = (scores > 0).astype(int)
        grad = X.T @ (preds - y) / len(y)
        weights -= lr * grad
        bias -= lr * (preds - y).mean()
    return {"weights": weights, "bias": bias}


def predict(model, X):
    scores = X @ model["weights"] + model["bias"]
    return (scores > 0).astype(int)
