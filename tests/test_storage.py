from datetime import datetime

from oc_nutrition.models import MealItem, MealLogEntry
from oc_nutrition.storage import append_log_entry, read_log_entries


def test_append_and_read_ndjson(tmp_path):
    entry = MealLogEntry(
        timestamp=datetime(2026, 1, 10, 12, 0, tzinfo=datetime.now().astimezone().tzinfo),
        meal_type="lunch",
        items=[
            MealItem(
                name="chicken salad",
                quantity="1 bowl",
                calories=450,
                protein_g=35,
                carbs_g=20,
                fat_g=18,
                source="manual",
                confidence=0.9,
            )
        ],
    )

    append_log_entry(entry, tmp_path)
    result = read_log_entries(tmp_path)

    assert len(result) == 1
    assert result[0].meal_type == "lunch"
    assert result[0].items[0].name == "chicken salad"
    assert result[0].items[0].calories == 450
