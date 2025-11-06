"""Route-level handlers for the TTS API stub.

We keep it framework-agnostic for now: expose a plain Python function that
accepts form-like parameters and returns the JSON payload per spec.
Later, this can be bound to a FastAPI/Flask/Gradio endpoint.
"""
from __future__ import annotations

from typing import Optional

from .schemas import TTSForm, APIResponse
from .service import synthesize_stub
from .integration import synthesize_to_mp3


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


def tts_api_handler(
    text: str,
    language: str,
    voice: str,
    rate: str,
    ostype: str,
    extra: Optional[str] = None,
) -> APIResponse:
    """Attempt real synthesis via shared TTS service; fallback to stub on failure.

    This matches the same form contract as tts_stub_handler, but will try to
    call into tts_webui_extension.openai_tts_api if present to generate an MP3
    file under outputs/ and return its URL. If the service or model is not
    available, returns a validation-style error (code>0).
    """
    form = TTSForm(
        text=text,
        language=language,
        voice=voice,
        rate=rate,
        ostype=ostype,
        extra=extra,
    )

    # Validate using existing rules first
    from .service import validate_form, make_error, make_success  # local import to avoid cycles

    ok, err = validate_form(form)
    if not ok:
        return make_error(err, code=1)

    try:
        _, url = synthesize_to_mp3(
            text=form.text,
            language=form.language,
            voice=form.voice,
            rate=form.rate,
            ostype=form.ostype,
            extra=form.extra,
        )
        return make_success(url)
    except ImportError:
        return make_error("TTS service not available; extension not installed", code=2)
    except ValueError as e:
        return make_error(str(e), code=3)
    except Exception as e:
        return make_error(f"unexpected error: {e}", code=4)
