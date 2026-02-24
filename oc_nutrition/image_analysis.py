from __future__ import annotations

import base64
import json
import mimetypes
import os
from dataclasses import dataclass
from pathlib import Path
from urllib import error, request


class ImageAnalysisError(RuntimeError):
    """Raised when food image analysis fails."""


@dataclass
class ImageNutritionEstimate:
    food_name: str
    quantity: str
    calories: float
    protein_g: float
    carbs_g: float
    fat_g: float
    confidence: float
    reasoning: str


def _as_data_uri(image_path: Path) -> str:
    if not image_path.exists() or not image_path.is_file():
        raise ImageAnalysisError(f"Image not found: {image_path}")

    mime_type = mimetypes.guess_type(image_path.name)[0] or "image/jpeg"
    encoded = base64.b64encode(image_path.read_bytes()).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


def _extract_json(raw_text: str) -> dict[str, object]:
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        cleaned = cleaned.replace("json", "", 1).strip()
    try:
        payload = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise ImageAnalysisError(f"Model response is not valid JSON: {raw_text}") from exc
    if not isinstance(payload, dict):
        raise ImageAnalysisError("Model response JSON must be an object")
    return payload


def analyze_food_image_online(image_path: Path) -> ImageNutritionEstimate:
    """Analyze a food photo with an online vision model and return estimated macros."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ImageAnalysisError("OPENAI_API_KEY is required for online image analysis")

    model = os.getenv("OPENAI_VISION_MODEL", "gpt-4.1-mini")
    endpoint = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/") + "/chat/completions"

    data_uri = _as_data_uri(image_path)
    prompt = (
        "You are a nutrition analyst. Determine if this image is food. "
        "If it is food, estimate calories and macros for one best-guess serving. "
        "Return ONLY JSON with keys: is_food (bool), food_name (str), quantity (str), "
        "calories (number), protein_g (number), carbs_g (number), fat_g (number), "
        "confidence (0..1), reasoning (str)."
    )
    body = {
        "model": model,
        "temperature": 0.2,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": data_uri}},
                ],
            }
        ],
    }

    req = request.Request(
        endpoint,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with request.urlopen(req, timeout=60) as resp:
            raw = resp.read().decode("utf-8")
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")
        raise ImageAnalysisError(f"Vision API request failed ({exc.code}): {detail}") from exc
    except error.URLError as exc:
        raise ImageAnalysisError(f"Vision API network error: {exc}") from exc

    try:
        response_payload = json.loads(raw)
        content = response_payload["choices"][0]["message"]["content"]
    except (json.JSONDecodeError, KeyError, IndexError, TypeError) as exc:
        raise ImageAnalysisError(f"Unexpected vision API response: {raw}") from exc

    parsed = _extract_json(content)
    if not parsed.get("is_food", False):
        raise ImageAnalysisError("The uploaded image does not appear to be food")

    try:
        return ImageNutritionEstimate(
            food_name=str(parsed["food_name"]),
            quantity=str(parsed["quantity"]),
            calories=float(parsed["calories"]),
            protein_g=float(parsed["protein_g"]),
            carbs_g=float(parsed["carbs_g"]),
            fat_g=float(parsed["fat_g"]),
            confidence=float(parsed["confidence"]),
            reasoning=str(parsed.get("reasoning", "")),
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise ImageAnalysisError(f"Missing/invalid macro fields in model response: {parsed}") from exc

