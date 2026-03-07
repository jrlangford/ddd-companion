# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

DDD Companion is a collection of Claude Code skills that form a pipeline: PRD extraction → bounded context modeling → Go code generation. This is **not** a traditional codebase — it is a set of skill definitions (structured markdown files) installed into `~/.claude/skills/`. Each skill's behavior is documented in its own SKILL.md; do not duplicate that here.

## Commands

```bash
just install    # Symlink all skills to ~/.claude/skills/
just uninstall  # Remove skill symlinks
just lint       # Lint skills against Anthropic best practices
just test       # Run QA tests
```

## Skill Anatomy

Each skill lives in `skills/{skill-name}/` and consists of:

- **`SKILL.md`** — Entry point. YAML frontmatter (`name`, `description`, optional `argument-hint`) followed by the skill's behavioral specification.
- **Supporting docs** — Referenced by SKILL.md and read at runtime (e.g., `fqbc-template.md`, `api-conventions.md`, `patterns/*.md`). Changes to these files directly affect skill behavior.

Skills are not code — they are structured prompts that Claude follows. There is no build step, but `qa/` contains linting and tests that check skill quality (see below).

## Repository Structure

```
skills/
├── ddd-extract-prd/       # SKILL.md + no supporting docs
├── ddd-prd/               # SKILL.md + schema.md, ddd-alignment.md, output-formats.md, scoping-criteria.md
├── ddd-model/             # SKILL.md + fqbc-template.md, context-mapping-patterns.md,
│                          #   api-conventions.md, manifest-schema.md, manifest.schema.json
├── ddd-implement/         # SKILL.md + generator-architecture.md, bcr-to-typespec.md, validate.md
│   ├── generators/golang/ #   generator.md + patterns/{domain,ports,application,adapters,mock,authorization,support}.md
│   └── manifest.schema.json
├── ddd-list/              # SKILL.md only
└── ddd-eval/              # SKILL.md only
justfile                   # Skill installation/removal
qa/                        # Skill linting and tests
local/                     # Local development workspace (not tracked)
```

## Key Design Decisions

- **Manifest-driven state**: `/ddd-model` and `/ddd-implement` persist progress in JSON manifest files, enabling multi-session workflows that survive context window limits
- **Subagent delegation**: `/ddd-implement` spawns subagents per bounded context to isolate context window usage
- **Generator abstraction**: Code generation patterns live under `generators/{language}/` — currently only `golang/` exists, but the structure supports adding new language generators
- **TypeSpec is documentation-only**: HTTP handlers are generated directly from FQBCs; TypeSpec produces OpenAPI specs as an additive artifact, not a handler dependency

## QA

`qa/lint_skills.py` (`just lint`) — Checks skills against [Anthropic's best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) and context window budget (200K tokens, Opus 4.6). Automated checks:

- **Size** — All files under 500 lines (body lines for SKILL.md, total for others), per-file and per-skill token estimates vs context window thresholds
- **Frontmatter** — `name` (max 64 chars, lowercase/numbers/hyphens, no reserved words) and `description` (non-empty, max 1024 chars)
- **References** — links in SKILL.md resolve to existing files, no backslash paths, no deeply nested references (max 1 level from SKILL.md)
- **Reference ToC** — files over 100 lines should have a table of contents
- **Terminology** — configurable term groups flag inconsistent synonyms

Exits non-zero on errors (frontmatter violations). Warnings flag size regressions and structural issues. Run after editing skills.

`qa/test_lint_skills.py` (`just test`) — pytest suite validating the linter's checks against temporary skill directories.

## Conventions for Editing Skills

- Supporting docs are the **single source of truth** for their concern (e.g., `api-conventions.md` for HTTP conventions, `patterns/domain.md` for domain layer code generation rules). Avoid restating rules across files.
- Some supporting docs are **cross-skill dependencies** — editing them affects multiple skills. Known cross-skill files: `ddd-model/api-conventions.md` (consumed by both `ddd-model` FQBC generation and `ddd-implement` HTTP handler generation)
- Generator pattern files (`patterns/*.md`) define exact code generation rules per architectural layer — when changing generated output structure, update the relevant pattern file
- Output artifacts (PRDs, BCR docs, FQBCs) use Markdown with Mermaid diagrams, optimized for Obsidian rendering
- The `justfile` `skills` variable must be updated when adding or removing skills

### Responding to Size Warnings

`just lint` flags files that exceed line or token thresholds. When reducing file size, **preserve all behavioral information** — the goal is to make skills smaller without making them less capable. Follow these rules:

- **Split, don't delete.** Extract sections into new supporting docs and replace them with a reference link. Every rule, example, or constraint in the original must appear in exactly one file after the split.
- **Compress prose, not rules.** Tighten wording, remove filler, and deduplicate — but do not drop decision rules, edge-case handling, constraints, or examples that illustrate non-obvious behavior.
- **Preserve examples that earn their bytes.** If an example clarifies a rule that would be ambiguous without it, keep it. Only remove examples that are redundant with another example or that restate what the prose already makes obvious.
- **Audit after splitting.** After any split, verify that (1) every rule from the original still exists in exactly one file, (2) SKILL.md links to the new file, and (3) `just lint` passes with no new link-missing warnings.
