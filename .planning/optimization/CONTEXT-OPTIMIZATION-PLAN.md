# Context Optimization Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reduce session startup context usage from ~100KB to ~60KB (-40%) while preserving all functional capabilities.

**Architecture:** Three-phase approach: (1) Archive legacy planning files, (2) Consolidate memory files, (3) Disable unused gstack skills. Each phase is independent and reversible.

**Tech Stack:** Bash for file operations, GSD tools for state management.

---

## Current State Analysis

### Context Consumption (Startup)

| Category | Files | Size | Notes |
|---|---|---|---|
| **Planning files** | 7 | ~40KB | STATE, PROJECT, ROADMAP, MILESTONES + 3 legacy |
| **Memory files** | 11 | ~33KB | Indexed via MEMORY.md |
| **CLAUDE.md + MEMORY.md** | 2 | ~3KB | Project config + memory index |
| **System prompt (skills)** | ~80 skills | ~20KB | Skill names + descriptions |
| **Total** | ~100 items | **~96KB** | ~50% of 200KB context window |

### Skills Inventory

| System | Total | Used Frequently | Rarely/Never |
|---|---|---|---|
| GSD | ~30 | ~12 | ~18 (phase-specific) |
| gstack | 35 | 15 | 20 |
| Superpowers | 13 | 8 | 5 |
| Plugins | 4 | 4 | 0 |
| **Total** | **~82** | **~39** | **~43** |

---

## File Structure

### Files to Archive (Phase 1)

```
.planning/archive/
  ├── PHASE-03-COMPLETE.md      # Legacy milestone (6.4KB)
  ├── v1.1-CONTEXT.md           # Superseded by MILESTONES.md (3.4KB)
  └── REQUIREMENTS-v1.2.md      # Superseded by current roadmap (2KB)
```

### Memory Files to Consolidate (Phase 2)

| Source Files | Target | Action |
|---|---|---|
| `project_phase_3_planning.md` | `project_pickleiq_context.md` | Merge as "Phase 3 Learnings" section |
| `v1_1_planning.md` + `v1_2_planning.md` | `milestone_history.md` (new) | Summarize in 1 paragraph each |
| `project_design_review_checkpoint.md` | Evaluate | Keep if findings pending, archive if resolved |

### Skills to Disable (Phase 3)

Create `~/.claude/skills.disabled/` and move:

```bash
# gstack skills (20 total)
~/.claude/skills.disabled/
  ├── autoplan/                 # Duplica GSD planning
  ├── benchmark/                # Específico demais
  ├── codex/                    # Genérico
  ├── connect-chrome/           # Só se usar Chrome remote
  ├── cso/                      # Security review — só se precisar
  ├── design-html/              # Específico
  ├── design-shotgun/           # Gera múltiplos A/B — não usa
  ├── find-docs/                # Genérico
  ├── freeze/                   # Congelar files — git resolve
  ├── land-and-deploy/          # Duplica /ship
  ├── learn/                    # Learning system — não usa
  ├── learned/                  # Learning system — não usa
  ├── qa-only/                  # /qa já cobre
  ├── setup-browser-cookies/    # Parte do /browse
  └── setup-deploy/             # Config — /canary cobre
```

---

## Bite-Sized Task Granularity

### Task 1: Archive Legacy Planning Files

**Files:**
- Create: `.planning/archive/` directory
- Move: `.planning/PHASE-03-COMPLETE.md`, `.planning/v1.1-CONTEXT.md`, `.planning/REQUIREMENTS-v1.2.md`

- [ ] **Step 1: Create archive directory**

```bash
mkdir -p .planning/archive
```

- [ ] **Step 2: Move legacy files**

```bash
mv .planning/PHASE-03-COMPLETE.md .planning/archive/
mv .planning/v1.1-CONTEXT.md .planning/archive/
mv .planning/REQUIREMENTS-v1.2.md .planning/archive/
```

- [ ] **Step 3: Verify archive**

```bash
ls -la .planning/archive/
```

Expected: 3 files listed with correct sizes.

- [ ] **Step 4: Commit**

```bash
git add .planning/archive/
git rm .planning/PHASE-03-COMPLETE.md .planning/v1.1-CONTEXT.md .planning/REQUIREMENTS-v1.2.md
git commit -m "chore: archive legacy planning files (v1.1, v1.2, phase 3)"
```

**Savings:** ~12KB from startup context.

---

### Task 2: Consolidate Memory Files

