from __future__ import annotations

from typer.testing import CliRunner

from oc_nutrition.cli import app

runner = CliRunner()


def test_log_requires_confirm_to_append(tmp_path):
    result = runner.invoke(
        app,
        [
            "log",
            "--meal-type",
            "lunch",
            "--item",
            "chicken salad",
            "--qty",
            "1 bowl",
            "--calories",
            "450",
            "--protein",
            "35",
            "--carbs",
            "20",
            "--fat",
            "18",
            "--data-dir",
            str(tmp_path),
        ],
    )

    assert result.exit_code == 0
    assert "Not saved yet" in result.stdout
    assert not (tmp_path / "meal_log.ndjson").exists()


def test_log_with_confirm_appends(tmp_path):
    result = runner.invoke(
        app,
        [
            "log",
            "--meal-type",
            "dinner",
            "--item",
            "salmon",
            "--qty",
            "1 fillet",
            "--calories",
            "520",
            "--protein",
            "40",
            "--carbs",
            "5",
            "--fat",
            "35",
            "--confirm",
            "--data-dir",
            str(tmp_path),
        ],
    )

    assert result.exit_code == 0
    assert "Confirmed and appended entry" in result.stdout
    assert (tmp_path / "meal_log.ndjson").exists()


def test_log_image_requires_explicit_analyze(tmp_path, monkeypatch):
    image_path = tmp_path / "meal.jpg"
    image_path.write_bytes(b"fake")

    called = False

    def _fake_analyze(_image_path):
        nonlocal called
        called = True
        raise AssertionError("analysis should not be called without --analyze")

    monkeypatch.setattr("oc_nutrition.cli.analyze_food_image_online", _fake_analyze)

    result = runner.invoke(
        app,
        [
            "log-image",
            "--image",
            str(image_path),
            "--meal-type",
            "lunch",
            "--data-dir",
            str(tmp_path),
        ],
    )

    assert result.exit_code == 0
    assert "Analysis not started" in result.stdout
    assert called is False
