from __future__ import annotations

import os

from app.core.errors import BadRequestError
from app.schemas.analysis import VideoMetrics


def compute_metrics(
    frames_sampled: int,
    frames_with_face: int,
    face_confidences: list[float],
) -> VideoMetrics:
    """Compute video metrics from sampled-frame observations (pure, testable)."""
    if frames_sampled <= 0:
        return VideoMetrics()

    coverage = round(frames_with_face / frames_sampled, 4)
    avg_conf = (
        round(sum(face_confidences) / len(face_confidences), 4)
        if face_confidences
        else 0.0
    )

    # Simple deterministic proxies from coverage + detection confidence.
    eye_contact = round(coverage * avg_conf, 4)
    posture = round(coverage, 4)
    engagement = round((coverage * 0.5) + (avg_conf * 0.5), 4)

    return VideoMetrics(
        frames_sampled=frames_sampled,
        frames_with_face=frames_with_face,
        face_detection_ratio=coverage,
        avg_face_confidence=avg_conf,
        eye_contact_score=eye_contact,
        posture_score=posture,
        engagement_score=engagement,
    )


class VideoAnalysisService:
    """Analyze candidate video answers with OpenCV + MediaPipe FaceMesh.

    Both ``cv2`` and ``mediapipe`` are imported lazily inside :meth:`analyze`
    to keep module import (and the app) free of the heavy dependencies.
    """

    def __init__(self, max_frames: int = 20) -> None:
        self._max_frames = max_frames

    def analyze(self, video_path: str) -> VideoMetrics:
        """Sample frames and run FaceMesh to compute simple engagement proxies."""
        if not os.path.exists(video_path):
            raise BadRequestError("Video file not found")

        import cv2  # noqa: PLC0415  (lazy import — heavy dependency)
        import mediapipe as mp  # noqa: PLC0415  (lazy import — heavy dependency)

        capture = cv2.VideoCapture(video_path)
        try:
            total = int(capture.get(cv2.CAP_PROP_FRAME_COUNT)) or 0
            step = max(1, total // self._max_frames) if total else 1

            face_mesh = mp.solutions.face_mesh.FaceMesh(
                static_image_mode=True,
                max_num_faces=1,
                refine_landmarks=True,
            )
            frames_sampled = 0
            frames_with_face = 0
            confidences: list[float] = []
            index = 0
            try:
                while True:
                    ok, frame = capture.read()
                    if not ok:
                        break
                    if index % step == 0:
                        frames_sampled += 1
                        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        result = face_mesh.process(rgb)
                        if result.multi_face_landmarks:
                            frames_with_face += 1
                            confidences.append(1.0)
                        if frames_sampled >= self._max_frames:
                            break
                    index += 1
            finally:
                face_mesh.close()
        finally:
            capture.release()

        return compute_metrics(frames_sampled, frames_with_face, confidences)
