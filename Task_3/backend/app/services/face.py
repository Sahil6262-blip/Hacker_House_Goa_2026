import hashlib
from dataclasses import dataclass
from typing import Protocol

import cv2
import numpy as np


@dataclass
class FaceEncoding:
    image_sha256: str
    face_count: int
    primary_box: list[int] | None
    descriptor: np.ndarray | None


class FaceProvider(Protocol):
    name: str

    def analyze(self, image_bytes: bytes) -> FaceEncoding: ...


class OpenCVFaceProvider:
    """Local Haar detector plus a normalized prototype face descriptor.

    This is intentionally labelled as similarity support, never identity proof.
    Replace it with a reviewed biometric provider before any production use.
    """

    name = "opencv_haar_prototype"

    def __init__(self) -> None:
        cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"  # type: ignore[attr-defined]
        self.detector = cv2.CascadeClassifier(cascade_path)

    def analyze(self, image_bytes: bytes) -> FaceEncoding:
        digest = hashlib.sha256(image_bytes).hexdigest()
        image = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
        if image is None:
            raise ValueError("The uploaded file is not a readable image.")
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        boxes = self.detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(40, 40))
        if len(boxes) == 0:
            return FaceEncoding(digest, 0, None, None)
        x, y, width, height = max(boxes, key=lambda box: int(box[2]) * int(box[3]))
        crop = gray[y : y + height, x : x + width]
        descriptor = cv2.resize(crop, (16, 8), interpolation=cv2.INTER_AREA).astype(np.float32).flatten()
        descriptor -= descriptor.mean()
        norm = float(np.linalg.norm(descriptor))
        if norm:
            descriptor /= norm
        return FaceEncoding(digest, len(boxes), [int(x), int(y), int(width), int(height)], descriptor)

    @staticmethod
    def similarity(left: np.ndarray | None, right: np.ndarray | None) -> float | None:
        if left is None or right is None:
            return None
        return round(float(np.clip(np.dot(left, right), -1, 1)), 4)
