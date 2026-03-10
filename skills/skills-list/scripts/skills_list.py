#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


KEYWORDS_RISK = {
    "secret",
    "token",
    "api key",
    "oauth",
    "credential",
    "browser automation",
    "chrome cdp",
    "danger",
    "reverse-engineered",
    "payment",
    "auth",
}

KEYWORDS_HOOKS = {
    "hook",
    "hooks",
    "pretooluse",
    "posttooluse",
    "stop hook",
}

CATEGORY_RULES = [
    ("security", ["security", "auth", "secret", "sensitive", "danger"]),
    ("frontend", ["ui", "ux", "frontend", "react", "design", "layout", "css"]),
    ("backend", ["backend", "api", "server", "database", "node", "express"]),
    ("research", ["retrieval", "notebooklm", "reference", "query", "research"]),
    (
        "content",
        [
            "markdown",
            "article",
            "wechat",
            "tweet",
            "xhs",
            "slide",
            "infographic",
            "comic",
            "post",
        ],
    ),
    ("media", ["image", "cover", "illustrat", "visual", "html"]),
    ("quality", ["tdd", "verification", "testing", "compact", "standards"]),
    (
        "meta",
        [
            "skill creator",
            "agent skill",
            "benchmark",
            "eval",
            "workflow",
            "learning",
            "audit my skills",
        ],
    ),
]


@dataclass
class SkillRecord:
    key: str
    path: str
    scope: str
    source_root: str
    name: str = ""
    description: str = ""
    version: str | None = None
    allowed_tools: list[str] = field(default_factory=list)
    compatibility: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    availability_status: str = "present"
    health_issues: list[str] = field(default_factory=list)
    has_scripts: bool = False
    has_references: bool = False
    has_assets: bool = False
    has_readme: bool = False
    scripts: list[str] = field(default_factory=list)
    references: list[str] = field(default_factory=list)
    trigger_keywords: list[str] = field(default_factory=list)
    trigger_examples: list[str] = field(default_factory=list)
    hook_usage: str = "none"
    category: str = "uncategorized"
    summary: str = ""
    update_status: str = "unknown"
    quality_score: int = 0
    security_score: int = 0
    maintainability_score: int = 0
    score: int = 0
    confidence: str = "medium"
    risk_flags: list[str] = field(default_factory=list)
    overlap_skills: list[str] = field(default_factory=list)
    conflict_risk: str = "low"
    strengthen: list[str] = field(default_factory=list)
    trim: list[str] = field(default_factory=list)
    add_new: list[str] = field(default_factory=list)
    installed_mtime: float = 0.0
    command_files: list[str] = field(default_factory=list)
    command_config_scopes: list[str] = field(default_factory=list)
    slash_entry: bool = False
    duplicate_scopes: list[str] = field(default_factory=list)
    duplicate_paths: list[str] = field(default_factory=list)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inspect installed OpenCode skills")
    parser.add_argument("mode", choices=["summary", "detail", "audit"])
    parser.add_argument("positional_skill", nargs="?")
    parser.add_argument("--skill", dest="named_skill")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("--cwd", default=os.getcwd())
    return parser.parse_args()


def discover_project_root(cwd: Path) -> Path | None:
    for current in [cwd, *cwd.parents]:
        if (current / ".opencode").exists():
            return current
    return None


def discover_roots(cwd: Path) -> list[tuple[str, Path]]:
    roots: list[tuple[str, Path]] = []
    global_root = Path.home() / ".config" / "opencode" / "skills"
    if global_root.exists():
        roots.append(("global", global_root))
    project_root = discover_project_root(cwd)
    if project_root:
        project_skills = project_root / ".opencode" / "skills"
        if project_skills.exists():
            roots.append(("project", project_skills))
    return roots


def load_command_map(cwd: Path) -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    config_commands: dict[str, list[str]] = defaultdict(list)
    file_commands: dict[str, list[str]] = defaultdict(list)

    global_command_dir = Path.home() / ".config" / "opencode" / "commands"
    if global_command_dir.exists():
        for path in sorted(global_command_dir.glob("*.md")):
            file_commands[path.stem].append("global")

    project_root = discover_project_root(cwd)
    if project_root:
        project_command_dir = project_root / ".opencode" / "commands"
        if project_command_dir.exists():
            for path in sorted(project_command_dir.glob("*.md")):
                file_commands[path.stem].append("project")

        config_path = project_root / ".opencode" / "opencode.json"
        if config_path.exists():
            try:
                data = json.loads(config_path.read_text(encoding="utf-8"))
                for key in (data.get("command") or {}).keys():
                    config_commands[key].append("project")
            except Exception:
                pass

    return config_commands, file_commands


