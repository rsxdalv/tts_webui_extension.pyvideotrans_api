"""Route-level handlers for the TTS API stub.

We keep it framework-agnostic for now: expose a plain Python function that
accepts form-like parameters and returns the JSON payload per spec.
Later, this can be bound to a FastAPI/Flask/Gradio endpoint.
"""
from __future__ import annotations

from typing import Optional

from .schemas import TTSForm, APIResponse
from .service import synthesize_stub


def tts_stub_handler(
    text: str,
    language: str,
    voice: str,
    rate: str,
    ostype: str,
    extra: Optional[str] = None,
) -> APIResponse:
    """Framework-agnostic handler matching the expected form fields.

    Input types correspond to application/x-www-form-urlencoded fields.
    Returns a dict suitable for JSON serialization.
    """
    form = TTSForm(
        text=text,
        language=language,
        voice=voice,
        rate=rate,
        ostype=ostype,
        extra=extra,
    )
    return synthesize_stub(form)
