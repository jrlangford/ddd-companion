#!/usr/bin/env python3
"""Evaluate skill quality against Anthropic best practices.

Checks automatable rules from:
  https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices

Walks the skills/ directory and runs these checks per skill:

  Size checks
    - All files under 500 lines (body lines for SKILL.md, total for others)
    - Per-file and per-skill token estimates vs context window budget
    - Reference files over 100 lines should have a table of contents

  Frontmatter checks
    - name: required, max 64 chars, lowercase/numbers/hyphens only,
      no reserved words ("anthropic", "claude")
    - description: required, non-empty, max 1024 chars

  Structure checks
    - No deeply nested references (max 1 level from SKILL.md)
    - No backslash paths in markdown links
    - Reference links in SKILL.md point to existing files
    - Consistent terminology (no mixed terms for same concept)

Token estimation uses ~4 characters per token (conservative for English
markdown; no tokenizer dependency required).
"""

import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# --- Configuration -----------------------------------------------------------

CONTEXT_WINDOW_TOKENS = 200_000
CHARS_PER_TOKEN = 4

THRESHOLDS = {
    "comfortable": 0.05,   # 10K tokens
    "acceptable":  0.10,   # 20K tokens
    "warning":     0.15,   # 30K tokens
}

SKILL_EXTENSIONS = {".md", ".json"}
MAX_FILE_LINES = 500
REFERENCE_TOC_THRESHOLD = 100  # lines above which a TOC is expected

NAME_MAX_LEN = 64
NAME_PATTERN = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
NAME_RESERVED = {"anthropic", "claude"}
DESC_MAX_LEN = 1024

# Markdown link pattern: [text](path)
MD_LINK = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")

# Terms that should not be mixed within a single skill.
# Each group is a set of variants for the same concept — only one should
# be used consistently.  Add project-specific groups here as drift is found.
TERM_GROUPS: list[set[str]] = [
    {"api endpoint", "api route"},
]

# --- Data model --------------------------------------------------------------

@dataclass
class Finding:
    level: str   # "error", "warning", "info"
    check: str   # short check name
    message: str
    file: Optional[str] = None


@dataclass
class FileInfo:
    path: Path          # relative to skill dir
    abs_path: Path      # absolute, for reading
    bytes: int
    lines: int
    est_tokens: int

    @property
    def is_entry_point(self) -> bool:
        return self.path.name == "SKILL.md"


@dataclass
class SkillInfo:
    name: str
    dir: Path
    files: list[FileInfo] = field(default_factory=list)
    findings: list[Finding] = field(default_factory=list)
    frontmatter: dict = field(default_factory=dict)

    @property
    def total_tokens(self) -> int:
        return sum(f.est_tokens for f in self.files)

    @property
    def entry_point_tokens(self) -> int:
        return sum(f.est_tokens for f in self.files if f.is_entry_point)

    @property
    def entry_point(self) -> Optional[FileInfo]:
        return next((f for f in self.files if f.is_entry_point), None)

    def add(self, level: str, check: str, msg: str, file: str = None):
        self.findings.append(Finding(level, check, msg, file))


# --- Helpers -----------------------------------------------------------------

def estimate_tokens(byte_count: int) -> int:
    return byte_count // CHARS_PER_TOKEN


def count_lines(path: Path) -> int:
    try:
        return sum(1 for _ in path.open("rb"))
    except OSError:
        return 0


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def parse_frontmatter(text: str) -> tuple[dict, int]:
    """Return (frontmatter_dict, body_start_line). Line count is 1-based."""
    fm = {}
    if not text.startswith("---"):
        return fm, 1
    end = text.find("\n---", 3)
    if end == -1:
        return fm, 1
    block = text[4:end]
    body_start = block.count("\n") + 3  # opening --- + block + closing ---
    for line in block.split("\n"):
        if ":" in line:
            key, _, val = line.partition(":")
            fm[key.strip()] = val.strip().strip('"').strip("'")
    return fm, body_start


def fmt_tokens(n: int) -> str:
    return f"{n / 1000:.1f}K" if n >= 1000 else str(n)


def fmt_pct(tokens: int) -> str:
    return f"{tokens / CONTEXT_WINDOW_TOKENS * 100:.1f}%"


# --- Collection --------------------------------------------------------------

