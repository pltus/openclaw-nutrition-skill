from __future__ import annotations

from datetime import datetime
from pathlib import Path

from oc_nutrition.models import MealLogEntry
from oc_nutrition.summaries import SummaryResult, last_7_days_summary


def render_weekly_markdown(entries: list[MealLogEntry], summary: SummaryResult, generated_at: datetime) -> str:
    lines = [
        "# Weekly Nutrition Report",
        "",
        f"Generated: {generated_at.isoformat()}",
        f"Range: {summary.start.isoformat()} to {summary.end.isoformat()}",
        "",
        "## Totals",
        f"- Entries logged: {summary.entries_count}",
        f"- Calories: {summary.totals.calories:.1f}",
        f"- Protein (g): {summary.totals.protein_g:.1f}",
        f"- Carbs (g): {summary.totals.carbs_g:.1f}",
        f"- Fat (g): {summary.totals.fat_g:.1f}",
        "",
        "## Notes",
        "- Log corrections by appending a new entry; do not edit prior records.",
        "- Values are user-provided estimates unless otherwise noted.",
    ]

    recent = [
        entry
        for entry in entries
        if summary.start <= entry.timestamp.astimezone(summary.start.tzinfo) <= summary.end
    ]
    if recent:
        lines.extend(["", "## Recent Meals"])
        for entry in recent[-10:]:
            item_names = ", ".join(item.name for item in entry.items)
            lines.append(f"- {entry.timestamp.isoformat()} ({entry.meal_type}): {item_names}")

    return "\n".join(lines) + "\n"


def export_weekly_markdown(entries: list[MealLogEntry], exports_dir: Path, now: datetime) -> Path:
    exports_dir.mkdir(parents=True, exist_ok=True)
    summary = last_7_days_summary(entries, now=now)
    report_body = render_weekly_markdown(entries=entries, summary=summary, generated_at=now)
    out_path = exports_dir / f"weekly_{now.date().isoformat()}.md"
    out_path.write_text(report_body, encoding="utf-8")
    return out_path
