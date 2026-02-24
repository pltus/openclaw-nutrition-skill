from datetime import datetime

from oc_nutrition.export import render_weekly_markdown
from oc_nutrition.models import MealItem, MealLogEntry
from oc_nutrition.summaries import last_7_days_summary


def test_markdown_export_contains_expected_sections():
    now = datetime(2026, 1, 7, 10, 0, tzinfo=datetime.now().astimezone().tzinfo)
    entries = [
        MealLogEntry(
            timestamp=now,
            meal_type="breakfast",
            items=[
                MealItem(
                    name="oatmeal",
                    quantity="1 bowl",
                    calories=350,
                    protein_g=12,
                    carbs_g=55,
                    fat_g=8,
                )
            ],
        )
    ]

    summary = last_7_days_summary(entries, now=now)
    markdown = render_weekly_markdown(entries, summary, generated_at=now)

    assert "# Weekly Nutrition Report" in markdown
    assert "## Totals" in markdown
    assert "## Notes" in markdown
    assert "oatmeal" in markdown