def collect_skill(skill_dir: Path) -> SkillInfo:
    skill = SkillInfo(name=skill_dir.name, dir=skill_dir)
    for root, _, filenames in os.walk(skill_dir):
        for fname in filenames:
            fpath = Path(root) / fname
            if fpath.suffix not in SKILL_EXTENSIONS:
                continue
            size = fpath.stat().st_size
            skill.files.append(FileInfo(
                path=fpath.relative_to(skill_dir),
                abs_path=fpath,
                bytes=size,
                lines=count_lines(fpath),
                est_tokens=estimate_tokens(size),
            ))
    skill.files.sort(key=lambda f: (-f.is_entry_point, -f.bytes))
    return skill


def collect_all(skills_root: Path) -> list[SkillInfo]:
    skills = []
    for child in sorted(skills_root.iterdir()):
        if child.is_dir():
            skill = collect_skill(child)
            if skill.files:
                skills.append(skill)
    skills.sort(key=lambda s: -s.total_tokens)
    return skills


# --- Checks ------------------------------------------------------------------

def check_frontmatter(skill: SkillInfo):
    ep = skill.entry_point
    if not ep:
        skill.add("error", "frontmatter", "No SKILL.md found")
        return

    text = read_text(ep.abs_path)
    fm, _ = parse_frontmatter(text)
    skill.frontmatter = fm

    name = fm.get("name", "")
    desc = fm.get("description", "")

    if not name:
        skill.add("error", "frontmatter-name", "Missing 'name' in frontmatter")
    else:
        if len(name) > NAME_MAX_LEN:
            skill.add("error", "frontmatter-name",
                       f"name is {len(name)} chars (max {NAME_MAX_LEN})")
        if not NAME_PATTERN.match(name):
            skill.add("error", "frontmatter-name",
                       f"name '{name}' must be lowercase letters, numbers, hyphens only")
        for word in NAME_RESERVED:
            if word in name:
                skill.add("error", "frontmatter-name",
                           f"name contains reserved word '{word}'")

    if not desc:
        skill.add("error", "frontmatter-desc", "Missing 'description' in frontmatter")
    else:
        if len(desc) > DESC_MAX_LEN:
            skill.add("error", "frontmatter-desc",
                       f"description is {len(desc)} chars (max {DESC_MAX_LEN})")


def check_size(skill: SkillInfo):
    ep = skill.entry_point
    if not ep:
        return

    # Body lines (after frontmatter)
    text = read_text(ep.abs_path)
    _, body_start = parse_frontmatter(text)
    body_lines = ep.lines - body_start
    if body_lines > MAX_FILE_LINES:
        skill.add("warning", "size-body",
                   f"SKILL.md body is {body_lines} lines (recommended max {MAX_FILE_LINES})",
                   file="SKILL.md")

    # Reference file lines
    for f in skill.files:
        if f.is_entry_point:
            continue
        if f.lines > MAX_FILE_LINES:
            skill.add("warning", "size-lines",
                       f"{f.path} is {f.lines} lines (recommended max {MAX_FILE_LINES})",
                       file=str(f.path))

    # Entry point token budget
    pct = ep.est_tokens / CONTEXT_WINDOW_TOKENS
    if pct > THRESHOLDS["warning"]:
        skill.add("error", "size-entry",
                   f"SKILL.md is {fmt_tokens(ep.est_tokens)} tokens ({fmt_pct(ep.est_tokens)} of context)",
                   file="SKILL.md")
    elif pct > THRESHOLDS["acceptable"]:
        skill.add("warning", "size-entry",
                   f"SKILL.md is {fmt_tokens(ep.est_tokens)} tokens ({fmt_pct(ep.est_tokens)} of context)",
                   file="SKILL.md")

    # Total skill budget — warning only; supporting docs are lazy-loaded so
    # the full total rarely lands in a single context window.  When this
    # fires, verify the skill reads reference files on demand (e.g. per
    # phase or per subagent) rather than loading everything up front.
    total_pct = skill.total_tokens / CONTEXT_WINDOW_TOKENS
    if total_pct > THRESHOLDS["warning"]:
        skill.add("warning", "size-total",
                   f"Total skill is {fmt_tokens(skill.total_tokens)} tokens ({fmt_pct(skill.total_tokens)} of context)"
                   " — ensure reference files are loaded lazily, not all at once")


