---
name: GSD Phase Execution Workflow Preferences
description: Diego's preferred execution mode for multi-plan phases using /gsd orchestrator
type: feedback
---

**Rule:** For multi-plan phases (3+ plans, 2+ waves), use **Wave 1 Checkpoint Mode** by default unless explicitly asked otherwise.

**Why:** During Phase 2 execution (2026-03-27), Diego chose checkpoint mode over "full phase execution" when asked. This showed that:
- Feedback loops between waves are valuable (verify Wave 1 results before Wave 2)
- Prevents context explosion (each wave handled fresh, not loading full phase at once)
- Checkpoints provide clear stopping points if issues emerge
- Allows parallel execution within a wave while respecting dependencies between waves

**How to apply:**

1. **For /gsd:plan-phase:** Auto-mode works well (`--auto` flag)
   - Creates comprehensive PLAN.md with task breakdown
   - No interactive questions needed
   - Use technical depth + parallel patterns in auto-decisions

2. **For /gsd:execute-phase with multi-wave plans:**
   - Ask: "Wave 1 Checkpoint (pause after Wave 1 completion for verification) or Full Phase (execute all waves sequentially)?"
   - Recommend: Wave 1 Checkpoint by default
   - If user chooses checkpoint: stop after Wave 1 completes, show summary, let user verify before continuing
   - If user chooses full: execute all waves sequentially without pause

3. **For /ship after phase complete:**
   - Run full automated workflow (no interactive prompts)
   - Auto-decide version bump (PATCH for <200 lines, ask user for MINOR/MAJOR)
   - Auto-generate CHANGELOG from diff
   - Auto-update TODOS.md
   - Create PR with comprehensive body (test coverage, review findings, verification results)

**Example pattern (from Phase 2, 2026-03-27):**
```
/gsd:plan-phase 2 --auto                              → Creates PLAN.md
/gsd:execute-phase 2-full-data-pipeline               → Asks for execution mode
                                                       → User chooses Wave 1 Checkpoint
                                                       → Execute 02-01 + 02-02 (parallel)
                                                       → Show WAVE-1-CHECKPOINT.md
                                                       → [pause for user verification]
/gsd:execute-phase 02-full-data-pipeline --auto       → Resume with --auto flag
                                                       → Execute Wave 2 (02-03/04/05 parallel)
                                                       → Complete phase verification
/ship                                                  → Fully automated PR creation
                                                       → Version bump, CHANGELOG, PR link
```

**When to deviate:**
- User explicitly says "full phase", "no checkpoints", "do it all at once" → execute all waves sequentially
- Phase is small (1-2 plans total) → full execution is fine, no need to checkpoint
- User is under time pressure → checkpoint mode actually saves time (faster feedback = fewer iterations)