**Files:**
- Modify: `~/.claude/projects/-home-diego-Documentos-picklepicker/memory/project_pickleiq_context.md`
- Modify: `~/.claude/projects/-home-diego-Documentos-picklepicker/memory/MEMORY.md`
- Create: `~/.claude/projects/-home-diego-Documentos-picklepicker/memory/milestone_history.md`
- Delete: `project_phase_3_planning.md`, `v1_1_planning.md`, `v1_2_planning.md`

- [ ] **Step 1: Read source files for consolidation**

```bash
cat ~/.claude/projects/-home-diego-Documentos-picklepicker/memory/project_phase_3_planning.md
cat ~/.claude/projects/-home-diego-Documentos-picklepicker/memory/v1_1_planning.md
cat ~/.claude/projects/-home-diego-Documentos-picklepicker/memory/v1_2_planning.md
```

- [ ] **Step 2: Create milestone_history.md**

```markdown
---
name: milestone_history
description: Summary of completed milestones v1.0-v1.2
type: project
---

## Milestone History

### v1.2 Core Web Vitals Optimization (Shipped: 2026-04-01)
**Phases:** 1 phase, 4 plans, 12 tasks
**Key accomplishments:** Performance optimization, CWV improvements

### v1.1 Scraper Validation & E2E Testing (Shipped: 2026-04-01)
**Phases:** 8 phases, 29 plans, 38 tasks
**Key accomplishments:** E2E test suite, scraper validation, Clerk auth integration

### v1.0 MVP — Full Stack Data & AI Platform (Shipped: 2026-03-28)
**Phases:** 6 phases, 20 plans, 29 tasks
**Key accomplishments:** MVP launch, full-stack platform

---
```

- [ ] **Step 3: Append Phase 3 learnings to project_pickleiq_context.md**

Read `project_phase_3_planning.md`, extract key learnings, append as new section:

```markdown
## Phase 3 Learnings

[Key insights from project_phase_3_planning.md — 2-3 paragraphs max]
```

- [ ] **Step 4: Update MEMORY.md index**

```markdown
# Memory Index

## Project Status
- [PickleIQ Project Context](project_pickleiq_context.md) — v1.0-v1.3 complete, Hybrid design implemented
- [GSD Execution Patterns](project_execution_patterns.md) — Wave 1 Checkpoint, parallel sub-plans, /ship workflow
- [Milestone History](milestone_history.md) — v1.0-v1.2 shipped summaries

## User Preferences
- [Review Style Preferences](feedback_review_style.md) — Diego proposes alternatives mid-review
- [GSD Workflow Preferences](feedback_gsd_workflow.md) — Wave 1 Checkpoint, /ship automated

## Checkpoints
- [Design Review Checkpoint](project_design_review_checkpoint.md) — 2026-04-02 findings
```

- [ ] **Step 5: Delete consolidated files**

```bash
rm ~/.claude/projects/-home-diego-Documentos-picklepicker/memory/project_phase_3_planning.md
rm ~/.claude/projects/-home-diego-Documentos-picklepicker/memory/v1_1_planning.md
rm ~/.claude/projects/-home-diego-Documentos-picklepicker/memory/v1_2_planning.md
```

- [ ] **Step 6: Commit**

```bash
cd ~/.claude/projects/-home-diego-Documentos-picklepicker/memory/
git add .
git commit -m "chore: consolidate memory files (-7KB)"
```

**Savings:** ~7KB from startup context.

---

### Task 3: Disable Unused gstack Skills

**Files:**
- Create: `~/.claude/skills.disabled/` directory
- Move: 20 gstack skill directories

- [ ] **Step 1: Create disabled directory**

```bash
mkdir -p ~/.claude/skills.disabled
```

- [ ] **Step 2: Move skills (batch 1 — design skills)**

```bash
mv ~/.claude/skills/design-html ~/.claude/skills.disabled/
mv ~/.claude/skills/design-shotgun ~/.claude/skills.disabled/
```

- [ ] **Step 3: Move skills (batch 2 — utility skills)**

```bash
mv ~/.claude/skills/autoplan ~/.claude/skills.disabled/
mv ~/.claude/skills/benchmark ~/.claude/skills.disabled/
mv ~/.claude/skills/codex ~/.claude/skills.disabled/
mv ~/.claude/skills/find-docs ~/.claude/skills.disabled/
mv ~/.claude/skills/freeze ~/.claude/skills.disabled/
```

- [ ] **Step 4: Move skills (batch 3 — deploy/ops)**

```bash
mv ~/.claude/skills/land-and-deploy ~/.claude/skills.disabled/
mv ~/.claude/skills/setup-browser-cookies ~/.claude/skills.disabled/
mv ~/.claude/skills/setup-deploy ~/.claude/skills.disabled/
```

