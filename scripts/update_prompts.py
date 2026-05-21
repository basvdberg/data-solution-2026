#!/usr/bin/env python3
"""Build prompts.md for the current repository from Cursor agent transcripts."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

TRANSCRIPTS_DIR = (
    Path.home()
    / ".cursor"
    / "projects"
    / "c-Dev2-Data-Engineering-2-0"
    / "agent-transcripts"
)

PROMPTS_FILENAME = "prompts.md"

# Match prompts to a repo by keywords (case-insensitive). First matching project wins
# when scores tie, order below is used as priority for equal scores.
PROJECT_FILTERS: list[tuple[str, list[str]]] = [
    (
        "data-engineering-2026",
        [
            r"data-engineering-2026",
            r"Data Engineering 2026",
            r"ci-cd-old-vs-new",
            r"open-standard-drives-generation",
            r"way of working with genai",
            r"new project.*data engineering",
            r"describing data engineering in 2026",
            r"markdown-toc",
            r"markdown-project-structure",
            r"project structure skill",
            r"table of contents skill",
            r"exclude the title in the table of contents",
            r"cursor hook",
            r"better way.*table of contents",
        ],
    ),
    (
        "data-solution-2026",
        [
            r"data-solution-2026",
            r"data solution 2026",
            r"knmi-daggegevens",
            r"\bKNMI\b",
            r"\bWFS\b",
            r"Extractors",
            r"plan3",
            r"\bOData\b",
            r"northwind",
            r"regions\.json",
            r"DataObjectMappings",
            r"DataObjects",
            r"architecture-staging",
            r"staging layer",
            r"000_Source",
            r"100_Landing",
            r"Parquet",
            r"GML",
            r"ADL",
            r"Handlebars",
            r"cbs\.json",
            r"WFS extractor",
        ],
    ),
    (
        "data-engineering-design-patterns",
        [
            r"data-engineering-design-patterns",
            r"Data Engineering Design Patterns",
            r"design-patterns/",
            r"definitions/",
            r"implementation/",
            r"business intelligence",
            r"DataEngineeringWithAI",
            r"kebab-case",
            r"event-based-orchestration",
            r"separate what and how",
            r"historic-bitemporal",
            r"object-property-tree",
            r"full-data-solution",
            r"prompts\.md",
            r"prompts like you did",
            r"other projects",
            r"pre-commit\.py",
            r"table of contents for the entire project",
            r"Store all prompts",
        ],
    ),
]

SKIP_PATTERNS = [
    re.compile(r"^(yes|no|ja|nee)$", re.IGNORECASE),
    re.compile(r"^commit", re.IGNORECASE),
    re.compile(r"^push", re.IGNORECASE),
    re.compile(r"^clone\s+http", re.IGNORECASE),
    re.compile(r"^install\s", re.IGNORECASE),
    re.compile(r"cursor\s*(plan|billing|spending|cost|usage)", re.IGNORECASE),
    re.compile(r"(left click|context menu|extension).*(cursor|ide)", re.IGNORECASE),
    re.compile(r"^(how can I|add an item|can you add).*(cursor|ide|menu)", re.IGNORECASE),
    re.compile(r"(preview|open).*(markdown|default)", re.IGNORECASE),
    re.compile(r"^Store all prompts", re.IGNORECASE),
    re.compile(r"^Create pre-commit", re.IGNORECASE),
    re.compile(r"(key|keybind|shortcut).*(Edit Markdown|assign)", re.IGNORECASE),
    re.compile(r"I mean.*(cursor|ide|extension|context menu)", re.IGNORECASE),
    re.compile(r"(dashboard|visuali[sz]e).*(cursor|usage|cost)", re.IGNORECASE),
    re.compile(r"(monthly|plan limit|tokens used|csv)", re.IGNORECASE),
    re.compile(r"(image generation|model.*runtime)", re.IGNORECASE),
    re.compile(r"(disabled by default|expensive)", re.IGNORECASE),
    re.compile(r"^Rename the repo", re.IGNORECASE),
    re.compile(r"^I mean (the|in)", re.IGNORECASE),
    re.compile(r"percentage.*(covered|usage|max)", re.IGNORECASE),
    re.compile(r"(show me|inform me).*(usage|resources|cost)", re.IGNORECASE),
    re.compile(r"schematic picture", re.IGNORECASE),
    re.compile(r"Switch to a model", re.IGNORECASE),
    re.compile(r"7\.4M tokens", re.IGNORECASE),
    re.compile(r"dalssoft", re.IGNORECASE),
    re.compile(r"(change|find out).*(items|options).*(context menu|this menu)", re.IGNORECASE),
    re.compile(r"^Briefly inform the user", re.IGNORECASE),
]


def is_content_prompt(prompt: str) -> bool:
    for pattern in SKIP_PATTERNS:
        if pattern.search(prompt):
            return False
    return len(prompt) > 5


def score_prompt(prompt: str, patterns: list[str]) -> int:
    return sum(1 for pat in patterns if re.search(pat, prompt, re.IGNORECASE))


def assign_project(prompt: str) -> str | None:
    best_name: str | None = None
    best_score = 0
    for name, patterns in PROJECT_FILTERS:
        score = score_prompt(prompt, patterns)
        if score > best_score:
            best_score = score
            best_name = name
    return best_name


def extract_sessions_from_transcripts() -> list[list[str]]:
    if not TRANSCRIPTS_DIR.exists():
        return []

    sessions: list[list[str]] = []
    for session_dir in sorted(TRANSCRIPTS_DIR.iterdir()):
        if not session_dir.is_dir():
            continue
        transcript = session_dir / f"{session_dir.name}.jsonl"
        if not transcript.exists():
            continue

        prompts: list[str] = []
        try:
            for line in transcript.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                entry = json.loads(line)
                if entry.get("role") != "user":
                    continue
                for block in entry.get("message", {}).get("content", []):
                    if block.get("type") != "text":
                        continue
                    match = re.search(
                        r"<user_query>\s*(.*?)\s*</user_query>",
                        block["text"],
                        re.DOTALL,
                    )
                    if not match:
                        continue
                    prompt = match.group(1).strip()
                    if is_content_prompt(prompt):
                        prompts.append(prompt)
        except (json.JSONDecodeError, KeyError, UnicodeDecodeError):
            continue

        if prompts:
            sessions.append(prompts)

    return sessions


def sessions_for_project(all_sessions: list[list[str]], project: str) -> list[list[str]]:
    filtered: list[list[str]] = []
    for session in all_sessions:
        project_prompts = [p for p in session if assign_project(p) == project]
        if project_prompts:
            filtered.append(project_prompts)
    return filtered


def generate_prompts_md(project: str, sessions: list[list[str]]) -> str:
    lines = [
        "# Prompts",
        "",
        f"This document contains the prompts used to generate and refine the content in **{project}**.",
        "",
    ]
    for i, prompts in enumerate(sessions, 1):
        lines.append(f"## Session {i}")
        lines.append("")
        for j, prompt in enumerate(prompts, 1):
            lines.append(f"{j}. {prompt}")
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def update_prompts(repo_root: Path, project: str | None = None) -> bool:
    project = project or repo_root.name
    known = {name for name, _ in PROJECT_FILTERS}
    if project not in known:
        print(
            f"warning: unknown project '{project}'; no prompts.md written",
            file=sys.stderr,
        )
        return False

    sessions = sessions_for_project(extract_sessions_from_transcripts(), project)
    prompts_path = repo_root / PROMPTS_FILENAME
    new_content = generate_prompts_md(project, sessions)

    if prompts_path.exists():
        current = prompts_path.read_text(encoding="utf-8")
        if current.strip() == new_content.strip():
            return False

    prompts_path.write_text(new_content, encoding="utf-8", newline="\n")
    print(f"updated: {PROMPTS_FILENAME} ({len(sessions)} session(s), {project})")
    return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--project",
        help="Project folder name (default: name of git root directory).",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Repository root (default: current directory).",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Update prompts.md in every known project under the parent of --root.",
    )
    args = parser.parse_args(argv)

    if args.all:
        base = (args.root or Path.cwd()).resolve()
        changed = False
        for name, _ in PROJECT_FILTERS:
            project_root = base / name
            if project_root.is_dir():
                if update_prompts(project_root, name):
                    changed = True
        return 0

    repo_root = (args.root or Path.cwd()).resolve()
    update_prompts(repo_root, args.project)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
