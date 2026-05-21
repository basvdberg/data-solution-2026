#!/usr/bin/env python3
"""Insert or refresh auto-generated table of contents and project structure in Markdown files."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

DESCRIPTIONS_FILE = "project-structure-descriptions.json"

TOC_START = "<!-- markdown-toc:start -->"
TOC_END = "<!-- markdown-toc:end -->"
STRUCT_START = "<!-- markdown-project-structure:start -->"
STRUCT_END = "<!-- markdown-project-structure:end -->"

LEGACY_TOC_MARKERS = ("<!-- toc:start -->", "<!-- toc:end -->")
LEGACY_PROJECT_TOC_MARKERS = ("<!-- project-toc:start -->", "<!-- project-toc:end -->")

SKIP_HEADING_TITLES = frozenset(
    {"table of contents", "project structure", "project table of contents"}
)

EXCLUDE_DIR_NAMES = frozenset(
    {
        ".git",
        ".hg",
        ".svn",
        ".cursor",
        ".githooks",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        "node_modules",
        ".venv",
        "venv",
        "dist",
        "build",
        ".idea",
        ".vscode",
        "Data",
        "Output",
    }
)

EXCLUDE_FILE_NAMES = frozenset({".DS_Store", "Thumbs.db", "Untitled"})

MARKER_PAIRS = (
    (TOC_START, TOC_END),
    (STRUCT_START, STRUCT_END),
    (LEGACY_TOC_MARKERS[0], LEGACY_TOC_MARKERS[1]),
    (LEGACY_PROJECT_TOC_MARKERS[0], LEGACY_PROJECT_TOC_MARKERS[1]),
)


def git_root(start: Path) -> Path:
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=start,
            text=True,
            stderr=subprocess.DEVNULL,
        )
        return Path(out.strip())
    except (subprocess.CalledProcessError, FileNotFoundError):
        return start.resolve()


def slugify(text: str) -> str:
    slug = text.strip().lower()
    slug = re.sub(r"[^\w\s-]", "", slug, flags=re.UNICODE)
    slug = re.sub(r"\s+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug.strip("-")


def strip_generated_blocks(content: str) -> str:
    result = content
    for start, end in MARKER_PAIRS:
        pattern = re.compile(
            re.escape(start) + r"[\s\S]*?" + re.escape(end) + r"\n?",
            re.MULTILINE,
        )
        result = pattern.sub("", result)
    # Drop standalone "## Table of contents" / "## Project structure" sections if left over
    result = re.sub(
        r"\n## Table of contents\s*\n+",
        "\n",
        result,
        flags=re.IGNORECASE,
    )
    result = re.sub(
        r"\n## Project structure\s*\n+",
        "\n",
        result,
        flags=re.IGNORECASE,
    )
    result = re.sub(
        r"\n## Project table of contents\s*\n+",
        "\n",
        result,
        flags=re.IGNORECASE,
    )
    return result.strip() + "\n"


def extract_title_from_file(path: Path) -> str:
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return path.stem.replace("-", " ").title()


SECTION_LABEL_OVERRIDES = {
    "definitions": "Definitions",
    "design-patterns": "Design patterns",
    "implementation": "Implementation",
}

SITE_MAP_SKIP_DIR_NAMES = frozenset({"scripts"})


def section_label(folder_name: str) -> str:
    """Human-readable folder label matching the design-patterns table of contents."""
    return SECTION_LABEL_OVERRIDES.get(
        folder_name.lower(), folder_name.replace("-", " ").title()
    )


def build_design_patterns_site_map(repo_root: Path, from_file: Path) -> list[str]:
    """Site map shared by the readme table of contents and project structure blocks."""
    definitions: list[tuple[str, Path]] = []
    design_patterns: list[tuple[str, Path]] = []
    implementation: dict[str, list[tuple[str, Path]]] = {}

    for path in sorted((repo_root / "definitions").glob("*.md")):
        if path.name.lower() == "readme.md":
            continue
        definitions.append((extract_title_from_file(path), path))

    for path in sorted((repo_root / "design-patterns").glob("*.md")):
        if path.name.lower() == "readme.md":
            continue
        design_patterns.append((extract_title_from_file(path), path))

    impl_dir = repo_root / "implementation"
    if impl_dir.exists():
        for sub in sorted(impl_dir.iterdir()):
            if not sub.is_dir() or should_exclude_dir(sub.name):
                continue
            files: list[tuple[str, Path]] = []
            for path in sorted(sub.glob("*.md")):
                if path.name.lower() == "readme.md":
                    continue
                files.append((extract_title_from_file(path), path))
            if files:
                section = sub.name.replace("-", " ").title()
                implementation[section] = files

    from_dir = from_file.parent
    lines: list[str] = []
    root_readme = repo_root / "readme.md"
    rel_root = os.path.relpath(root_readme, from_dir).replace("\\", "/")
    lines.append(f"- [Data Engineering Design Patterns]({rel_root})")

    if definitions:
        lines.append(f"  - {section_label('definitions')}")
        for title, path in definitions:
            rel = os.path.relpath(path, from_dir).replace("\\", "/")
            lines.append(f"    - [{title}]({rel})")

    if design_patterns:
        lines.append(f"  - {section_label('design-patterns')}")
        for title, path in design_patterns:
            rel = os.path.relpath(path, from_dir).replace("\\", "/")
            lines.append(f"    - [{title}]({rel})")

    if implementation:
        lines.append(f"  - {section_label('implementation')}")
        for section, files in implementation.items():
            lines.append(f"    - {section}")
            for title, path in files:
                rel = os.path.relpath(path, from_dir).replace("\\", "/")
                lines.append(f"      - [{title}]({rel})")

    return lines


def build_generic_site_map(repo_root: Path, from_file: Path) -> list[str]:
    """TOC-style site map for repositories without the design-patterns layout."""
    from_dir = from_file.parent
    lines: list[str] = []
    root_readme = repo_root / "readme.md"
    if root_readme.is_file():
        title = extract_title_from_file(root_readme)
        rel = os.path.relpath(root_readme, from_dir).replace("\\", "/")
        lines.append(f"- [{title}]({rel})")
    lines.extend(_site_map_dir(repo_root, from_dir, depth=1))
    return lines


def _site_map_dir(root: Path, from_dir: Path, depth: int) -> list[str]:
    """Recurse directories using the same bullet rules as the design-patterns site map."""
    indent = "  " * depth
    lines: list[str] = []

    for path, is_dir in _list_tree_entries(root):
        if is_dir:
            if should_exclude_dir(path.name) or path.name in SITE_MAP_SKIP_DIR_NAMES:
                continue
            lines.append(f"{indent}- {section_label(path.name)}")
            lines.extend(_site_map_dir(path, from_dir, depth + 1))
            continue

        if path.name.lower() == "readme.md":
            continue
        title = extract_title_from_file(path)
        rel = os.path.relpath(path, from_dir).replace("\\", "/")
        lines.append(f"{indent}- [{title}]({rel})")

    return lines


def title_slug_from_block(title: str | None) -> str | None:
    """Slug for the document `#` title line, used to keep it out of the TOC."""
    if not title:
        return None
    first = title.strip().splitlines()[0]
    match = re.match(r"^#\s+(.+)$", first)
    if not match:
        return None
    plain = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", match.group(1).strip())
    return slugify(plain)


def parse_headings(
    lines: list[str],
    *,
    document_title_slug: str | None = None,
) -> list[tuple[int, str, str]]:
    """Collect `##`–`######` headings for the TOC (never `#` / h1)."""
    headings: list[tuple[int, str, str]] = []
    in_fence = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        match = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        if not match:
            continue
        level = len(match.group(1))
        if level < 2:
            continue
        title = match.group(2).strip()
        plain = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", title)
        plain = re.sub(r"`([^`]+)`", r"\1", plain)
        plain = plain.strip()
        if plain.lower() in SKIP_HEADING_TITLES:
            continue
        anchor = slugify(plain)
        if document_title_slug and anchor == document_title_slug:
            continue
        headings.append((level, plain, anchor))
    return headings


def build_toc_block(
    headings: list[tuple[int, str, str]],
    repo_root: Path,
    path: Path,
    *,
    document_title_slug: str | None = None,
) -> str:
    """Heading-based TOC only (site map lives in the project structure block)."""
    lines: list[str] = []
    toc_headings = [
        (level, title, anchor)
        for level, title, anchor in headings
        if not document_title_slug or anchor != document_title_slug
    ]
    if toc_headings:
        min_level = min(level for level, _, _ in toc_headings)
        for level, title, anchor in toc_headings:
            indent = "  " * (level - min_level)
            lines.append(f"{indent}- [{title}](#{anchor})")
    if not lines:
        return f"{TOC_START}\n_No sections yet._\n{TOC_END}"
    return f"{TOC_START}\n" + "\n".join(lines) + f"\n{TOC_END}"


def should_exclude_dir(name: str) -> bool:
    return name in EXCLUDE_DIR_NAMES or name.startswith(".")


def load_folder_descriptions(repo_root: Path) -> dict[str, str]:
    """Load optional short descriptions keyed by relative folder path (POSIX slashes)."""
    path = repo_root / DESCRIPTIONS_FILE
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"warning: invalid {DESCRIPTIONS_FILE}: {exc}", file=sys.stderr)
        return {}
    if not isinstance(data, dict):
        return {}
    return {
        str(key).replace("\\", "/").strip("/"): str(value).strip()
        for key, value in data.items()
        if str(value).strip()
    }


def should_include_markdown_file(name: str) -> bool:
    return name.lower() not in {"prompts.md"}


def _list_tree_entries(root: Path) -> list[tuple[Path, bool]]:
    """Return (path, is_directory) entries: directories first, then Markdown files."""
    try:
        directories = sorted(
            (p for p in root.iterdir() if p.is_dir() and not should_exclude_dir(p.name)),
            key=lambda p: p.name.lower(),
        )
        markdown_files = sorted(
            (
                p
                for p in root.iterdir()
                if p.is_file()
                and p.suffix.lower() == ".md"
                and should_include_markdown_file(p.name)
                and p.name not in EXCLUDE_FILE_NAMES
            ),
            key=lambda p: p.name.lower(),
        )
    except OSError:
        return []

    return [(path, True) for path in directories] + [(path, False) for path in markdown_files]


def build_project_structure(repo_root: Path, from_file: Path | None = None) -> str:
    """Same nested bullet site map as the readme table of contents (without in-page anchors)."""
    from_file = from_file or (repo_root / "readme.md")
    if (repo_root / "design-patterns").is_dir():
        lines = build_design_patterns_site_map(repo_root, from_file)
    else:
        lines = build_generic_site_map(repo_root, from_file)
    return f"{STRUCT_START}\n" + "\n".join(lines) + f"\n{STRUCT_END}"


def split_title_and_body(content: str) -> tuple[str | None, str]:
    lines = content.splitlines()
    if not lines:
        return None, ""

    first = lines[0]
    title_match = re.match(r"^#\s+(.+)$", first)
    if title_match:
        title_block = first + "\n"
        body = "\n".join(lines[1:]).lstrip("\n")
        return title_block, body

    return None, content


def _assemble_toc_only(original: str, title: str | None, body: str, toc: str) -> str:
    if TOC_START in original and TOC_END in original:
        pattern = re.compile(
            re.escape(TOC_START) + r"[\s\S]*?" + re.escape(TOC_END),
            re.MULTILINE,
        )
        return pattern.sub(toc, original, count=1)
    return assemble_document(title, body, toc, "")


def _assemble_structure_only(
    original: str, title: str | None, body: str, structure: str
) -> str:
    if STRUCT_START in original and STRUCT_END in original:
        pattern = re.compile(
            re.escape(STRUCT_START) + r"[\s\S]*?" + re.escape(STRUCT_END),
            re.MULTILINE,
        )
        return pattern.sub(structure, original, count=1)
    return assemble_document(title, body, "", structure)


def assemble_document(title: str | None, body: str, toc: str, structure: str) -> str:
    parts: list[str] = []
    if title:
        parts.append(title.rstrip("\n"))
        parts.append("")
    if toc.strip():
        parts.append("## Table of contents")
        parts.append("")
        parts.append(toc)
        parts.append("")
    if body.strip():
        parts.append(body.rstrip())
        parts.append("")
    if structure.strip():
        parts.append("## Project structure")
        parts.append("")
        parts.append(structure)
        parts.append("")
    return "\n".join(parts).rstrip() + "\n"


def update_file(
    path: Path,
    repo_root: Path,
    check: bool = False,
    *,
    toc_only: bool = False,
    structure_only: bool = False,
) -> bool:
    original = path.read_text(encoding="utf-8")
    cleaned = strip_generated_blocks(original)
    title, body = split_title_and_body(cleaned)
    document_title_slug = title_slug_from_block(title)
    headings = parse_headings(body.splitlines(), document_title_slug=document_title_slug)
    toc = build_toc_block(
        headings,
        repo_root,
        path,
        document_title_slug=document_title_slug,
    )
    structure = build_project_structure(repo_root, path)

    if toc_only:
        updated = _assemble_toc_only(original, title, body, toc)
    elif structure_only:
        updated = _assemble_structure_only(original, title, body, structure)
    else:
        updated = assemble_document(title, body, toc, structure)
    if updated == original:
        return False
    if check:
        print(f"would update: {path.relative_to(repo_root)}", file=sys.stderr)
        return True
    path.write_text(updated, encoding="utf-8", newline="\n")
    print(f"updated: {path.relative_to(repo_root)}")
    return True


def discover_markdown_files(repo_root: Path) -> list[Path]:
    files: list[Path] = []
    for path in repo_root.rglob("*.md"):
        if any(part in EXCLUDE_DIR_NAMES or part.startswith(".") for part in path.parts):
            continue
        if path.is_file() and path.name.lower() not in {"prompts.md"}:
            files.append(path)
    return sorted(files)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="Optional specific Markdown files; default is all *.md in the repository.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Report files that would change without writing.",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Repository root (default: detected via git).",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--toc-only",
        action="store_true",
        help="Refresh only the table of contents block.",
    )
    mode.add_argument(
        "--structure-only",
        action="store_true",
        help="Refresh only the project structure block (TOC-style bullets and file links).",
    )
    args = parser.parse_args(argv)

    repo_root = args.root.resolve() if args.root else git_root(Path.cwd())
    if args.paths:
        targets = [p.resolve() for p in args.paths]
    else:
        targets = discover_markdown_files(repo_root)

    changed = 0
    for path in targets:
        if not path.is_file():
            print(f"skip (not a file): {path}", file=sys.stderr)
            continue
        if path.suffix.lower() != ".md":
            continue
        if update_file(
            path,
            repo_root,
            check=args.check,
            toc_only=args.toc_only,
            structure_only=args.structure_only,
        ):
            changed += 1

    if args.check and changed:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
