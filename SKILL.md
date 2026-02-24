---
name: openclaw-nutrition-skill
description: Chat-based meal logging, macro tracking, weekly nutrition reports, and meal planning/grocery list support with append-only local storage workflows.
metadata: {"emoji":"🥗","category":"health","supports":["meal logging","macro estimation","weekly reports","meal planning","grocery lists"]}
user-invocable: true
---

# OpenClaw Nutrition Skill

## What this skill does
- Capture quick meal logs from chat and store entries in append-only NDJSON.
- Estimate calories/macros from user-provided meals when exact data is unavailable.
- Summarize nutrition totals for today and the last 7 days.
- Export a weekly markdown report.
- Assist with meal planning and grocery list suggestions from recent logs.

## Inputs it accepts
- Quick logs: meal type, one or more items, portions, optional notes.
- Photo logs: user-uploaded image path/input that may contain a meal.
- Macro details: calories, protein, carbs, fat, optional fiber/sodium.
- Goals updates: daily calorie/macro targets and preference notes.
- Correction entries: append-only corrections when a previous log needs adjustment.

## Workflow
1. If input is an image, first classify whether it appears to be food.
2. For food images, run online nutrition estimation to infer calories/macros from the photo.
3. Ask up to **2 clarifying questions** only if needed (missing meal type, quantities, or macros).
4. Confirm the final interpreted meal details before writing (explicit user confirmation required).
5. Append new log entry only after confirmation (never edit or delete old entries).
6. Return immediate summary (today and/or week totals) when requested.
7. Offer markdown export path for weekly report output.

## Output formats
- **Chat summary**: concise confirmation + macro totals.
- **Markdown export**: weekly report at `data/exports/weekly_YYYY-MM-DD.md`.

## Safety rules
- Keep storage append-only; corrections are new entries.
- Avoid collecting secrets or credentials.
- Do not run downloads, shell commands, or network actions unless user explicitly confirms.
- For image analysis, show estimated result first and require explicit confirmation before writing logs.
- Keep data local by default.

## Example dialogues
1. **Quick log**
   - User: "Log lunch: chicken salad, one bowl, about 450 calories."
   - Assistant: "Any macro estimates for protein/carbs/fat?"
   - User: "35 protein, 20 carbs, 18 fat."
   - Assistant: "Confirmed. Appending lunch entry and updating today totals."

2. **Correction entry**
   - User: "I undercounted breakfast by 120 calories."
   - Assistant: "I will append a correction note entry (no edits to old records). Confirm?"
   - User: "Yes."
   - Assistant: "Correction logged and totals refreshed."

3. **Goals update**
   - User: "Set my daily target to 2100 calories, 140 protein, 230 carbs, 70 fat."
   - Assistant: "Confirmed. I will update your profile targets and keep logs unchanged."

4. **Weekly export**
   - User: "Create my weekly report."
   - Assistant: "Done. Export generated at data/exports/weekly_YYYY-MM-DD.md with totals and recent meals."
