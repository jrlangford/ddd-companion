# Session Management

This document covers multi-session workflow design, subagent delegation, session resumption/stop protocols, and error recovery for the ddd-implement skill.

## Multi-Session Design

This workflow is designed to span multiple sessions. Context window limits will be reached during generation of complex systems.

### Core Principles

1. **Manifest is the source of truth** - All progress is tracked in `ddd-workspace/ddd-implement.manifest.json`
2. **One context at a time** - Process each bounded context completely before moving to the next
3. **Subagents for isolation** - Use Task tool subagents for each context to manage memory
4. **Checkpoint after each operation** - Update manifest immediately after completing any unit of work
5. **File-level tracking** - Track individual files created, not just phases

### Context Window Management Strategies

**Strategy 1: Subagent per Context (Recommended)**
```
Main Agent:
  1. Read manifest, identify next context to process
  2. Spawn subagent for that context with focused prompt
  3. Subagent generates all layers for ONE context
  4. Subagent updates manifest with files created
  5. Main agent verifies, moves to next context
```

**Strategy 2: Subagent per Phase**
```
Main Agent:
  1. For each phase (domain, ports, application, adapters):
     - Spawn subagent with phase-specific prompt
     - Subagent processes ALL contexts for that phase
     - Subagent updates manifest
```

**Strategy 3: Checkpoint and Clear**
```
After completing each context:
  1. Update manifest with all file paths created
  2. Run `go build ./...` to verify
  3. Summarize progress to user
  4. User can continue in new session if needed
```

### Subagent Prompts

When spawning a subagent for a context, provide:
```
Generate [PHASE] for context [CONTEXT_NAME]:

Manifest location: ./ddd-workspace/ddd-implement.manifest.json
Context definition: [paste relevant context object from manifest]
Generator patterns: Read these files for code generation rules:
  - generators/golang/patterns/domain.md
  - generators/golang/patterns/ports.md
  - generators/golang/patterns/application.md
  - generators/golang/patterns/adapters.md
  - generators/golang/patterns/mock.md
  - generators/golang/patterns/authorization.md
  - generators/golang/patterns/support.md
  (Include only patterns relevant to [PHASE])

Requirements:
1. Generate files for this context only
2. Update manifest.contexts[N].phases.[phase] = "complete"
3. Update manifest.contexts[N].generatedFiles.[phase] = [list of files]
4. Run `go build ./...` after generation
5. Report any errors encountered

Do NOT read other context directories.
Do NOT modify files outside this context.
```

---

## Session Resumption Protocol

When starting or resuming work:

### Step 1: Read and Analyze Manifest
```
1. Read ddd-workspace/ddd-implement.manifest.json
2. Check currentPhase and currentContext
3. For each context, check status and phases
4. Identify the FIRST incomplete item
```

### Step 2: Determine Next Action

| State | Action |
|-------|--------|
| No manifest | Create manifest, parse BCR workspace |
| `infrastructure.support.status = pending` | Generate support packages |
| Context with `status = in_progress` | Resume that context from incomplete phase |
| Context with `status = pending` | Start that context |
| All contexts complete, `apiContracts.status = pending` | Generate TypeSpec contracts |
| API contracts complete, `drivingAdapters.http.status = pending` | Generate HTTP adapters |
| Driving adapters complete, `mainWiring.status = pending` | Generate main wiring |
| Main wiring complete, validation pending | Run validation |

### Step 3: Execute with Checkpointing

After EACH file or small group of files:
1. Update `generatedFiles` array in manifest
2. If completing a phase, update phase status
3. If completing a context, update context status and `history`

### Step 4: Verify Before Proceeding
```bash
go build ./...
```
If build fails, record error in manifest and stop.

---

## Session Stop Protocol

When context window is approaching capacity or you need to end a session, follow this protocol for a clean handoff.

### When to Stop

Stop at the nearest natural boundary:

| Current Work | Natural Stopping Point |
|-------------|----------------------|
| Phase 3 (Contexts) | After completing any full context (all layers: domain → ports → application → adapters → mock) |
| Phase 4 (HTTP Handlers) | After completing all handlers for one context |
| Phase 5 (TypeSpec) | After completing TypeSpec for one context |
| Phase 6 (Main Wiring) | After `main.go` is written and builds |
| Phase 7 (Validation) | After build/test results are recorded |

**Do not stop mid-layer** (e.g., domain generated but ports not started). Complete the current context's layer set or roll back to the last checkpoint.

### Before Stopping

1. **Update the manifest** — ensure all completed work is reflected in `generatedFiles`, phase statuses, and context statuses
2. **Run `go build ./...`** — verify the codebase compiles; record result in manifest
3. **Set `currentContext` to null** if the current context is fully complete; leave it set if mid-context (the resumption protocol will pick it up)

### What to Report

Provide the user with a handoff summary:

```markdown
**Session Complete**

**Progress**: [N]/[Total] contexts generated | Phase [current] | [files created] files
**Build status**: [pass/fail]
**Next step**: [what the next session should do first]

To resume: re-invoke `/ddd-implement` — the manifest tracks all progress.
```

---

## Error Recovery

### Build Failure During Context Generation

```json
{
  "contexts": [{
    "name": "role-management",
    "status": "error",
    "errors": [
      {
        "phase": "application",
        "file": "internal/rolemanagement/rolemanagementapplication/service.go",
        "error": "undefined: PersonId",
        "timestamp": "2024-01-20T10:30:00Z"
      }
    ]
  }]
}
```

**Recovery**:
1. Read the error from manifest
2. Fix the specific file
3. Re-run build
4. If successful, clear error and continue

### Session Interrupted Mid-Context

The manifest shows exactly where we stopped:
- `currentContext` indicates which context
- `phases` shows which phases are complete
- `generatedFiles` shows exactly what files exist

Resume by checking which phase is incomplete and continuing from there.
