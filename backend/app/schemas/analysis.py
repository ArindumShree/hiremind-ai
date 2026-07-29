from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class SpeechMetrics(BaseModel):
    """Speech analysis results derived from a candidate audio answer."""

    model_config = ConfigDict(from_attributes=True)

    transcript: str = ""
    word_count: int = 0
    duration_seconds: float | None = None
    words_per_minute: float | None = None
    filler_word_count: int = 0
    filler_word_ratio: float = 0.0
    fluency_score: float = 0.0
    confidence_score: float = 0.0
    clarity_score: float | None = None


class VideoMetrics(BaseModel):
    """Video analysis results derived from a candidate video answer."""

    model_config = ConfigDict(from_attributes=True)

    frames_sampled: int = 0
    frames_with_face: int = 0
    face_detection_ratio: float = 0.0
    avg_face_confidence: float = 0.0
    eye_contact_score: float = 0.0
    posture_score: float = 0.0
    engagement_score: float = 0.0


class EvaluationDimension(BaseModel):
    """A single scored dimension in a candidate evaluation."""

    name: str
    score: float = Field(ge=0.0, le=100.0)
    weight: float = Field(ge=0.0, le=1.0)


class Evaluation(BaseModel):
    """Combined evaluation of a candidate across speech, video and answers."""

    model_config = ConfigDict(from_attributes=True)

    overall_score: float = Field(default=0.0, ge=0.0, le=100.0)
    dimensions: list[EvaluationDimension] = Field(default_factory=list)
    summary: str = ""
    ai_feedback: str | None = None
