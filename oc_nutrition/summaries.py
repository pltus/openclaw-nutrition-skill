from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta

from oc_nutrition.models import MealLogEntry


@dataclass
class MacroTotals:
    calories: float = 0.0
    protein_g: float = 0.0
    carbs_g: float = 0.0
    fat_g: float = 0.0


@dataclass
class SummaryResult:
    start: datetime
    end: datetime
    totals: MacroTotals
    entries_count: int


def _local_tzinfo():
    return datetime.now().astimezone().tzinfo


def _local_now() -> datetime:
    return datetime.now().astimezone()


def _range_for_day(target_day: date) -> tuple[datetime, datetime]:
    tzinfo = _local_tzinfo()
    start = datetime.combine(target_day, time.min, tzinfo=tzinfo)
    end = datetime.combine(target_day, time.max, tzinfo=tzinfo)
    return start, end


def _sum_entries(entries: list[MealLogEntry], start: datetime, end: datetime) -> SummaryResult:
    totals = MacroTotals()
    count = 0
    for entry in entries:
        local_dt = entry.timestamp.astimezone(start.tzinfo)
        if not (start <= local_dt <= end):
            continue
        count += 1
        for item in entry.items:
            totals.calories += item.calories
            totals.protein_g += item.protein_g
            totals.carbs_g += item.carbs_g
            totals.fat_g += item.fat_g

    return SummaryResult(start=start, end=end, totals=totals, entries_count=count)


def today_summary(entries: list[MealLogEntry], now: datetime | None = None) -> SummaryResult:
    current = now or _local_now()
    start, end = _range_for_day(current.date())
    return _sum_entries(entries, start=start, end=end)


def last_7_days_summary(entries: list[MealLogEntry], now: datetime | None = None) -> SummaryResult:
    current = now or _local_now()
    tzinfo = current.tzinfo or _local_tzinfo()
    end = current.astimezone(tzinfo)
    start_day = (end - timedelta(days=6)).date()
    start = datetime.combine(start_day, time.min, tzinfo=tzinfo)
    return _sum_entries(entries, start=start, end=end)
