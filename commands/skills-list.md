---
description: Inspect installed OpenCode skills in summary, detail, or audit mode.
---

Use the global `skills-list` analyzer result below to answer the user's request.

Requested arguments: `$ARGUMENTS`

Analyzer output:

!`python ~/.config/opencode/skills/skills-list/scripts/command_entry.py $ARGUMENTS`

Summarize the result clearly.

If the user requested a detail view without a skill name, explain the correct usage:

`/skills-list detail <skill-name>`

If the user asks for raw structured output, mention that `--format json` is supported by the analyzer script.
