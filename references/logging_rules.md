# Logging Rules

1. Keep logs append-only; never rewrite prior lines in `meal_log.ndjson`.
2. If a correction is needed, append a new entry noting the correction in `notes`.
3. Record local timestamps with timezone offsets.
4. Ask at most two clarifying questions before logging when user input is incomplete.
5. Confirm meal details before append when any macro estimate is uncertain.
6. Keep entries practical and non-brand-specific unless user explicitly provides brand names.
