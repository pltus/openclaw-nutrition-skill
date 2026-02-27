---
name: openclaw-nutrition-skill
description: Chat-based meal logging, macro tracking, and weekly nutrition reports with append-only local storage workflows.
metadata: {"emoji":"🥗","category":"health","supports":["meal logging","macro estimation","weekly reports"]}
user-invocable: true
---

# OpenClaw Nutrition Skill

## What this skill does
- Capture quick meal logs from chat and store entries in append-only NDJSON.
- Estimate calories/macros from user-provided meals when exact data is unavailable.
- Summarize nutrition totals for today and the last 7 days.
- Export a weekly markdown report.

## Inputs it accepts
- Quick logs: meal type, one or more items, portions, optional notes.
- Photo logs: user-uploaded image path/input that may contain a meal.
- Macro details: calories, protein, carbs, fat, optional fiber/sodium.

## Workflow
1. If input is an image, request explicit approval for online analysis first.
2. For food images, use the **connected multimodal model** to estimate calories/macros from the photo (do not execute local Python code, scripts, or CLI commands).
3. Ask up to **2 clarifying questions** only if needed (missing meal type, quantities, or macros).
4. Confirm the final interpreted meal details before writing (explicit user confirmation required).
5. Append new log entry only after confirmation (never edit or delete old entries).
6. Return immediate summary (today and/or week totals) when requested.
7. Offer markdown export path for weekly report output.

> Note: Clarifying-question limits are enforced at the OpenClaw agent orchestration layer.

## Output formats
- **Chat summary**: concise confirmation + macro totals.
- **Markdown export**: weekly report at `data/exports/weekly_YYYY-MM-DD.md`.

## Safety rules
- Keep storage append-only; corrections are new entries.
- Avoid collecting secrets or credentials.
- Do not run downloads, shell commands, or network actions unless user explicitly confirms.
- For image analysis, call the connected model directly for estimation and show the result first; require explicit confirmation before writing logs.
- Keep data local by default.

## OpenClaw execution policy
- Follow OpenClaw skill interaction style (chat-first, confirmation-first).
- Prefer the connected model/tooling route for inference and reasoning.
- Do **not** ask the user to run Python files or invoke local CLI commands as part of normal skill execution.
- Treat Python modules in this repository as reference implementation details, not the primary runtime path in OpenClaw chats.

## Example dialogues
1. **Quick log**
   - User: "Log lunch: chicken salad, one bowl, about 450 calories."
   - Assistant: "Any macro estimates for protein/carbs/fat?"
   - User: "35 protein, 20 carbs, 18 fat."
   - Assistant: "확인했어요. 저장하려면 확정할까요?"

2. **Photo log**
   - User: "이 사진으로 저녁 기록해줘."
   - Assistant: "온라인 이미지 분석을 실행해도 될까요?"
   - User: "응."
   - Assistant: "분석 결과를 보여드릴게요. 이 내용으로 저장할까요?"

3. **Weekly export**
   - User: "Create my weekly report."
   - Assistant: "Done. Export generated at data/exports/weekly_YYYY-MM-DD.md with totals and recent meals."
