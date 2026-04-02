---
phase: 11
slug: core-web-vitals-optimization
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-01
---

# Phase 11 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Lighthouse CI + web-vitals |
| **Config file** | `.github/workflows/performance.yml` |
| **Quick run command** | `npm run lighthouse:mobile` |
| **Full suite command** | `npm run lighthouse:desktop && npm run lighthouse:mobile` |
| **Estimated runtime** | ~120 seconds |

---

## Sampling Rate

- **After every task commit:** Run `npm run lighthouse:mobile`
- **After every plan wave:** Run full Lighthouse CI suite
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 60 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 11-01-01 | 01 | 1 | IMG-01 | lighthouse | `npm run lighthouse:mobile` | ⬜ W0 | ⬜ pending |
| 11-01-02 | 01 | 1 | IMG-02 | lighthouse | `npm run lighthouse:mobile` | ⬜ W0 | ⬜ pending |
| 11-02-01 | 02 | 1 | FONT-01 | lighthouse | `npm run lighthouse:mobile` | ⬜ W0 | ⬜ pending |
| 11-02-02 | 02 | 1 | SCRIPT-01 | lighthouse | `npm run lighthouse:mobile` | ⬜ W0 | ⬜ pending |
| 11-03-01 | 03 | 2 | CLS-01 | lighthouse | `npm run lighthouse:mobile` | ⬜ W0 | ⬜ pending |
| 11-04-01 | 04 | 2 | RUM-01 | manual | Vercel dashboard check | ⬜ W0 | ⬜ pending |
| 11-04-02 | 04 | 2 | A11Y-01 | axe | `npm run test:a11y` | ⬜ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `lighthouserc.json` — Lighthouse CI configuration
- [ ] `scripts/performance-test.js` — Performance test runner
- [ ] `@next/bundle-analyzer` — Bundle size analysis

*Wave 0 installs performance testing infrastructure.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Real user CWV data | RUM-01 | Needs production traffic | Check Vercel Speed Insights dashboard for 75th percentile metrics |
| WCAG AA compliance | A11Y-03 | Visual/contrast checks | Manual axe DevTools scan on all page types |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 60s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
