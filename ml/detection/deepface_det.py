"""DeepFace detector strategy.

Wraps DeepFace's built-in face detectors (opencv, ssd, dlib, mtcnn, retinaface,
mediapipe). Falls back to OpenCV Haar when DeepFace is unavailable.
"""

from __future__ import annotations

from typing import List

import cv2
import numpy as np

from .base import Detection, FaceDetector


class DeepFaceDetector(FaceDetector):
    def __init__(
        self,
        detector_backend: str = "opencv",
        conf_threshold: float = 0.45,
    ) -> None:
        self.detector_backend = detector_backend
        self.conf_threshold = conf_threshold
        self._deepface = None
        try:  # pragma: no cover - optional heavy dependency
            from deepface import DeepFace  # type: ignore

            self._deepface = DeepFace
        except Exception:  # pragma: no cover - optional
            self._deepface = None
        try:
            self._fallback = cv2.CascadeClassifier(
                cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
            )
        except AttributeError:  # opencv build without contrib/haar
            self._fallback = None

    def name(self) -> str:
        return f"deepface_{self.detector_backend}"

    def detect(self, image: np.ndarray) -> List[Detection]:
        if self._deepface is not None:
            return self._detect_deepface(image)
        return self._detect_haar(image)

    def _detect_deepface(self, image: np.ndarray) -> List[Detection]:
        try:
            faces = self._deepface.extract_faces(
                img_path=image,
                detector_backend=self.detector_backend,
                enforce_detection=False,
                align=True,
            )
        except Exception:
            return self._detect_haar(image)
        detections: List[Detection] = []
        for f in faces:
            area = f.get("facial_area", {})
            x = float(area.get("x", 0))
            y = float(area.get("y", 0))
            w = float(area.get("w", 0))
            h = float(area.get("h", 0))
            conf = float(f.get("confidence", 0.8))
            if conf < self.conf_threshold:
                continue
            detections.append(
                Detection(
                    bbox=np.array([x, y, x + w, y + h], dtype=np.float32),
                    confidence=conf,
                    landmarks=f.get("landmarks"),
                )
            )
        return detections

    def _detect_haar(self, image: np.ndarray) -> List[Detection]:
        if self._fallback is None or self._fallback.empty():
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


def build_detector(name: str = "yolo_face", **kwargs) -> FaceDetector:
    name = (name or "yolo_face").lower()
    if name == "yolo_face":
        from .yolo_face import YoloFaceDetector

        return YoloFaceDetector(**kwargs)
    if name.startswith("deepface"):
        from .deepface_det import DeepFaceDetector

        backend = kwargs.pop("detector_backend", "opencv")
        return DeepFaceDetector(detector_backend=backend, **kwargs)
    raise ValueError(f"Unknown detector: {name}")
