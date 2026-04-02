# Claude Code Configuration

## gstack

Use the `/browse` skill from gstack for all web browsing. Never use `mcp__claude-in-chrome__*` tools.

**Available gstack skills:**
- `/office-hours` — Q&A and guidance from gstack team
- `/plan-ceo-review` — CEO-level review and stakeholder alignment
- `/plan-eng-review` — Engineering review for technical decisions
- `/plan-design-review` — Design review for UI/UX validation
- `/design-consultation` — Design consultation for frontend work
- `/review` — General review and feedback
- `/ship` — Ship PR and merge process
- `/land-and-deploy` — Landing and deployment management
- `/canary` — Canary deployment and rollout
- `/benchmark` — Performance benchmarking
- `/browse` — Fast headless browser for QA, testing, and site dogfooding
- `/qa` — Full QA testing workflow
- `/qa-only` — QA testing only (no deployment)
- `/design-review` — Detailed design review
- `/setup-browser-cookies` — Configure browser cookies for testing
- `/setup-deploy` — Set up deployment configuration
- `/retro` — Retrospective and post-mortem
- `/investigate` — Investigation and debugging
- `/document-release` — Release documentation
- `/codex` — Codebase knowledge and generation
- `/cso` — Chief Security Officer review
- `/autoplan` — Automatic planning
- `/careful` — Careful/safe execution mode
- `/freeze` — Freeze changes
- `/guard` — Guard and protect
- `/unfreeze` — Unfreeze changes
- `/gstack-upgrade` — Update gstack to latest version

## Design System

Always read DESIGN.md before making any visual or UI decisions.
All font choices, colors, spacing, and aesthetic direction are defined there.
Do not deviate without explicit user approval.
In QA mode, flag any code that doesn't match DESIGN.md.

**Key decisions (DESIGN.md v2.0):**
- Hybrid Modern Sports Tech aesthetic (sport energy + data credibility)
- Lime (#84CC16) on dark backgrounds only — never on white
- Green (#76b900) for data elements: charts, tables, section labels
- JetBrains Mono for specs/tables — signals "we take data seriously"
- 2px border radius everywhere — sharp corners = precision
- Alternating dark/light sections
- Section labels: 14px, weight 700, uppercase, green accent
