from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class UserProfile(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    timezone: str = Field(default="local")
    daily_targets: dict[str, float] = Field(default_factory=dict)
    preferences: dict[str, str] = Field(default_factory=dict)


class MealItem(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    quantity: str = Field(min_length=1, max_length=100)
    calories: float = Field(ge=0)
    protein_g: float = Field(ge=0)
    carbs_g: float = Field(ge=0)
    fat_g: float = Field(ge=0)
    fiber_g: float | None = Field(default=None, ge=0)
    sodium_mg: float | None = Field(default=None, ge=0)
    source: Literal["manual", "estimate"] | None = None
    confidence: float | None = Field(default=None, ge=0, le=1)


class MealLogEntry(BaseModel):
    timestamp: datetime
    meal_type: Literal["breakfast", "lunch", "dinner", "snack"]
    items: list[MealItem] = Field(min_length=1)
    notes: str | None = None

    @field_validator("timestamp")
    def validate_timezone(value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("timestamp must include timezone offset")
        return value
