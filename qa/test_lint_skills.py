"""Tests for lint_skills.py checks."""

import textwrap
from pathlib import Path

import pytest

from lint_skills import (
    MAX_FILE_LINES,
    SkillInfo,
    check_frontmatter,
    check_links,
    check_reference_toc,
    check_size,
    check_terminology,
    collect_skill,
    estimate_tokens,
    parse_frontmatter,
    rate_lines,
    rate_tokens,
)


# --- Helpers -----------------------------------------------------------------

def make_skill(tmp_path, files: dict[str, str]) -> SkillInfo:
    """Create a skill directory with given files and collect it."""
    skill_dir = tmp_path / "test-skill"
    skill_dir.mkdir(exist_ok=True)
    for name, content in files.items():
        p = skill_dir / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)
    return collect_skill(skill_dir)


MINIMAL_FM = textwrap.dedent("""\
    ---
    name: test-skill
    description: A test skill
    ---
    """)


# --- Unit: pure functions ----------------------------------------------------

class TestEstimateTokens:
    def test_basic(self):
        assert estimate_tokens(400) == 100

    def test_zero(self):
        assert estimate_tokens(0) == 0


class TestParseFrontmatter:
    def test_valid(self):
        fm, body_start = parse_frontmatter("---\nname: foo\n---\nbody")
        assert fm["name"] == "foo"
        assert body_start == 3

    def test_no_frontmatter(self):
        fm, body_start = parse_frontmatter("just text")
        assert fm == {}
        assert body_start == 1

    def test_unclosed(self):
        fm, body_start = parse_frontmatter("---\nname: foo\nno closing")
        assert fm == {}
        assert body_start == 1


class TestRateLines:
    def test_at_limit(self):
        assert rate_lines(MAX_FILE_LINES) == "ok"

    def test_over_limit(self):
        assert rate_lines(MAX_FILE_LINES + 1) == "warning"


class TestRateTokens:
    def test_comfortable(self):
        assert rate_tokens(5_000) == "ok"

    def test_acceptable(self):
        assert rate_tokens(15_000) == "acceptable"

    def test_warning(self):
        assert rate_tokens(25_000) == "warning"

    def test_critical(self):
        assert rate_tokens(50_000) == "CRITICAL"

    def test_cap_at_warning(self):
        assert rate_tokens(50_000, cap_at_warning=True) == "warning"


# --- Integration: checks against temp skill dirs ----------------------------

class TestCheckFrontmatter:
    def test_valid(self, tmp_path):
        skill = make_skill(tmp_path, {"SKILL.md": MINIMAL_FM + "body\n"})
        check_frontmatter(skill)
        assert not any(f.level == "error" for f in skill.findings)

    def test_missing_name(self, tmp_path):
        content = "---\ndescription: hi\n---\nbody\n"
        skill = make_skill(tmp_path, {"SKILL.md": content})
        check_frontmatter(skill)
        assert any(f.check == "frontmatter-name" for f in skill.findings)

    def test_missing_description(self, tmp_path):
        content = "---\nname: test-skill\n---\nbody\n"
        skill = make_skill(tmp_path, {"SKILL.md": content})
        check_frontmatter(skill)
        assert any(f.check == "frontmatter-desc" for f in skill.findings)

    def test_invalid_name_format(self, tmp_path):
        content = "---\nname: Bad Name!\ndescription: hi\n---\nbody\n"
        skill = make_skill(tmp_path, {"SKILL.md": content})
        check_frontmatter(skill)
        errors = [f for f in skill.findings if f.check == "frontmatter-name"]
        assert any("lowercase" in f.message for f in errors)

    def test_reserved_word(self, tmp_path):
        content = "---\nname: my-claude-skill\ndescription: hi\n---\nbody\n"
        skill = make_skill(tmp_path, {"SKILL.md": content})
        check_frontmatter(skill)
        errors = [f for f in skill.findings if f.check == "frontmatter-name"]
        assert any("reserved" in f.message for f in errors)

    def test_no_skill_md(self, tmp_path):
        skill = make_skill(tmp_path, {"readme.md": "# hi\n"})
        check_frontmatter(skill)
        assert any(f.check == "frontmatter" and f.level == "error"
                   for f in skill.findings)


