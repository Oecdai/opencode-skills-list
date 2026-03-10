# opencode-skills-list

中文 | [English](#english)

OpenCode 技能，用来审计已安装技能，提供 `summary`、`detail`、按分类优先的 `audit` 视图，并给出版本、触发方式、重叠风险与改进建议。

## 中文

### 功能简介

`skills-list` 会检查你当前安装的 OpenCode skills，并生成三种视图：

- `summary` - 按分类分组的技能总览
- `detail <skill-name>` - 单个技能的深入分析
- `audit` - 按分类优先的审计视图，包含重叠、风险与强化建议

分析器主要依据本地 `SKILL.md`、目录结构、脚本、参考资料以及推断出的触发模式。

### 仓库结构

```text
skills/
  skills-list/
    SKILL.md
    scripts/
      skills_list.py
commands/
  skills-list.md
```

### 安装方式

把仓库克隆到 OpenCode 配置目录：

```bash
git clone https://github.com/Oecdai/opencode-skills-list.git ~/.config/opencode/opencode-skills-list
mkdir -p ~/.config/opencode/skills ~/.config/opencode/commands
ln -s ~/.config/opencode/opencode-skills-list/skills/skills-list ~/.config/opencode/skills/skills-list
ln -s ~/.config/opencode/opencode-skills-list/commands/skills-list.md ~/.config/opencode/commands/skills-list.md
```

如果你更喜欢直接复制：

```bash
cp -R ~/.config/opencode/opencode-skills-list/skills/skills-list ~/.config/opencode/skills/skills-list
cp ~/.config/opencode/opencode-skills-list/commands/skills-list.md ~/.config/opencode/commands/skills-list.md
```

### 使用方式

斜线命令：

```text
/skills-list summary
/skills-list detail skill-creator
/skills-list audit
```

安装后也可以自然语言触发：

```text
show my installed skills
audit my OpenCode skills
give me details for skills-list
```

### 说明

- `update_status` 目前比较保守，没有硬证据时默认显示为 `unknown`
- 大多数 skills 没有显式 enabled/disabled 开关，所以状态通常是推断值
- 重叠与冲突属于启发式分析，目的是帮助审计，不代表绝对结论

### 发布规范

- 本仓库默认采用中英双语 Release
- 只要有已推送更新，就应创建对应的 GitHub Release
- 详细规则见 `RELEASING.md`

## English

OpenCode skill for auditing installed skills with summary, detail, and category-first audit views, including versions, triggers, overlap, risk, and improvement suggestions.

### What It Does

`skills-list` inspects your installed OpenCode skills and generates three views:

- `summary` - grouped inventory overview
- `detail <skill-name>` - deep inspection for one skill
- `audit` - category-first audit with overlap, risk, and improvement hints

The analyzer focuses on local evidence from `SKILL.md`, directory structure, scripts, references, and inferred trigger patterns.

### Repository Layout

```text
skills/
  skills-list/
    SKILL.md
    scripts/
      skills_list.py
commands/
  skills-list.md
```

### Install

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

### Usage

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

### Notes

- `update_status` is conservative and defaults to `unknown` without hard evidence
- enabled/disabled state is inferred, not declared by most skills today
- overlap and conflict are heuristic, intended as audit hints rather than hard truth

### Release Policy

- This repository uses bilingual GitHub Releases by default
- Whenever updates have been pushed, a matching GitHub Release should be created
- See `RELEASING.md` for the full policy
