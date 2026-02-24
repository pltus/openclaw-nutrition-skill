from __future__ import annotations

from datetime import datetime
from pathlib import Path

import typer

from oc_nutrition.export import export_weekly_markdown
from oc_nutrition.models import MealItem, MealLogEntry
from oc_nutrition.storage import (
    StorageError,
    append_log_entry,
    init_profile_from_example,
    read_log_entries,
    resolve_data_dir,
)
from oc_nutrition.summaries import last_7_days_summary, today_summary

app = typer.Typer(help="OpenClaw nutrition logging toolkit.")


def _now_local() -> datetime:
    return datetime.now().astimezone()


def _format_summary(label: str, summary) -> str:
    return (
        f"{label}\n"
        f"Range: {summary.start.isoformat()} -> {summary.end.isoformat()}\n"
        f"Entries: {summary.entries_count}\n"
        f"Calories: {summary.totals.calories:.1f}\n"
        f"Protein (g): {summary.totals.protein_g:.1f}\n"
        f"Carbs (g): {summary.totals.carbs_g:.1f}\n"
        f"Fat (g): {summary.totals.fat_g:.1f}"
    )


@app.command("init-profile")
def init_profile(
    data_dir: Path | None = typer.Option(None, help="Override data directory."),
    example: Path = typer.Option(
        Path("data/profile.example.json"),
        help="Path to example profile template.",
    ),
) -> None:
    """Initialize data/profile.json from the example template."""
    target_dir = resolve_data_dir(data_dir)
    try:
        destination = init_profile_from_example(target_dir, example)
    except StorageError as exc:
        raise typer.BadParameter(str(exc)) from exc
    typer.echo(f"Profile created at {destination}")


@app.command("log")
def log_meal(
    meal_type: str = typer.Option(..., help="One of breakfast/lunch/dinner/snack."),
    item: str = typer.Option(..., help="Meal item name."),
    qty: str = typer.Option(..., help="Quantity text (e.g., '1 bowl')."),
    calories: float = typer.Option(..., min=0),
    protein: float = typer.Option(..., min=0),
    carbs: float = typer.Option(..., min=0),
    fat: float = typer.Option(..., min=0),
    fiber: float | None = typer.Option(None, min=0),
    sodium: float | None = typer.Option(None, min=0),
    notes: str | None = typer.Option(None),
    source: str | None = typer.Option(None, help="manual or estimate."),
    confidence: float | None = typer.Option(None, min=0, max=1),
    data_dir: Path | None = typer.Option(None, help="Override data directory."),
) -> None:
    """Append a meal log entry to NDJSON storage (append-only)."""
    now = _now_local()
    try:
        meal_item = MealItem(
            name=item,
            quantity=qty,
            calories=calories,
            protein_g=protein,
            carbs_g=carbs,
            fat_g=fat,
            fiber_g=fiber,
            sodium_mg=sodium,
            source=source,
            confidence=confidence,
        )
        entry = MealLogEntry(
            timestamp=now,
            meal_type=meal_type,
            items=[meal_item],
            notes=notes,
        )
        destination = append_log_entry(entry, resolve_data_dir(data_dir))
    except (ValueError, StorageError) as exc:
        raise typer.BadParameter(str(exc)) from exc

    typer.echo(f"Appended entry to {destination}")


@app.command("today")
def show_today(data_dir: Path | None = typer.Option(None, help="Override data directory.")) -> None:
    """Show macro totals for today."""
    entries = read_log_entries(resolve_data_dir(data_dir))
    summary = today_summary(entries)
    typer.echo(_format_summary("Today totals", summary))


@app.command("week")
def show_week(data_dir: Path | None = typer.Option(None, help="Override data directory.")) -> None:
    """Show macro totals for the last 7 days (including today)."""
    entries = read_log_entries(resolve_data_dir(data_dir))
    summary = last_7_days_summary(entries)
    typer.echo(_format_summary("Last 7 days totals", summary))


@app.command("export-week")
def export_week(data_dir: Path | None = typer.Option(None, help="Override data directory.")) -> None:
    """Export a weekly markdown report to data/exports."""
    base_dir = resolve_data_dir(data_dir)
    entries = read_log_entries(base_dir)
    now = _now_local()
    output = export_weekly_markdown(entries, exports_dir=base_dir / "exports", now=now)
    typer.echo(f"Exported report: {output}")


if __name__ == "__main__":
    app()