def frontmatter_and_body(text: str) -> tuple[dict[str, Any], str, list[str]]:
    issues: list[str] = []
    if not text.startswith("---\n") and not text.startswith("---\r\n"):
        return {}, text, ["missing-frontmatter"]

    lines = text.splitlines()
    end_index = None
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            end_index = index
            break
    if end_index is None:
        return {}, text, ["unterminated-frontmatter"]

    front_lines = lines[1:end_index]
    body = "\n".join(lines[end_index + 1 :])
    data: dict[str, Any] = {}
    block_key: str | None = None
    metadata_key: str | None = None

    for raw in front_lines:
        line = raw.rstrip()
        if not line.strip():
            continue
        if block_key and (line.startswith("  ") or line.startswith("\t")):
            value = line.strip()
            previous = data.get(block_key, "")
            data[block_key] = (previous + " " + value).strip()
            continue
        block_key = None
        if line.startswith("metadata:"):
            data.setdefault("metadata", {})
            metadata_key = "metadata"
            continue
        if metadata_key and re.match(r"^\s{2,}[A-Za-z0-9_-]+:", line):
            key, value = line.strip().split(":", 1)
            data.setdefault("metadata", {})[key] = clean_scalar(value)
            continue
        metadata_key = None
        if ":" not in line:
            issues.append(f"unparsed-frontmatter:{line}")
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        stripped = value.strip()
        if stripped in {"|", ">", "|-", ">-"}:
            data[key] = ""
            block_key = key
            continue
        data[key] = clean_scalar(value)
    return data, body, issues


def clean_scalar(value: str) -> str:
    return value.strip().strip('"').strip("'")


def collect_trigger_data(
    description: str, body: str
) -> tuple[list[str], list[str], str]:
    keywords: set[str] = set()
    examples: list[str] = []
    lowered = f"{description}\n{body}".lower()

    for match in re.findall(r'"([^"]{3,80})"', description):
        if len(examples) < 8:
            examples.append(match)
        if 2 <= len(match.split()) <= 8:
            keywords.add(match.lower())

    trigger_section = False
    for line in body.splitlines():
        raw = line.rstrip()
        stripped = raw.strip(" -\t")
        if not stripped:
            continue
        lowered_line = stripped.lower()
        if lowered_line.startswith("## trigger") or lowered_line.startswith(
            "## when to use"
        ):
            trigger_section = True
            continue
        if trigger_section and stripped.startswith("## "):
            trigger_section = False
        if trigger_section and raw.lstrip().startswith(("-", "*")):
            if len(examples) < 8 and stripped not in examples:
                examples.append(stripped)
            if len(stripped.split()) <= 10:
                keywords.add(stripped.lower())
        elif any(
            token in lowered_line
            for token in [
                "use when user",
                "triggers on phrases like",
                "user asks to",
                "user mentions",
            ]
        ):
            if len(stripped) <= 140 and len(examples) < 8 and stripped not in examples:
                examples.append(stripped)

    hook_usage = (
        "inferred" if any(word in lowered for word in KEYWORDS_HOOKS) else "none"
    )
    clean_keywords = [
        item
        for item in sorted(keywords)
        if not any(
            noise in item
            for noise in [
                "json",
                "prompt",
                "output",
                "example",
                "description of",
                "expected result",
            ]
        )
    ]
    return clean_keywords[:12], examples[:10], hook_usage


def infer_category(name: str, description: str, path: str) -> str:
    haystack = f"{name} {description} {path}".lower()
    for category, hints in CATEGORY_RULES:
        if any(hint in haystack for hint in hints):
            return category
    return "uncategorized"


def infer_risk(description: str, body: str, scripts: list[str]) -> list[str]:
    text = f"{description}\n{body}".lower()
    flags = [keyword for keyword in KEYWORDS_RISK if keyword in text]
    if any(script.endswith((".sh", ".py", ".js")) for script in scripts):
        flags.append("executes-local-scripts")
    return sorted(set(flags))


def choose_summary(description: str, body: str) -> str:
    first = description.strip().split(". ")[0].strip()
    if first:
        return first
    for line in body.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            return stripped[:180]
    return "No summary available"


