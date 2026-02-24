from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from oc_nutrition.models import MealLogEntry, UserProfile

DEFAULT_DATA_DIR = Path("data")
PROFILE_FILENAME = "profile.json"
LOG_FILENAME = "meal_log.ndjson"


class StorageError(RuntimeError):
    """Raised when a local data operation fails."""


def resolve_data_dir(data_dir: Path | None = None) -> Path:
    if data_dir is not None:
        return data_dir
    env_dir = os.getenv("OC_NUTRITION_DATA_DIR")
    return Path(env_dir) if env_dir else DEFAULT_DATA_DIR


def ensure_data_layout(data_dir: Path) -> None:
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "exports").mkdir(parents=True, exist_ok=True)


def profile_path(data_dir: Path) -> Path:
    return data_dir / PROFILE_FILENAME


def log_path(data_dir: Path) -> Path:
    return data_dir / LOG_FILENAME


def init_profile_from_example(data_dir: Path, example_path: Path) -> Path:
    ensure_data_layout(data_dir)
    destination = profile_path(data_dir)
    if destination.exists():
        raise StorageError(f"Profile already exists at {destination}; refusing to overwrite.")

    try:
        payload: dict[str, Any] = json.loads(example_path.read_text(encoding="utf-8"))
        profile = UserProfile.model_validate(payload)
    except FileNotFoundError as exc:
        raise StorageError(f"Example profile file not found: {example_path}") from exc
    except json.JSONDecodeError as exc:
        raise StorageError(f"Example profile is not valid JSON: {exc}") from exc
    except ValidationError as exc:
        raise StorageError(f"Example profile failed validation: {exc}") from exc

    destination.write_text(profile.model_dump_json(indent=2), encoding="utf-8")
    return destination


def append_log_entry(entry: MealLogEntry, data_dir: Path) -> Path:
    ensure_data_layout(data_dir)
    destination = log_path(data_dir)
    with destination.open("a", encoding="utf-8") as handle:
        handle.write(entry.model_dump_json())
        handle.write("\n")
    return destination


def read_log_entries(data_dir: Path) -> list[MealLogEntry]:
    source = log_path(data_dir)
    if not source.exists():
        return []

    entries: list[MealLogEntry] = []
    with source.open("r", encoding="utf-8") as handle:
        for idx, raw_line in enumerate(handle, start=1):
            line = raw_line.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
                entries.append(MealLogEntry.model_validate(payload))
            except json.JSONDecodeError as exc:
                raise StorageError(f"Invalid JSON in {source} line {idx}: {exc}") from exc
            except ValidationError as exc:
                raise StorageError(f"Invalid meal log entry in {source} line {idx}: {exc}") from exc

    return entries