class TestCheckSize:
    def test_body_under_limit(self, tmp_path):
        body = "line\n" * (MAX_FILE_LINES - 10)
        skill = make_skill(tmp_path, {"SKILL.md": MINIMAL_FM + body})
        check_size(skill)
        assert not any(f.check == "size-body" for f in skill.findings)

    def test_body_over_limit(self, tmp_path):
        body = "line\n" * (MAX_FILE_LINES + 50)
        skill = make_skill(tmp_path, {"SKILL.md": MINIMAL_FM + body})
        check_size(skill)
        assert any(f.check == "size-body" and f.level == "warning"
                   for f in skill.findings)

    def test_reference_file_over_limit(self, tmp_path):
        body = "line\n" * 10
        ref = "line\n" * (MAX_FILE_LINES + 50)
        skill = make_skill(tmp_path, {
            "SKILL.md": MINIMAL_FM + body,
            "big-ref.md": ref,
        })
        check_size(skill)
        assert any(f.check == "size-lines" and "big-ref.md" in f.message
                   for f in skill.findings)

    def test_reference_file_under_limit(self, tmp_path):
        body = "line\n" * 10
        ref = "line\n" * (MAX_FILE_LINES - 10)
        skill = make_skill(tmp_path, {
            "SKILL.md": MINIMAL_FM + body,
            "small-ref.md": ref,
        })
        check_size(skill)
        assert not any(f.check == "size-lines" for f in skill.findings)

    def test_total_warning_not_critical(self, tmp_path):
        """Total skill rating should never exceed warning (lazy loading)."""
        # Create enough content to exceed the warning threshold
        big = "x" * 80 + "\n"  # ~80 bytes per line
        body = big * 100
        ref = big * 800
        skill = make_skill(tmp_path, {
            "SKILL.md": MINIMAL_FM + body,
            "huge-ref.md": ref,
        })
        check_size(skill)
        total_findings = [f for f in skill.findings if f.check == "size-total"]
        assert all(f.level == "warning" for f in total_findings)


class TestCheckReferenceToc:
    def test_short_file_no_toc_ok(self, tmp_path):
        skill = make_skill(tmp_path, {
            "SKILL.md": MINIMAL_FM + "body\n",
            "short.md": "line\n" * 50,
        })
        check_reference_toc(skill)
        assert not any(f.check == "reference-toc" for f in skill.findings)

    def test_long_file_no_toc_flagged(self, tmp_path):
        skill = make_skill(tmp_path, {
            "SKILL.md": MINIMAL_FM + "body\n",
            "long.md": "line\n" * 150,
        })
        check_reference_toc(skill)
        assert any(f.check == "reference-toc" and "long.md" in f.message
                   for f in skill.findings)

    def test_long_file_with_toc_ok(self, tmp_path):
        toc = "## Contents\n" + "- [Section](#section)\n" * 5
        body = "line\n" * 150
        skill = make_skill(tmp_path, {
            "SKILL.md": MINIMAL_FM + "body\n",
            "doc.md": toc + body,
        })
        check_reference_toc(skill)
        assert not any(f.check == "reference-toc" and "doc.md" in f.message
                       for f in skill.findings)


class TestCheckLinks:
    def test_valid_link(self, tmp_path):
        body = "[ref](ref.md)\n"
        skill = make_skill(tmp_path, {
            "SKILL.md": MINIMAL_FM + body,
            "ref.md": "content\n",
        })
        check_links(skill)
        assert not any(f.check == "link-missing" for f in skill.findings)

    def test_broken_link(self, tmp_path):
        body = "[ref](missing.md)\n"
        skill = make_skill(tmp_path, {
            "SKILL.md": MINIMAL_FM + body,
        })
        check_links(skill)
        assert any(f.check == "link-missing" and "missing.md" in f.message
                   for f in skill.findings)

    def test_backslash_path(self, tmp_path):
        body = "[ref](sub\\file.md)\n"
        skill = make_skill(tmp_path, {
            "SKILL.md": MINIMAL_FM + body,
        })
        check_links(skill)
        assert any(f.check == "link-backslash" for f in skill.findings)

    def test_external_links_ignored(self, tmp_path):
        body = "[site](https://example.com)\n[anchor](#top)\n"
        skill = make_skill(tmp_path, {
            "SKILL.md": MINIMAL_FM + body,
        })
        check_links(skill)
        assert not skill.findings

    def test_deep_nesting_flagged(self, tmp_path):
        body = "[ref](ref.md)\n"
        ref = "[other](other.md)\n"
        skill = make_skill(tmp_path, {
            "SKILL.md": MINIMAL_FM + body,
            "ref.md": ref,
            "other.md": "content\n",
        })
        check_links(skill)
        assert any(f.check == "link-depth" for f in skill.findings)


class TestCheckTerminology:
    def test_consistent_terms_ok(self, tmp_path):
        body = "Use the api endpoint for access.\n"
        skill = make_skill(tmp_path, {
            "SKILL.md": MINIMAL_FM + body,
        })
        check_terminology(skill)
        assert not any(f.check == "terminology" for f in skill.findings)

    def test_mixed_terms_flagged(self, tmp_path):
        body = "Use the api endpoint here.\nThe api route is different.\n"
        skill = make_skill(tmp_path, {
            "SKILL.md": MINIMAL_FM + body,
        })
        check_terminology(skill)
        assert any(f.check == "terminology" for f in skill.findings)


class TestCollectSkill:
    def test_ignores_non_skill_extensions(self, tmp_path):
        skill = make_skill(tmp_path, {
            "SKILL.md": MINIMAL_FM + "body\n",
            "image.png": "binary",
            "data.json": "{}",
        })
        extensions = {f.path.suffix for f in skill.files}
        assert ".png" not in extensions
        assert ".md" in extensions
        assert ".json" in extensions

    def test_entry_point_sorted_first(self, tmp_path):
        skill = make_skill(tmp_path, {
            "SKILL.md": MINIMAL_FM + "body\n",
            "zzz.md": "content\n",
        })
        assert skill.files[0].is_entry_point