def check_reference_toc(skill: SkillInfo):
    """Reference files over 100 lines should have a ToC."""
    for f in skill.files:
        if f.is_entry_point or f.path.suffix != ".md":
            continue
        if f.lines <= REFERENCE_TOC_THRESHOLD:
            continue
        text = read_text(f.abs_path)
        # Heuristic: look for a "Contents" or "Table of Contents" heading,
        # or a cluster of markdown links near the top (first 30 lines).
        top = "\n".join(text.split("\n")[:30]).lower()
        has_toc = (
            "## contents" in top
            or "## table of contents" in top
            or "## toc" in top
            or top.count("](#") >= 3  # 3+ anchor links = likely a ToC
        )
        if not has_toc:
            skill.add("info", "reference-toc",
                       f"{f.path} is {f.lines} lines with no table of contents",
                       file=str(f.path))


def check_links(skill: SkillInfo):
    """Check that SKILL.md links point to existing files and are one level deep."""
    ep = skill.entry_point
    if not ep:
        return

    text = read_text(ep.abs_path)
    skill_file_set = {str(f.path) for f in skill.files}

    for match in MD_LINK.finditer(text):
        target = match.group(2)
        # Skip URLs, anchors, and parent-relative paths (cross-skill refs)
        if target.startswith(("http://", "https://", "#", "mailto:")):
            continue

        # Strip anchor fragment
        target_path = target.split("#")[0]
        if not target_path:
            continue

        # Check for backslash paths
        if "\\" in target_path:
            skill.add("warning", "link-backslash",
                       f"Backslash in link path: {target}",
                       file="SKILL.md")

        # Check existence (only for paths that don't go outside the skill dir)
        if target_path.startswith(".."):
            continue
        if target_path not in skill_file_set:
            skill.add("warning", "link-missing",
                       f"Link target not found: {target_path}",
                       file="SKILL.md")

    # Check for deep nesting: supporting docs should not reference other files
    for f in skill.files:
        if f.is_entry_point or f.path.suffix != ".md":
            continue
        ref_text = read_text(f.abs_path)
        for match in MD_LINK.finditer(ref_text):
            target = match.group(2)
            if target.startswith(("http://", "https://", "#", "mailto:")):
                continue
            target_path = target.split("#")[0]
            if not target_path or target_path.startswith(".."):
                continue
            # If a supporting doc links to another file in the skill, that's
            # a second level of reference — flag it.
            if target_path in skill_file_set:
                skill.add("info", "link-depth",
                           f"{f.path} references {target_path} (2 levels deep from SKILL.md)",
                           file=str(f.path))


def check_terminology(skill: SkillInfo):
    """Check for mixed terminology within a skill."""
    all_text = ""
    for f in skill.files:
        if f.path.suffix == ".md":
            all_text += read_text(f.abs_path).lower() + "\n"

    for group in TERM_GROUPS:
        found = {term for term in group if term in all_text}
        if len(found) > 1:
            skill.add("info", "terminology",
                       f"Mixed terms: {', '.join(sorted(found))}")


def run_all_checks(skill: SkillInfo):
    check_frontmatter(skill)
    check_size(skill)
    check_reference_toc(skill)
    check_links(skill)
    check_terminology(skill)


# --- Report ------------------------------------------------------------------

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
RED = "\033[31m"
YELLOW = "\033[33m"
GREEN = "\033[32m"
CYAN = "\033[36m"

RATING_STYLE = {
    "ok": GREEN,
    "acceptable": CYAN,
    "warning": YELLOW,
    "CRITICAL": RED,
}

LEVEL_STYLE = {
    "error": RED,
    "warning": YELLOW,
    "info": DIM,
}


def rate_lines(lines: int) -> str:
    if lines <= MAX_FILE_LINES:
        return "ok"
    return "warning"


def rate_tokens(tokens: int, cap_at_warning: bool = False) -> str:
    """Rate token count against context window budget.

    cap_at_warning: when True the rating never exceeds "warning".  Used for
    aggregate totals where reference files are lazy-loaded and unlikely to
    all occupy the context window simultaneously.
    """
    pct = tokens / CONTEXT_WINDOW_TOKENS
    if pct <= THRESHOLDS["comfortable"]:
        return "ok"
    if pct <= THRESHOLDS["acceptable"]:
        return "acceptable"
    if pct <= THRESHOLDS["warning"] or cap_at_warning:
        return "warning"
    return "CRITICAL"


def styled_rating(rating: str) -> str:
    color = RATING_STYLE.get(rating, "")
    return f"{color}{rating}{RESET}"


def styled_level(level: str) -> str:
    color = LEVEL_STYLE.get(level, "")
    return f"{color}{level}{RESET}"


