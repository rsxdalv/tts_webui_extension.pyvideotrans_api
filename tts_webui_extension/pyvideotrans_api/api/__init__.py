"""
API package for Pyvideotrans TTS stub.

This module exposes the callable handler for future routing integration.
"""

from .routes import tts_stub_handler, tts_api_handler

__all__ = ["tts_stub_handler", "tts_api_handler"]
