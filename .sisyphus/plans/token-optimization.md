## Plan Generated: Token-Optimization

**Key Decisions**: 
- [Decision] Concise prompts improve token efficiency: keep intent to 1 sentence, use bullets for specifics.
- [Decision] Use plan/docs as primary memory: summarize long context in plan rather than re-sending.
- [Decision] Delegate heavy exploration to explore/librarian only when necessary; otherwise minimize.

**Scope**: IN: Planning-only improvements to conversation flow; OUT: Any code changes or runtime changes.

**Guardrails** (from Metis): Avoid plan creep; ensure every task has explicit acceptance criteria; keep changes in .sisyphus only.

**Auto-Resolved**: 
- [Defaults Applied] If user asks for more detail, propose adding it to plan document rather than expanding prompt.

**Defaults Applied**: 
- Use 2-4 bullet points in responses when summarizing research; no long verbatim prompts.

**Decisions Needed**: None at this moment. If user wants tighter control, adjust cap.

## TL;DR
Minimize token usage by shifting narrative into plan docs, using concise prompts, and limiting live exploration.

## Context
### Original Request
User asked: [Portuguese] "como otimizar o consumo de tokens aqui?"
### Interview Summary
User seeks actionable, repeatable approach; no constraints on time or resources were given.
### Metis Review (gaps addressed)
N/A at this stage.

## Work Objectives
### Core Objective
Reduce tokens per interaction while maintaining decision quality.
### Deliverables
- A documented prompt convention for all interactions.
- A plan to store context summaries in .sisyphus/plans.
- A template for incremental plan writing to avoid large one-shot outputs.
### Definition of Done (verifiable)
- Token usage per interaction reduced by at least 30% within 2 weeks of adoption.
- All plans include explicit references and acceptance criteria.
- No new plan exceeds a single skeleton plus two edits at a time.
### Must Have
- Concise intent prompts
- Plan-based memory
- Documentation of references
### Must NOT Have
- Rewriting large histories in every prompt.
- Deviations from the plan format.

## Verification Strategy
- Test decision: Use 2 sample conversations; compare token counts with and without plan-based summarization.
- QA policy: All prompts documented with references; tests on token counts.
- Evidence: .sisyphus/evidence/token-optimization-demo.md

## Execution Strategy
### Parallel Execution Waves
- Wave 1: Establish prompt templates; update drafts and plan skeleton.
- Wave 2: Implement plan-writing procedure; start using skeleton+edits.

### Dependency Matrix
- Plan Templates -> Drafts + Plans
### Agent Dispatch Summary
- 4 tasks: Draft creation, Plan skeleton, Wave tasks, QA check

## TODOs
- [ ] Create final skeleton for token-optimization plan.
- [ ] Implement incremental write protocol: skeleton + 2-4 edits per batch.
- [ ] Add QA scenarios: happy path and edge-case.
- [ ] Create evidence artifacts and references.
- [ ] Run Momus review for final acceptance (if high-accuracy required).

## Final Verification Wave
- F1 Plan Compliance Audit — oracle
- F2 Code Quality Review — none
- F3 Real Manual QA — not applicable
- F4 Scope Fidelity Check — deep

## Commit Strategy
- Commit plan artifacts to .sisyphus/plans/token-optimization.md

## Success Criteria
- Token usage reduced by target threshold; plan includes explicit acceptance criteria; plan is ready for execution.
