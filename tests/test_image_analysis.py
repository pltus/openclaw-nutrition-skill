from __future__ import annotations

import json
from pathlib import Path

import pytest

from oc_nutrition.image_analysis import ImageAnalysisError, analyze_food_image_online


class _FakeHTTPResponse:
    def __init__(self, body: dict):
        self._body = json.dumps(body).encode("utf-8")

    def read(self) -> bytes:
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


def test_analyze_food_image_success(monkeypatch, tmp_path: Path):
    image_path = tmp_path / "meal.jpg"
    image_path.write_bytes(b"fake-image")

    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    response_body = {
        "choices": [
            {
                "message": {
                    "content": json.dumps(
                        {
                            "is_food": True,
                            "food_name": "bibimbap",
                            "quantity": "1 bowl",
                            "calories": 650,
                            "protein_g": 25,
                            "carbs_g": 85,
                            "fat_g": 22,
                            "confidence": 0.72,
                            "reasoning": "Rice and mixed toppings",
                        }
                    )
                }
            }
        ]
    }

    def _fake_urlopen(req, timeout=60):  # noqa: ANN001
        assert req.full_url.endswith("/chat/completions")
        return _FakeHTTPResponse(response_body)

    monkeypatch.setattr("urllib.request.urlopen", _fake_urlopen)

    estimate = analyze_food_image_online(image_path)

    assert estimate.food_name == "bibimbap"
    assert estimate.calories == 650
    assert estimate.confidence == pytest.approx(0.72)


def test_analyze_food_image_non_food_raises(monkeypatch, tmp_path: Path):
    image_path = tmp_path / "desk.png"
    image_path.write_bytes(b"not-food")

    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    response_body = {
        "choices": [{"message": {"content": json.dumps({"is_food": False})}}]
    }

    monkeypatch.setattr(
        "urllib.request.urlopen",
        lambda req, timeout=60: _FakeHTTPResponse(response_body),  # noqa: ARG005
    )

    with pytest.raises(ImageAnalysisError, match="does not appear to be food"):
        analyze_food_image_online(image_path)
