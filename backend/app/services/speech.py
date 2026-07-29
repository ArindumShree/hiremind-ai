from __future__ import annotations

import os
import re

from app.core.errors import BadRequestError
from app.schemas.analysis import SpeechMetrics

_FILLER_WORDS = frozenset(
    {
        "um",
        "uh",
        "er",
        "ah",
        "like",
        "you know",
        "sort of",
        "kind of",
        "basically",
        "actually",
        "literally",
        "so",
        "well",
        "hmm",
    }
)


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z']+", text.lower())


def compute_metrics(
    transcript: str, duration_seconds: float | None = None
) -> SpeechMetrics:
    """Compute speech metrics from a transcript (pure, testable)."""
    words = _tokenize(transcript)
    word_count = len(words)

    if word_count == 0:
        return SpeechMetrics(
            transcript=transcript,
            word_count=0,
            duration_seconds=duration_seconds,
        )

    filler_count = sum(1 for word in words if word in _FILLER_WORDS)
    # Count multi-word fillers on the raw lowered text.
    lowered = transcript.lower()
    for phrase in ("you know", "sort of", "kind of"):
        filler_count += lowered.count(phrase)

    filler_ratio = round(filler_count / word_count, 4) if word_count else 0.0

    wpm: float | None = None
    if duration_seconds and duration_seconds > 0:
        wpm = round(word_count / (duration_seconds / 60.0), 2)

    # Fluency: ideal pace ~130 wpm; penalize fillers.
    if wpm is not None:
        pace_score = max(0.0, 1.0 - abs(wpm - 130.0) / 130.0)
    else:
        pace_score = 1.0 if word_count else 0.0
    fluency = round(max(0.0, (pace_score * 0.7) + (1.0 - filler_ratio) * 0.3), 4)

    # Confidence proxy: fewer fillers + reasonable length => higher confidence.
    length_factor = min(1.0, word_count / 80.0)
    confidence = round(
        max(0.0, (1.0 - filler_ratio) * 0.6 + length_factor * 0.4), 4
    )

    return SpeechMetrics(
        transcript=transcript,
        word_count=word_count,
        duration_seconds=duration_seconds,
        words_per_minute=wpm,
        filler_word_count=filler_count,
        filler_word_ratio=filler_ratio,
        fluency_score=fluency,
        confidence_score=confidence,
        clarity_score=None,
    )


class SpeechAnalysisService:
    """Transcribe candidate audio (Whisper) and compute speech metrics.

    Whisper is imported lazily inside :meth:`transcribe` so that importing this
    module (and the app) never triggers the heavy dependency or model download.
    """

    def __init__(self, model_name: str = "base") -> None:
        self._model_name = model_name

    def transcribe(self, audio_path: str) -> str:
        """Transcribe an audio file to text using OpenAI Whisper."""
        if not os.path.exists(audio_path):
            raise BadRequestError("Audio file not found")

        import whisper  # noqa: PLC0415  (lazy import — heavy dependency)

        model = whisper.load_model(self._model_name)
        result = model.transcribe(audio_path)
        return str(result.get("text", "")).strip()

    def analyze(
        self, audio_path: str, duration_seconds: float | None = None
    ) -> SpeechMetrics:
        """Transcribe the audio then compute derived speech metrics."""
        transcript = self.transcribe(audio_path)
        return compute_metrics(transcript, duration_seconds)