def print_report(skills: list[SkillInfo]) -> dict:
    ctx_tok = fmt_tokens(CONTEXT_WINDOW_TOKENS)

    # --- Header ---
    print(f"\n{BOLD}Skill Quality Evaluation{RESET}")
    print(f"Context window: {ctx_tok} tokens  |  Token estimate: ~{CHARS_PER_TOKEN} chars/token")
    print(f"Rules: platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices")
    print()

    separator = "-" * 78
    errors = 0
    warnings = 0

    # --- Per-skill detail ---
    for skill in skills:
        ep_rating = rate_tokens(skill.entry_point_tokens)
        total_rating = rate_tokens(skill.total_tokens, cap_at_warning=True)

        print(separator)
        print(
            f"{BOLD}{skill.name}{RESET}"
            f"  |  entry: {fmt_tokens(skill.entry_point_tokens):>6} ({fmt_pct(skill.entry_point_tokens)}) "
            f"[{styled_rating(ep_rating)}]"
            f"  |  total: {fmt_tokens(skill.total_tokens):>6} ({fmt_pct(skill.total_tokens)}) "
            f"[{styled_rating(total_rating)}]"
        )

        for f in skill.files:
            marker = "*" if f.is_entry_point else " "
            if f.is_entry_point:
                text = read_text(f.abs_path)
                _, body_start = parse_frontmatter(text)
                line_count = f.lines - body_start
                line_label = "body lines"
            else:
                line_count = f.lines
                line_label = "     lines"
            line_rating = rate_lines(line_count)
            line_style = DIM if line_rating == "ok" else ""
            tok_rating = rate_tokens(f.est_tokens)
            tok_style = DIM if tok_rating == "ok" else ""
            print(
                f"  {marker} {str(f.path):<40} "
                f"{line_count:>5} {line_label} {line_style}[{styled_rating(line_rating)}]{RESET if line_style else ''}  "
                f"{fmt_tokens(f.est_tokens):>6} tok  "
                f"{tok_style}[{styled_rating(tok_rating)}]{RESET if tok_style else ''}"
            )

        for finding in skill.findings:
            loc = f" ({finding.file})" if finding.file else ""
            print(f"  {styled_level(finding.level):>18}  {finding.check}: {finding.message}{loc}")

        errors += sum(1 for f in skill.findings if f.level == "error")
        warnings += sum(1 for f in skill.findings if f.level == "warning")

    print(separator)
    print()

    # --- Summary ---
    total_tokens_all = sum(s.total_tokens for s in skills)
    total_findings = sum(len(s.findings) for s in skills)
    infos = total_findings - errors - warnings

    print(f"{BOLD}Summary{RESET}")
    print(f"  Skills:   {len(skills)}")
    print(f"  Tokens:   {fmt_tokens(total_tokens_all)} ({fmt_pct(total_tokens_all)} of context)")
    print(f"  Findings: {errors} errors, {warnings} warnings, {infos} info")
    print()

    print(f"  {BOLD}{'Skill':<20} {'Entry':>6}  {'Total':>6}  {'Total'}{RESET}")
    print(f"  {'':20} {'tokens':>6}  {'tokens':>6}  {'rating'}")
    for skill in skills:
        total_rating = rate_tokens(skill.total_tokens, cap_at_warning=True)
        print(
            f"    {skill.name:<20} {fmt_tokens(skill.entry_point_tokens):>6}  "
            f"{fmt_tokens(skill.total_tokens):>6}  [{styled_rating(total_rating)}]"
        )
    print()

    if errors:
        print(f"  {RED}{BOLD}FAIL{RESET}: {errors} error(s) found.")
    if warnings:
        print(f"  {YELLOW}{BOLD}WARN{RESET}: {warnings} warning(s) found.")
    if not errors and not warnings:
        print(f"  {GREEN}{BOLD}PASS{RESET}: All checks passed.")
    print()

    return {"errors": errors, "warnings": warnings}


# --- Main --------------------------------------------------------------------

def main() -> int:
    project_root = Path(__file__).resolve().parent.parent
    skills_root = project_root / "skills"

    if not skills_root.is_dir():
        print(f"Error: skills directory not found at {skills_root}", file=sys.stderr)
        return 1

    skills = collect_all(skills_root)
    if not skills:
        print("No skills found.", file=sys.stderr)
        return 1

    for skill in skills:
        run_all_checks(skill)

    result = print_report(skills)
    return 1 if result["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
