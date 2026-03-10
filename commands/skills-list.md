---
description: Inspect installed OpenCode skills in summary, detail, or audit mode.
---

Use the `skills-list` skill and run the local analyzer for the requested mode.

Interpret `$ARGUMENTS` as one of:

- `summary`
- `detail <skill-name>`
- `audit`

Rules:

1. If no arguments are given, default to `summary`.
2. For `detail`, require a skill name.
3. Always run the local analyzer first:
   - `python ~/.config/opencode/skills/skills-list/scripts/skills_list.py summary`
   - `python ~/.config/opencode/skills/skills-list/scripts/skills_list.py detail --skill <name>`
   - `python ~/.config/opencode/skills/skills-list/scripts/skills_list.py audit`
4. Summarize the result clearly for the user instead of dumping unnecessary raw output unless they explicitly ask for JSON.
