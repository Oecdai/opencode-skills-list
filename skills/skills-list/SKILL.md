---
name: skills-list
description: Inspect installed OpenCode skills and report summary, detail, or audit views. Use when the user asks to list skills, inspect an installed skill, review skill health, compare overlapping skills, check trigger patterns, or run a skills audit. Triggers on phrases like "skills list", "show my installed skills", "skill detail", "audit my skills", "/skills-list", "which skills overlap", or "what skills should I trim or improve".
allowed-tools: Bash(python:*) Read Glob Grep
metadata:
  version: "0.1.0"
  source: local-opencode
---

# Skills List

Inspect the current OpenCode skill inventory with a consistent local report.

## When to Use

Use this skill when the user wants to:

- list installed skills with metadata
- inspect one skill in depth
- audit the whole skill inventory by category and health
- find overlap, conflicts, weak descriptions, or missing metadata
- understand trigger patterns, hooks, scripts, or allowed tools

## Views

Run the analyzer in one of these modes:

- `summary` - grouped inventory overview
- `detail <skill-name>` - deep dive into a single skill
- `audit` - grouped audit with overlap, risk, and improvement suggestions

## Command Usage

Preferred command forms:

- `/skills-list summary`
- `/skills-list detail <skill-name>`
- `/skills-list audit`

Natural language also works:

- `show my installed skills`
- `audit my OpenCode skills`
- `give me details for skill-creator`

## Execution

Always run the local analyzer first, then summarize the result for the user.

```bash
python scripts/skills_list.py summary
python scripts/skills_list.py detail --skill skill-creator
python scripts/skills_list.py audit
```

If the user asks for raw structured output, add `--format json`.

## Output Rules

- Prefer grouped text output for normal use
- In `summary`, group by category before listing skills
- In `audit`, group by category, then surface risks and recommendations inside each group
- In `detail`, include triggers, scripts/resources, overlap candidates, scores, and next actions
- When metadata is missing or inferred, say so explicitly

## Interpretation Rules

- Treat `name` and `description` in frontmatter as the primary source of truth
- Treat `version`, `allowed-tools`, `metadata.*`, and explicit trigger sections as optional
- Treat enabled/update status as inferred unless explicit evidence exists
- If a skill has scripts, references, or assets, mention them as capability signals
- If two skills have very similar trigger phrases or categories, flag them as potential overlap rather than definite conflict

## Limits

- Do not claim a skill is up to date unless the analyzer has hard evidence
- Do not claim a skill is disabled unless the analyzer has hard evidence
- Do not invent version numbers, authors, or source repos
- If a skill cannot be parsed cleanly, report `parse-error` and continue auditing the rest