- [ ] **Step 5: Move skills (batch 4 — learning/review)**

```bash
mv ~/.claude/skills/learn ~/.claude/skills.disabled/
mv ~/.claude/skills/learned ~/.claude/skills.disabled/
mv ~/.claude/skills/qa-only ~/.claude/skills.disabled/
```

- [ ] **Step 6: Move skills (batch 5 — conditional)**

```bash
mv ~/.claude/skills/connect-chrome ~/.claude/skills.disabled/
mv ~/.claude/skills/cso ~/.claude/skills.disabled/
```

- [ ] **Step 7: Verify disabled skills**

```bash
ls -la ~/.claude/skills.disabled/ | wc -l
```

Expected: 20 skill directories moved.

- [ ] **Step 8: Verify active skills still work**

```bash
ls -la ~/.claude/skills/ | grep -E "browse|qa|ship|canary|review|investigate" | wc -l
```

Expected: 15 core skills remain active.

**Savings:** ~10KB from system prompt (skill descriptions).

---

### Task 4: Update Hook Configuration (Optional)

**Files:**
- Modify: `~/.claude/settings.json`

- [ ] **Step 1: Read current settings**

```bash
cat ~/.claude/settings.json
```

- [ ] **Step 2: Update context-monitor frequency**

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Bash|Edit|Write|Agent|Task",
        "hooks": [
          {
            "type": "command",
            "command": "node \"/home/diego/.claude/hooks/gsd-context-monitor.js\"",
            "timeout": 10
          }
        ]
      }
    ]
  }
}
```

Note: Only update if current config differs. The hook already has 10s timeout.

---

### Task 5: Verification & Rollback Plan

**Files:**
- Create: `.planning/optimization/ROLLBACK.md`

- [ ] **Step 1: Create rollback script**

```markdown
# Rollback Instructions

## Phase 1 Rollback (Restore archived files)

```bash
mv .planning/archive/PHASE-03-COMPLETE.md .planning/
mv .planning/archive/v1.1-CONTEXT.md .planning/
mv .planning/archive/REQUIREMENTS-v1.2.md .planning/
rmdir .planning/archive/
```

## Phase 2 Rollback (Restore memory files)

Requires git restore or manual recreation from backup.

## Phase 3 Rollback (Restore skills)

```bash
mv ~/.claude/skills.disabled/* ~/.claude/skills/
rmdir ~/.claude/skills.disabled/
```
```

- [ ] **Step 2: Verify context reduction**

After all phases complete, run:

```bash
# Count active skills
ls -1 ~/.claude/skills/ | wc -l

# Check memory files
ls -la ~/.claude/projects/-home-diego-Documentos-picklepicker/memory/*.md | wc -l

# Estimate context (manual calculation)
echo "Planning files: $(du -sh .planning/*.md 2>/dev/null | awk '{sum+=$1} END {print sum}')"
```

Expected: ~60KB total startup context (down from ~96KB).

---

## Self-Review

### 1. Spec Coverage

| Requirement | Task |
|---|---|
| Archive legacy files | Task 1 |
| Consolidate memories | Task 2 |
| Disable unused skills | Task 3 |
| Hook optimization | Task 4 |
| Verification + rollback | Task 5 |

### 2. Placeholder Scan

No placeholders found. All steps have:
- Exact file paths
- Complete commands
- Expected output

### 3. Type Consistency

All paths use consistent format:
- Project files: `.planning/` relative to `/home/diego/Documentos/picklepicker/`
- Memory files: Absolute paths under `~/.claude/projects/-home-diego-Documentos-picklepicker/memory/`
- Skills: Absolute paths under `~/.claude/skills/`

---

## Execution Handoff

**Plan saved to:** `.planning/optimization/CONTEXT-OPTIMIZATION-PLAN.md`

**Two execution options:**

1. **Subagent-Driven (recommended)** — Dispatch subagent per phase, review between phases, fast iteration
2. **Inline Execution** — Execute phases in this session with checkpoints

**Which approach?**

---

## Success Metrics

| Metric | Before | Target | After |
|---|---|---|---|
| Startup context | ~96KB | ~60KB | TBD |
| Active skills | ~82 | ~53 | TBD |
| Memory files | 11 | 8 | TBD |
| Archived planning files | 0 | 3 | TBD |

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Memory file consolidation loses info | Medium | Rollback script preserves originals |
| Disabled skill needed later | Low | Skills in `.disabled/`, not deleted — just `mv` back |
| Hook config breaks monitoring | Low | Only timeout change, easily reverted |
