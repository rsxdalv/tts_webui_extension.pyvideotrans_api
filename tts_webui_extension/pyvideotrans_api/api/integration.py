"""Integration with the shared TTS service (openai_tts_api).

This module attempts to use the existing adapters to synthesize audio, then
converts to MP3, writes it to the outputs/ folder, and returns the file URL.
If the service or model isn't available, it can raise ImportError or ValueError,
which callers should handle (e.g., by returning a stub response).
"""
from __future__ import annotations

import json
import os
import time
import uuid
from typing import Dict, Tuple, Any

# For type checkers, declare symbols; at runtime we import dynamically.
generic_tts_adapter: Any = None
webui_to_wav: Any = None
convert_audio_format: Any = None
ResponseFormatEnum: Any = None

try:  # pragma: no cover - environment dependent
    import importlib

    tts_service_mod = importlib.import_module(
        "tts_webui_extension.openai_tts_api.services.tts_service"
    )
    models_mod = importlib.import_module(
        "tts_webui_extension.openai_tts_api.models"
    )

    generic_tts_adapter = getattr(tts_service_mod, "generic_tts_adapter", None)
    webui_to_wav = getattr(tts_service_mod, "webui_to_wav", None)
    convert_audio_format = getattr(tts_service_mod, "convert_audio_format", None)
    ResponseFormatEnum = getattr(models_mod, "ResponseFormatEnum", None)
except Exception:
    # Keep symbols as None; callers will handle ImportError path.
    pass


DEFAULT_BASE_URL = os.environ.get("PYVIDEOTRANS_API_BASE_URL", "http://127.0.0.1:7772")
OUTPUTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "outputs"))
# Ensure outputs directory exists
os.makedirs(OUTPUTS_DIR, exist_ok=True)


def parse_rate_to_speed(rate: str) -> float:
    """Convert rate spec ('0', '+10%', '-20%') to a multiplier (1.0 = normal)."""
    rate = (rate or "0").strip()
    if rate == "0":
        return 1.0
    sign = 1
    if rate.startswith("+"):
        sign = 1
        rate = rate[1:]
    elif rate.startswith("-"):
        sign = -1
        rate = rate[1:]
    if rate.endswith("%"):
        rate = rate[:-1]
    try:
        pct = float(rate)
    except ValueError:
        return 1.0
    return max(0.25, 1.0 + sign * (pct / 100.0))


def parse_extra(extra: str | None) -> Dict:
    """Best-effort parse of the 'extra' string as JSON; return dict or {}."""
    if not extra:
        return {}
    try:
        return json.loads(extra)
    except Exception:
        return {}


def pick_model(language: str, extra_params: Dict) -> Tuple[str, Dict]:
    """Choose a model and base params.

    Priority:
    - If extra_params contains "model", use it.
    - Otherwise default to a lightweight model name expected in the WebUI.
    """
    if "model" in extra_params and extra_params["model"]:
        model = str(extra_params["model"]).strip()
        params = dict(extra_params)
        params.pop("model", None)
        return model, params

    # Default fallback; fairly available in many envs is 'piper-tts' if installed.
    # If not available, the caller should catch ImportError/ValueError and fallback.
    return "piper-tts", {}


def synthesize_to_mp3(
    *,
    text: str,
    language: str,
    voice: str,
    rate: str,
    ostype: str,
    extra: str | None,
    base_url: str | None = None,
) -> Tuple[str, str]:
    """Run synthesis via generic_tts_adapter and materialize an MP3 file.

    Returns (file_path, public_url).
    Raises ImportError or ValueError if adapters/models are unavailable.
    """
    if generic_tts_adapter is None or webui_to_wav is None or convert_audio_format is None or ResponseFormatEnum is None:
        raise ImportError("openai_tts_api service not available")

    extra_params = parse_extra(extra)
    model, params = pick_model(language, extra_params)

    # Map our fields to adapter params
    speed = parse_rate_to_speed(rate)

    # Some adapters expect different key names; we pass a general set and let adapters ignore unknowns.
    params = {
        "voice": voice,
        "voice_name": voice,
        "language": language,
        "speed": speed,
        **params,
    }

    # Generate audio using WebUI adapter
    result = generic_tts_adapter(text, params, model)

    # Convert to WAV and then MP3 bytes
    wav_bytes = webui_to_wav(result)
    mp3_bytes = convert_audio_format(wav_bytes, ResponseFormatEnum.MP3)

    # Persist to outputs
    filename = f"pyvideo_{int(time.time())}_{uuid.uuid4().hex[:8]}.mp3"
    abs_path = os.path.join(OUTPUTS_DIR, filename)
    with open(abs_path, "wb") as f:
        f.write(mp3_bytes)

    # Build URL
    base = base_url or DEFAULT_BASE_URL
    public_url = f"{base}/outputs/{filename}"
    return abs_path, public_url
