# Data Model

## User profile (`data/profile.json`)
- `name`: display name.
- `timezone`: IANA timezone string or `local`.
- `daily_targets`: optional macro targets (`calories`, `protein_g`, `carbs_g`, `fat_g`).
- `preferences`: optional key/value preferences.

## Meal log (`data/meal_log.ndjson`)
Each line is one immutable `MealLogEntry` JSON object.

- `timestamp` (ISO 8601 with timezone offset)
- `meal_type` (`breakfast`, `lunch`, `dinner`, `snack`)
- `items` (list of `MealItem`)
- `notes` (optional)

### MealItem fields
- `name`
- `quantity` (free text)
- `calories`, `protein_g`, `carbs_g`, `fat_g` (float)
- `fiber_g` (optional float)
- `sodium_mg` (optional float)
- `source` (`manual` or `estimate`, optional)
- `confidence` (0..1, optional)
