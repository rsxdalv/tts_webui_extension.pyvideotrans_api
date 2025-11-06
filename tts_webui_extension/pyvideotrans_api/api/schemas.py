from dataclasses import dataclass
from typing import Optional, TypedDict


# Supported languages per spec
SUPPORTED_LANGUAGES = {
    "zh-cn",
    "zh-tw",
    "en",
    "ja",
    "ko",
    "ru",
    "de",
    "fr",
    "tr",
    "th",
    "vi",
    "ar",
    "hi",
    "hu",
    "es",
    "pt",
    "it",
}

SUPPORTED_OS = {"win32", "mac", "linux"}


@dataclass
class TTSForm:
    """Incoming form payload for TTS synthesis (application/x-www-form-urlencoded)."""

    text: str
    language: str
    voice: str
    rate: str  # "0" or "+10%" or "-5%"
    ostype: str  # "win32" | "mac" | "linux"
    extra: Optional[str] = None


class APIResponse(TypedDict):
    """Standard JSON response as per spec.

    code: 0 on success, >0 on error
    msg: "ok" on success, otherwise error reason
    data: URL string when success, empty string when failure
    """

    code: int
    msg: str
    data: str
