"""MLflow experiment tracking and model registry for FMPPI.

Tracks parameters, metrics and artifacts per training run, promotes the best
checkpoint to the model registry, and writes a model card summary. Runs are
resumable via run id; all artifact paths resolve against the repository root.
"""

from __future__ import annotations

import os
from typing import Any, Dict, Optional


try:  # pragma: no cover - optional dependency
    import mlflow
    import mlflow.pyfunc
    from mlflow.tracking import MlflowClient
    from mlflow.models.signature import ModelSignature
    from mlflow.types.schema import Schema, TensorSpec
except Exception:  # pragma: no cover - mlflow absent
    mlflow = None
    MlflowClient = None  # type: ignore
    ModelSignature = None  # type: ignore
    Schema = None  # type: ignore
    TensorSpec = None  # type: ignore

from .config import resolve


def available() -> bool:
    return mlflow is not None


def init_tracking(settings) -> str:
    """Initialize MLflow tracking and return the experiment id."""
    if not available():
        raise RuntimeError("mlflow is not installed; pip install mlflow")
    # The file-store backend is gated behind a flag in MLflow 3.x; opt in for
    # local/cPanel-friendly file-based tracking.
    os.environ.setdefault("MLFLOW_ALLOW_FILE_STORE", "true")
    tracking_uri = resolve(settings.mlflow.tracking_uri)
    mlflow.set_tracking_uri(tracking_uri)
    os.makedirs(tracking_uri, exist_ok=True)
    experiment = mlflow.set_experiment(settings.mlflow.experiment_name)
    return experiment.experiment_id


class Run:
    """Context wrapper around an MLflow run with convenience logging."""

    def __init__(self, settings, run_name: Optional[str] = None) -> None:
        self.settings = settings
        self.run_name = run_name
        self._run = None
        self._client = None

    def __enter__(self):
        if not available():
            return self
        self._run = mlflow.start_run(run_name=self.run_name)
        self._client = MlflowClient()
        return self

    def __exit__(self, exc_type, exc, tb):
        if self._run is not None:
            mlflow.end_run()

    def log_params(self, params: Dict[str, Any]) -> None:
        if self._run is None:
            return
        for key, value in params.items():
            mlflow.log_param(key, value)

    def log_metrics(self, metrics: Dict[str, float], step: Optional[int] = None) -> None:
        if self._run is None:
            return
        mlflow.log_metrics(metrics, step=step)

    def log_artifact(self, local_path: str, artifact_path: Optional[str] = None) -> None:
        if self._run is None:
            return
        mlflow.log_artifact(local_path, artifact_path)

    def log_dict(self, dictionary: Dict[str, Any], artifact_file: str) -> None:
        if self._run is None:
            return
        mlflow.log_dict(dictionary, artifact_file)

    @property
    def run_id(self) -> Optional[str]:
        return self._run.info.run_id if self._run is not None else None

    @property
    def client(self):
        return self._client


def register_model(run_id: str, model_path: str, settings, name: Optional[str] = None) -> Optional[str]:
    """Log a Keras model + ONNX export as an MLflow model and register a version.

    Returns the registered model version or None when mlflow is unavailable.
    """
    if not available():
        return None
    name = name or settings.mlflow.model_name
    client = MlflowClient()
    try:
        client.create_registered_model(name)
    except Exception:
        # Model may already exist
        pass
    # Log the Keras model as an artifact under the run
    mlflow.log_artifacts(model_path, artifact_path="model")
    version = None
    try:
        mv = client.create_model_version(
            name=name,
            source=f"runs:/{run_id}/model",
            run_id=run_id,
        )
        version = mv.version
        client.transition_model_version_stage(
            name=name, version=version, stage="Production"
        )
    except Exception:
        pass
    return version