def score_record(record: SkillRecord) -> None:
    quality = 55
    security = 80
    maintainability = 60
    if record.description:
        quality += 10
    if record.trigger_examples:
        quality += 8
    if record.has_scripts:
        quality += 6
    if record.has_references:
        quality += 6
    if record.allowed_tools:
        quality += 5
    if record.version:
        maintainability += 8
    if record.has_readme:
        maintainability += 7
    if record.command_files or record.command_config_scopes:
        maintainability += 5
    if record.health_issues:
        quality -= min(20, 5 * len(record.health_issues))
        maintainability -= min(18, 4 * len(record.health_issues))
    if record.risk_flags:
        security -= min(35, 5 * len(record.risk_flags))
    if record.hook_usage != "none":
        maintainability += 4
    record.quality_score = clamp(quality)
    record.security_score = clamp(security)
    record.maintainability_score = clamp(maintainability)
    record.score = clamp(
        round(
            (
                record.quality_score
                + record.security_score
                + record.maintainability_score
            )
            / 3
        )
    )


def clamp(value: int) -> int:
    return max(0, min(100, value))


def recommendation_pass(record: SkillRecord) -> None:
    if not record.version:
        record.strengthen.append("add explicit version metadata")
    if not record.allowed_tools:
        record.strengthen.append("declare allowed-tools for clearer runtime safety")
    if not record.trigger_examples:
        record.strengthen.append(
            "add explicit trigger phrases or a When to Use section"
        )
    if not record.slash_entry:
        record.strengthen.append(
            "add a slash command entry if interactive discovery matters"
        )
    if record.risk_flags and "security" not in record.category:
        record.strengthen.append("document safety boundaries for risky capabilities")
    if record.health_issues:
        record.strengthen.append(
            "fix parse or structure issues before expanding the skill"
        )
    if record.score >= 85 and record.overlap_skills:
        record.trim.append(
            "consider merging or narrowing overlap with: "
            + ", ".join(record.overlap_skills[:3])
        )
    if record.category == "uncategorized":
        record.add_new.append(
            "improve description so category and trigger become easier to infer"
        )


def build_records(cwd: Path) -> list[SkillRecord]:
    records: list[SkillRecord] = []
    config_commands, file_commands = load_command_map(cwd)
    for scope, root in discover_roots(cwd):
        for skill_dir in sorted(root.iterdir()):
            if not skill_dir.is_dir():
                continue
            skill_md = skill_dir / "SKILL.md"
            if not skill_md.exists():
                continue
            text = skill_md.read_text(encoding="utf-8", errors="replace")
            frontmatter, body, issues = frontmatter_and_body(text)
            name = str(frontmatter.get("name") or skill_dir.name)
            description = str(frontmatter.get("description") or "")
            metadata = frontmatter.get("metadata") or {}
            version = frontmatter.get("version")
            if not version and isinstance(metadata, dict):
                version = metadata.get("version")
            allowed_tools = str(frontmatter.get("allowed-tools") or "").split()
            trigger_keywords, trigger_examples, hook_usage = collect_trigger_data(
                description, body
            )
            scripts = (
                sorted(
                    str(path.relative_to(skill_dir))
                    for path in (skill_dir / "scripts").rglob("*")
                    if path.is_file()
                )
                if (skill_dir / "scripts").exists()
                else []
            )
            references = (
                sorted(
                    str(path.relative_to(skill_dir))
                    for path in (skill_dir / "references").rglob("*.md")
                    if path.is_file()
                )
                if (skill_dir / "references").exists()
                else []
            )
            key = skill_dir.name

            record = SkillRecord(
                key=key,
                path=str(skill_dir),
                scope=scope,
                source_root=str(root),
                name=name,
                description=description,
                version=str(version) if version else None,
                allowed_tools=allowed_tools,
                compatibility=str(frontmatter.get("compatibility") or "") or None,
                metadata=metadata if isinstance(metadata, dict) else {},
                availability_status="present",
                health_issues=issues.copy(),
                has_scripts=(skill_dir / "scripts").exists(),
                has_references=(skill_dir / "references").exists(),
                has_assets=(skill_dir / "assets").exists(),
                has_readme=(skill_dir / "README.md").exists(),
                scripts=scripts[:20],
                references=references[:20],
                trigger_keywords=trigger_keywords,
                trigger_examples=trigger_examples,
                hook_usage=hook_usage,
                category=infer_category(name, description, str(skill_dir)),
                summary=choose_summary(description, body),
                risk_flags=infer_risk(description, body, scripts),
                installed_mtime=skill_md.stat().st_mtime,
                command_files=file_commands.get(key, []),
                command_config_scopes=config_commands.get(key, []),
                slash_entry=(key in file_commands or key in config_commands),
            )
            if not description:
                record.health_issues.append("missing-description")
            if not text.startswith("---"):
                record.health_issues.append("missing-frontmatter")
                record.availability_status = "incomplete"
            score_record(record)
            records.append(record)

    records = collapse_records(records)
    compute_overlap(records)
    for record in records:
        recommendation_pass(record)
    return records


