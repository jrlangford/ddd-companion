# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

DDD Companion is a collection of Claude Code skills that form a pipeline: PRD extraction → bounded context modeling → Go code generation. This is **not** a traditional codebase — it is a set of skill definitions (structured markdown files) installed into `~/.claude/skills/`. Each skill's behavior is documented in its own SKILL.md; do not duplicate that here.

## Commands

```bash
just install    # Symlink all skills to ~/.claude/skills/
just uninstall  # Remove skill symlinks
```

## Skill Anatomy

Each skill lives in `skills/{skill-name}/` and consists of:

- **`SKILL.md`** — Entry point. YAML frontmatter (`name`, `description`, `disable-model-invocation: true`, optional `argument-hint`) followed by the skill's behavioral specification.
- **Supporting docs** — Referenced by SKILL.md and read at runtime (e.g., `fqbc-template.md`, `api-conventions.md`, `patterns/*.md`). Changes to these files directly affect skill behavior.

Skills are not code — they are structured prompts that Claude follows. There is no build step, linting, or test suite for the skills themselves.

## Repository Structure

```
skills/
├── ddd-extract-prd/       # SKILL.md + no supporting docs
├── ddd-prd/               # SKILL.md + schema.md, ddd-alignment.md, output-formats.md, poc-scoping.md
├── ddd-model/             # SKILL.md + fqbc-template.md, context-mapping-patterns.md,
│                          #   api-conventions.md, manifest-schema.md
├── ddd-implement/         # SKILL.md + generator-architecture.md, bcr-to-typespec.md, validate.md
│   ├── generators/golang/ #   generator.md + patterns/{domain,ports,application,adapters,mock,authorization}.md
│   └── manifest.schema.json
├── ddd-list/              # SKILL.md only
└── ddd-eval/              # SKILL.md only
justfile                   # Skill installation/removal
local/                     # Local development workspace (not tracked)
```

## Key Design Decisions

- **Manifest-driven state**: `/ddd-model` and `/ddd-implement` persist progress in JSON manifest files, enabling multi-session workflows that survive context window limits
- **Subagent delegation**: `/ddd-implement` spawns subagents per bounded context to isolate context window usage
- **Generator abstraction**: Code generation patterns live under `generators/{language}/` — currently only `golang/` exists, but the structure supports adding new language generators
- **TypeSpec is documentation-only**: HTTP handlers are generated directly from FQBCs; TypeSpec produces OpenAPI specs as an additive artifact, not a handler dependency

## Conventions for Editing Skills

- All skills set `disable-model-invocation: true` — they are user-invoked only
- Supporting docs are the **single source of truth** for their concern (e.g., `api-conventions.md` for HTTP conventions, `patterns/domain.md` for domain layer code generation rules). Avoid restating rules across files.
- Generator pattern files (`patterns/*.md`) define exact code generation rules per architectural layer — when changing generated output structure, update the relevant pattern file
- Output artifacts (PRDs, BCR docs, FQBCs) use Markdown with Mermaid diagrams, optimized for Obsidian rendering
- The `justfile` `skills` variable must be updated when adding or removing skills
