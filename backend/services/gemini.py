import os
import logging
from google import genai
from fastapi import HTTPException

logger = logging.getLogger(__name__)
GEMINI_MODEL = "gemini-3.6-flash"

def ask_gemini(prompt: str) -> str:
    key = os.getenv("GEMINI_API_KEY")
    if not key: raise HTTPException(503, "Gemini is not configured. Add GEMINI_API_KEY to the server environment.")
    try:
        client = genai.Client(api_key=key)
        response = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
        if not response.text:
            raise ValueError("Gemini returned an empty response.")
        return response.text
    except Exception as exc:
        # Keep the local frontend useful while never returning the API key itself.
        safe_error = str(exc).replace(key, "[redacted]")
        logger.exception("Gemini request failed")
        raise HTTPException(502, f"Gemini request failed ({type(exc).__name__}): {safe_error}") from exc
