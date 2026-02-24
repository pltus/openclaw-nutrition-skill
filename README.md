# openclaw-nutrition-skill

A local-first OpenClaw skill and Python toolkit for chat-based meal logging, macro tracking, weekly summaries, and markdown report exports.

## Features
- Append-only meal logs in NDJSON (`data/meal_log.ndjson`).
- Pydantic validation for profiles and meal records.
- Daily and last-7-days macro aggregation.
- Weekly markdown exports to `data/exports/`.
- Safe-by-default behavior: local data only, no destructive rewrites.

## Repository layout
- `SKILL.md`: OpenClaw skill definition and workflow instructions.
- `oc_nutrition/`: Python package (`models`, `storage`, `summaries`, `export`, `cli`).
- `scripts/`: local script entrypoint (`scripts/oc_nutrition_cli.py`).
- `references/`: data model, logging rules, and privacy/security notes.
- `data/`: examples and local runtime data directory.
- `tests/`: pytest coverage for storage, aggregation, and export output.

## Setup
```bash
git clone <your-fork-or-repo-url>
cd openclaw-nutrition-skill
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

## CLI usage
Default data path is `./data`. Override with `OC_NUTRITION_DATA_DIR=/path/to/data`.

```bash
oc-nutrition init-profile
oc-nutrition log --meal-type lunch --item "chicken salad" --qty "1 bowl" --calories 450 --protein 35 --carbs 20 --fat 18
oc-nutrition today
oc-nutrition week
oc-nutrition export-week
```

## Data files
- `data/profile.json` (optional real profile)
- `data/meal_log.ndjson` (append-only log)
- `data/food_aliases.json` (optional aliases)
- `data/exports/weekly_YYYY-MM-DD.md` (generated reports)

To adjust a mistake, append a correction entry instead of editing historical lines.

## Use as an OpenClaw skill
1. Place this repository folder inside your OpenClaw skills directory **or** create a symlink to it.
2. Ensure `SKILL.md` exists at the repository root (it is the skill entry file).
3. Invoke the skill in OpenClaw chat and follow the meal logging workflow.

## Testing
```bash
pytest
```

## License
MIT (see `LICENSE`).
