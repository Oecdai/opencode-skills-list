# opencode-skills-list

OpenCode skill for auditing installed skills with summary, detail, and category-first audit views, including versions, triggers, overlap, risk, and improvement suggestions.

## What It Does

`skills-list` inspects your installed OpenCode skills and generates three views:

- `summary` - grouped inventory overview
- `detail <skill-name>` - deep inspection for one skill
- `audit` - category-first audit with overlap, risk, and improvement hints

The analyzer focuses on local evidence from `SKILL.md`, directory structure, scripts, references, and inferred trigger patterns.

## Repository Layout

```text
skills/
  skills-list/
    SKILL.md
    scripts/
      skills_list.py
commands/
  skills-list.md
```

## Install

Clone this repository into your OpenCode config directory:

```bash
git clone https://github.com/Oecdai/opencode-skills-list.git ~/.config/opencode/opencode-skills-list
mkdir -p ~/.config/opencode/skills ~/.config/opencode/commands
ln -s ~/.config/opencode/opencode-skills-list/skills/skills-list ~/.config/opencode/skills/skills-list
ln -s ~/.config/opencode/opencode-skills-list/commands/skills-list.md ~/.config/opencode/commands/skills-list.md
```

If you prefer copying instead of symlinks:

```bash
cp -R ~/.config/opencode/opencode-skills-list/skills/skills-list ~/.config/opencode/skills/skills-list
cp ~/.config/opencode/opencode-skills-list/commands/skills-list.md ~/.config/opencode/commands/skills-list.md
```

## Usage

Slash command:

```text
/skills-list summary
/skills-list detail skill-creator
/skills-list audit
```

Natural language also works once the skill is installed:

```text
show my installed skills
audit my OpenCode skills
give me details for skills-list
```

## Notes

- `update_status` is conservative and defaults to `unknown` without hard evidence
- enabled/disabled state is inferred, not declared by most skills today
- overlap and conflict are heuristic, intended as audit hints rather than hard truth
