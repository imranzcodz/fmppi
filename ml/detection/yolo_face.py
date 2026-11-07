"""YoloFace detector strategy.

Wraps an Ultralytics YOLO model exported with YoloFace weights. Falls back to
OpenCV's Haar/ DNN face detector when ultralytics or the weights are not
available, keeping the pipeline runnable in minimal environments.
"""

from __future__ import annotations

import os
from typing import List, Optional

import cv2
import numpy as np

from .base import Detection, FaceDetector


class YoloFaceDetector(FaceDetector):
    def __init__(
        self,
        weights: Optional[str] = None,
        conf_threshold: float = 0.45,
        input_size: int = 640,
        device: str = "cpu",
    ) -> None:
        self.weights = weights
        self.conf_threshold = conf_threshold
        self.input_size = input_size
        self.device = device
        self._model = None
        self._fallback = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )
        self._load()

    def _load(self) -> None:
        try:  # pragma: no cover - optional heavy dependency
            from ultralytics import YOLO  # type: ignore

            if self.weights and os.path.exists(self.weights):
                self._model = YOLO(self.weights)
        except Exception:  # pragma: no cover - optional
            self._model = None

    def name(self) -> str:
        return "yolo_face"

    def detect(self, image: np.ndarray) -> List[Detection]:
        if self._model is not None:
            return self._detect_yolo(image)
        return self._detect_haar(image)

    def _detect_yolo(self, image: np.ndarray) -> List[Detection]:
        results = self._model.predict(
            image,
            imgsz=self.input_size,
            conf=self.conf_threshold,
            device=self.device,
            verbose=False,
        )
        detections: List[Detection] = []
        for r in results:
            if r.boxes is None:
                continue
            for box in r.boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                conf = float(box.conf[0]) if box.conf is not None else 1.0
                detections.append(
                    Detection(bbox=np.array([x1, y1, x2, y2], dtype=np.float32), confidence=conf)
                )
        return detections

    def _detect_haar(self, image: np.ndarray) -> List[Detection]:
        if self._fallback.empty():
            return []
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if image.ndim == 3 else image
        faces = self._fallback.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        detections: List[Detection] = []
        for x, y, w, h in faces:
            detections.append(
                Detection(
                    bbox=np.array([x, y, x + w, y + h], dtype=np.float32),
                    confidence=0.8,
                )
            )
        return detections
