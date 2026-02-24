from datetime import datetime

from oc_nutrition.models import MealItem, MealLogEntry
from oc_nutrition.summaries import last_7_days_summary, today_summary


def _entry(day: int, calories: float, protein: float, carbs: float, fat: float) -> MealLogEntry:
    return MealLogEntry(
        timestamp=datetime(2026, 1, day, 12, 0, tzinfo=datetime.now().astimezone().tzinfo),
        meal_type="lunch",
        items=[
            MealItem(
                name="meal",
                quantity="1 serving",
                calories=calories,
                protein_g=protein,
                carbs_g=carbs,
                fat_g=fat,
            )
        ],
    )


def test_today_summary_aggregation():
    now = datetime(2026, 1, 7, 18, 0, tzinfo=datetime.now().astimezone().tzinfo)
    entries = [_entry(7, 500, 30, 40, 20), _entry(6, 300, 15, 20, 10)]

    summary = today_summary(entries, now=now)

    assert summary.entries_count == 1
    assert summary.totals.calories == 500
    assert summary.totals.protein_g == 30


def test_last_7_days_summary_aggregation():
    now = datetime(2026, 1, 7, 23, 0, tzinfo=datetime.now().astimezone().tzinfo)
    entries = [
        _entry(7, 500, 30, 40, 20),
        _entry(6, 300, 15, 20, 10),
        _entry(1, 700, 50, 60, 30),
    ]

    summary = last_7_days_summary(entries, now=now)

    assert summary.entries_count == 3
    assert summary.totals.calories == 1500
    assert summary.totals.protein_g == 95
    assert summary.totals.carbs_g == 120
    assert summary.totals.fat_g == 60
