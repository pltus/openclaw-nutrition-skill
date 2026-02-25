from __future__ import annotations

from datetime import datetime
from pathlib import Path

import typer

from oc_nutrition.export import export_weekly_markdown
from oc_nutrition.image_analysis import ImageAnalysisError, analyze_food_image_online
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


def _format_entry_preview(entry: MealLogEntry) -> str:
    item = entry.items[0]
    return (
        "Entry preview\n"
        f"Timestamp: {entry.timestamp.isoformat()}\n"
        f"Meal type: {entry.meal_type}\n"
        f"Item: {item.name} ({item.quantity})\n"
        f"Calories: {item.calories:.1f}\n"
        f"Protein (g): {item.protein_g:.1f}\n"
        f"Carbs (g): {item.carbs_g:.1f}\n"
        f"Fat (g): {item.fat_g:.1f}\n"
        f"Fiber (g): {item.fiber_g if item.fiber_g is not None else '-'}\n"
        f"Sodium (mg): {item.sodium_mg if item.sodium_mg is not None else '-'}\n"
        f"Source: {item.source or '-'}\n"
        f"Confidence: {item.confidence if item.confidence is not None else '-'}\n"
        f"Notes: {entry.notes or '-'}"
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
    confirm: bool = typer.Option(
        False,
        "--confirm/--no-confirm",
        help="Set --confirm to append the previewed entry.",
    ),
    data_dir: Path | None = typer.Option(None, help="Override data directory."),
) -> None:
    """Preview meal details, then append to NDJSON only with explicit confirmation."""
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
    except (ValueError, StorageError) as exc:
        raise typer.BadParameter(str(exc)) from exc

    typer.echo(_format_entry_preview(entry))
    if not confirm:
        typer.echo("Not saved yet. Re-run with --confirm to append this entry.")
        return

    try:
        destination = append_log_entry(entry, resolve_data_dir(data_dir))
    except StorageError as exc:
        raise typer.BadParameter(str(exc)) from exc

    typer.echo(f"Confirmed and appended entry to {destination}")


@app.command("log-image")
def log_image_meal(
    image: Path = typer.Option(..., exists=True, file_okay=True, dir_okay=False, readable=True),
    meal_type: str = typer.Option(..., help="One of breakfast/lunch/dinner/snack."),
    notes: str | None = typer.Option(None),
    analyze: bool = typer.Option(
        False,
        "--analyze/--no-analyze",
        help="Set --analyze to explicitly allow online image analysis.",
    ),
    confirm: bool = typer.Option(
        False,
        "--confirm/--no-confirm",
        help="Set --confirm to append analyzed result after preview.",
    ),
    data_dir: Path | None = typer.Option(None, help="Override data directory."),
) -> None:
    """Analyze food image online, preview estimates, append only with explicit confirmation."""
    if not analyze:
        typer.echo("Analysis not started. Re-run with --analyze to allow online analysis.")
        return

    try:
        estimate = analyze_food_image_online(image)
    except ImageAnalysisError as exc:
        raise typer.BadParameter(str(exc)) from exc

    typer.echo("Image analysis result")
    typer.echo(f"Food: {estimate.food_name}")
    typer.echo(f"Quantity: {estimate.quantity}")
    typer.echo(f"Calories: {estimate.calories:.1f}")
    typer.echo(f"Protein (g): {estimate.protein_g:.1f}")
    typer.echo(f"Carbs (g): {estimate.carbs_g:.1f}")
    typer.echo(f"Fat (g): {estimate.fat_g:.1f}")
    typer.echo(f"Confidence: {estimate.confidence:.2f}")
    typer.echo(f"Reasoning: {estimate.reasoning or '-'}")

    if not confirm:
        typer.echo("Not saved yet. Re-run with --confirm to append this entry.")
        return

    entry = MealLogEntry(
        timestamp=_now_local(),
        meal_type=meal_type,
        items=[
            MealItem(
                name=estimate.food_name,
                quantity=estimate.quantity,
                calories=estimate.calories,
                protein_g=estimate.protein_g,
                carbs_g=estimate.carbs_g,
                fat_g=estimate.fat_g,
                source="estimate",
                confidence=estimate.confidence,
            )
        ],
        notes=notes,
    )
    try:
        destination = append_log_entry(entry, resolve_data_dir(data_dir))
    except (ValueError, StorageError) as exc:
        raise typer.BadParameter(str(exc)) from exc

    typer.echo(f"Confirmed and appended entry to {destination}")


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
