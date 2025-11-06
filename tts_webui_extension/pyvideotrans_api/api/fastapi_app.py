"""FastAPI app exposing the Pyvideotrans TTS API.

Endpoint: POST /api/pyvideotrans/tts
Accepts application/x-www-form-urlencoded fields per spec and returns JSON.
Also serves generated files from /outputs.
"""
from __future__ import annotations

from fastapi import FastAPI, Form, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from .schemas import TTSForm
from .service import validate_form, make_error, make_success
from .integration import synthesize_to_mp3, OUTPUTS_DIR

app = FastAPI(title="Pyvideotrans TTS API", version="0.0.1")

# Serve generated audio files
app.mount("/outputs", StaticFiles(directory=OUTPUTS_DIR), name="outputs")


@app.post("/api/pyvideotrans/tts")
async def tts_endpoint(
    request: Request,
    text: str = Form(...),
    language: str = Form(...),
    voice: str = Form(...),
    rate: str = Form(...),
    ostype: str = Form(...),
    extra: str | None = Form(None),
):
    form = TTSForm(
        text=text,
        language=language,
        voice=voice,
        rate=rate,
        ostype=ostype,
        extra=extra,
    )

    ok, err = validate_form(form)
    if not ok:
        return JSONResponse(make_error(err, code=1))

    # Use the FastAPI base URL so returned links point to this server
    base_url = str(request.base_url).rstrip("/")

    try:
        _, public_url = synthesize_to_mp3(
            text=form.text,
            language=form.language,
            voice=form.voice,
            rate=form.rate,
            ostype=form.ostype,
            extra=form.extra,
            base_url=base_url,
        )
        return JSONResponse(make_success(public_url))
    except ImportError:
        return JSONResponse(make_error("TTS service not available; extension not installed", code=2))
    except ValueError as e:
        return JSONResponse(make_error(str(e), code=3))
    except Exception as e:
        return JSONResponse(make_error(f"unexpected error: {e}", code=4))
