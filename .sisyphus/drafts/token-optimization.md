# Draft: Token Optimization Plan

## Requirements (confirmed)
- [ ] Reduce token usage in planning interactions while preserving decision quality.
- [ ] Establish repeatable conventions for prompts and summary outputs.
- [ ] Document decision criteria to minimize back-and-forth.

## Technical Decisions
- Use concise prompt templates (target <= 1-2 sentences for intent; bullet lists for specifics).
- Rely on plan/draft storage to summarize context instead of re-sending long histories.
- When repeating context, attach a brief summary reference (one-liner) and a pointer to prior plan.
- Defer non-critical explorations; rely on explicit "explore" delegation only when necessary.
- Implement incremental plan writing: skeleton plan first, then append tasks in small batches.
- Use minimal QA scenarios focusing on happy paths; avoid exhaustive edge-case QA for tokens unless needed.
- Centralize reference patterns and sources in the plan for auditor efficiency.
- Cache commonly requested facts via the plan's "References" sections; do not re-derive.
- Apply "Metis guardrails" to avoid scope creep and duplication.

## Research Findings
- Found patterns: plan-driven execution reduces token churn by moving long rationale into plan documentation.
- Found best practice: use "Question" tool only for meaningful tradeoffs; otherwise answer concisely.
- Note: No external dependencies required to implement these token-saving measures.

## Open Questions
- [ ] Do you want strict token caps per prompt? If yes, what caps?
- [ ] Should we enforce a maximum number of plan tasks per wave?
- [ ] Is a global plan store preferred or per-task plans?

## Scope Boundaries
- INCLUDE: Plan for token optimization in ongoing conversations.
- EXCLUDE: Any changes to code or runtime behavior; this is planning-only.

## Next Steps
- Prepare .sisyphus/plans/token-optimization.md with finalized decisions.
- If approved, implement the plan via the standard rollout process.