def collapse_records(records: list[SkillRecord]) -> list[SkillRecord]:
    grouped: dict[str, list[SkillRecord]] = defaultdict(list)
    for record in records:
        grouped[record.key].append(record)

    result: list[SkillRecord] = []
    for key in sorted(grouped):
        items = sorted(
            grouped[key], key=lambda item: (item.scope != "project", item.path)
        )
        primary = items[0]
        if len(items) > 1:
            primary.duplicate_scopes = [item.scope for item in items[1:]]
            primary.duplicate_paths = [item.path for item in items[1:]]
            primary.command_files = sorted(
                set(
                    primary.command_files
                    + [scope for item in items[1:] for scope in item.command_files]
                )
            )
            primary.command_config_scopes = sorted(
                set(
                    primary.command_config_scopes
                    + [
                        scope
                        for item in items[1:]
                        for scope in item.command_config_scopes
                    ]
                )
            )
            primary.slash_entry = primary.slash_entry or any(
                item.slash_entry for item in items[1:]
            )
        result.append(primary)
    return result


def token_set(record: SkillRecord) -> set[str]:
    raw = " ".join(
        [record.name, record.description, record.category, *record.trigger_keywords]
    ).lower()
    stop_words = {
        "skill",
        "skills",
        "use",
        "when",
        "user",
        "asks",
        "with",
        "from",
        "that",
        "this",
        "your",
        "their",
        "create",
        "using",
        "installed",
        "report",
        "audit",
        "detail",
        "summary",
        "opencode",
    }
    return {
        token
        for token in re.findall(r"[a-z0-9][a-z0-9-]{2,}", raw)
        if token not in stop_words
    }


def compute_overlap(records: list[SkillRecord]) -> None:
    for record in records:
        base = token_set(record)
        overlap: list[str] = []
        for other in records:
            if other.key == record.key:
                continue
            common = base & token_set(other)
            if record.category == other.category and len(common) >= 3:
                overlap.append(other.key)
        record.overlap_skills = sorted(set(overlap))[:6]
        if len(record.overlap_skills) >= 3:
            record.conflict_risk = "high"
        elif record.overlap_skills:
            record.conflict_risk = "medium"


def format_summary(records: list[SkillRecord]) -> str:
    grouped: dict[str, list[SkillRecord]] = defaultdict(list)
    project_count = sum(1 for item in records if item.scope == "project")
    slash_count = sum(1 for item in records if item.slash_entry)
    duplicate_count = sum(1 for item in records if item.duplicate_paths)
    for record in sorted(
        records, key=lambda item: (item.category, item.key, item.scope)
    ):
        grouped[record.category].append(record)
    lines = [
        f"Skills Summary ({len(records)} skills)",
        f"project={project_count} global={len(records) - project_count} slash-enabled={slash_count} duplicates-collapsed={duplicate_count}",
    ]
    for category in sorted(grouped):
        items = grouped[category]
        lines.append("")
        lines.append(f"[{category}] {len(items)}")
        for item in items:
            version = item.version or "n/a"
            slash = "yes" if item.slash_entry else "no"
            lines.append(
                f"- {item.key} | scope={item.scope} | v={version} | score={item.score} | slash={slash} | update={item.update_status}"
            )
            lines.append(f"  {item.summary}")
            if item.duplicate_scopes:
                lines.append(f"  duplicates: {', '.join(item.duplicate_scopes)}")
    return "\n".join(lines)


