"""Business logic for the TTS API stub.

This module validates inputs and returns a static URL when inputs look valid.
It does NOT perform synthesis yet; that will be wired in future steps.
"""
from __future__ import annotations

import re
from typing import Tuple

from .schemas import TTSForm, APIResponse, SUPPORTED_LANGUAGES, SUPPORTED_OS


_RATE_RE = re.compile(r"^(0|[+-]\d+%)$")


def validate_form(form: TTSForm) -> Tuple[bool, str]:
    """Validate incoming payload according to the spec.

    Returns (is_valid, error_message).
    """
    if not form.text or not form.text.strip():
        return False, "text is required"

    if not form.voice or not form.voice.strip():
        return False, "voice is required"

    if form.language not in SUPPORTED_LANGUAGES:
        return False, f"unsupported language: {form.language}"

    if form.ostype not in SUPPORTED_OS:
        return False, f"unsupported ostype: {form.ostype}"

    if not _RATE_RE.match(form.rate):
        return False, (
            "invalid rate format: expected '0' or '+number%' or '-number%'"
        )

    return True, ""


def make_success(url: str) -> APIResponse:
    return {"code": 0, "msg": "ok", "data": url}


def make_error(msg: str, code: int = 1) -> APIResponse:
    # code > 0 indicates failure; keep 1 as generic validation error for now.
    return {"code": code, "msg": msg, "data": ""}


def synthesize_stub(form: TTSForm) -> APIResponse:
    """Stub synthesis: returns a placeholder URL when validation passes."""
    ok, err = validate_form(form)
    if not ok:
        return make_error(err, code=1)

    # Placeholder URL; will be replaced by actual storage/serving path later.
    placeholder_url = "http://127.0.0.1:7772/outputs/stub.mp3"
    return make_success(placeholder_url)
