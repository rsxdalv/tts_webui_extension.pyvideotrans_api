# Pyvideotrans API Scaffold

This directory contains a minimal scaffold for a custom TTS API used by the TTS Generation WebUI extension.

## Contract (stubbed)

POST (application/x-www-form-urlencoded) fields:
- `text`: string (required)
- `language`: one of {zh-cn, zh-tw, en, ja, ko, ru, de, fr, tr, th, vi, ar, hi, hu, es, pt, it}
- `voice`: string (required)
- `rate`: `0` or `+number%` or `-number%`
- `ostype`: one of {win32, mac, linux}
- `extra`: string (optional)

JSON response:
```json
{ "code": 0, "msg": "ok", "data": "http://127.0.0.1:7772/outputs/stub.mp3" }
```
- `code`: 0 = success; >0 = failure
- `msg`: "ok" on success; otherwise error reason
- `data`: URL of the MP3 on success; empty string on failure

## Files

- `api/schemas.py`: data shapes (input form and response types)
- `api/service.py`: validation and stubbed synthesis logic
- `api/routes.py`: framework-agnostic handlers `tts_stub_handler` (placeholder) and `tts_api_handler` (uses shared TTS service when available)

## Next steps

- Bind `api.tts_api_handler` (preferred) or `api.tts_stub_handler` to a real HTTP endpoint (FastAPI/Flask/Gradio) that accepts `application/x-www-form-urlencoded`.
- Replace the placeholder URL with an actual served MP3 path after synthesis.
- Optionally add unit tests for validators and edge cases.