def format_detail(record: SkillRecord) -> str:
    lines = [f"Skill Detail: {record.key}"]
    lines.append(f"name: {record.name}")
    lines.append(f"scope: {record.scope}")
    lines.append(f"path: {record.path}")
    lines.append(f"version: {record.version or 'unknown'}")
    lines.append(f"category: {record.category}")
    lines.append(f"status: {record.availability_status}")
    lines.append(f"update: {record.update_status}")
    lines.append(f"hooks: {record.hook_usage}")
    lines.append(f"slash-entry: {'yes' if record.slash_entry else 'no'}")
    lines.append(
        f"duplicates: {', '.join(record.duplicate_scopes) if record.duplicate_scopes else 'none'}"
    )
    lines.append(
        f"command-files: {', '.join(record.command_files) if record.command_files else 'none'}"
    )
    lines.append(
        f"command-config: {', '.join(record.command_config_scopes) if record.command_config_scopes else 'none'}"
    )
    lines.append(
        f"allowed-tools: {' '.join(record.allowed_tools) if record.allowed_tools else 'none'}"
    )
    lines.append(
        f"scores: overall={record.score} quality={record.quality_score} security={record.security_score} maintainability={record.maintainability_score}"
    )
    lines.append(f"summary: {record.summary}")
    lines.append(f"description: {record.description or 'missing'}")
    lines.append(
        f"trigger-keywords: {', '.join(record.trigger_keywords) if record.trigger_keywords else 'none inferred'}"
    )
    lines.append(
        f"trigger-examples: {', '.join(record.trigger_examples[:5]) if record.trigger_examples else 'none inferred'}"
    )
    lines.append(
        f"resources: scripts={len(record.scripts)} references={len(record.references)} assets={'yes' if record.has_assets else 'no'} readme={'yes' if record.has_readme else 'no'}"
    )
    lines.append(
        f"risk-flags: {', '.join(record.risk_flags) if record.risk_flags else 'none'}"
    )
    lines.append(
        f"overlap: {', '.join(record.overlap_skills) if record.overlap_skills else 'none'}"
    )
    lines.append(
        f"health-issues: {', '.join(record.health_issues) if record.health_issues else 'none'}"
    )
    lines.append(
        f"strengthen: {', '.join(record.strengthen) if record.strengthen else 'none'}"
    )
    lines.append(f"trim: {', '.join(record.trim) if record.trim else 'none'}")
    lines.append(f"add-new: {', '.join(record.add_new) if record.add_new else 'none'}")
    return "\n".join(lines)


def format_audit(records: list[SkillRecord]) -> str:
    grouped: dict[str, list[SkillRecord]] = defaultdict(list)
    for record in records:
        grouped[record.category].append(record)
    lines = [f"Skills Audit ({len(records)} skills)"]
    for category in sorted(grouped):
        items = sorted(
            grouped[category],
            key=lambda item: (
                item.conflict_risk != "high",
                item.update_status != "update-available",
                len(item.risk_flags),
                len(item.health_issues),
                item.key,
            ),
        )
        lines.append("")
        lines.append(f"[{category}]")
        for item in items:
            lines.append(
                f"- {item.key} | scope={item.scope} | score={item.score} | conflict={item.conflict_risk} | risk={len(item.risk_flags)} | issues={len(item.health_issues)} | slash={'yes' if item.slash_entry else 'no'}"
            )
            if item.duplicate_scopes:
                lines.append(f"  duplicates: {', '.join(item.duplicate_scopes)}")
            if item.overlap_skills:
                lines.append(f"  overlap: {', '.join(item.overlap_skills[:4])}")
            if item.risk_flags:
                lines.append(f"  risk: {', '.join(item.risk_flags[:4])}")
            if item.strengthen:
                lines.append(f"  strengthen: {item.strengthen[0]}")
            if item.trim:
                lines.append(f"  trim: {item.trim[0]}")
            if item.add_new:
                lines.append(f"  add: {item.add_new[0]}")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    cwd = Path(args.cwd).resolve()
    records = build_records(cwd)
    if args.mode == "detail":
        skill = args.named_skill or args.positional_skill
        if not skill:
            print("detail mode requires --skill <name>", file=sys.stderr)
            return 2
        match = next(
            (
                record
                for record in records
                if record.key == skill or record.name == skill
            ),
            None,
        )
        if not match:
            print(f"skill not found: {skill}", file=sys.stderr)
            return 1
        output: Any = asdict(match) if args.format == "json" else format_detail(match)
    elif args.mode == "summary":
        output = (
            [asdict(record) for record in records]
            if args.format == "json"
            else format_summary(records)
        )
    else:
        output = (
            [asdict(record) for record in records]
            if args.format == "json"
            else format_audit(records)
        )
    if args.format == "json":
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
