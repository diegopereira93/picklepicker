---
phase: 08-navigation-ux-fixes
plan: GAP-01
type: execute
wave: 1
depends_on: []
files_modified:
  - frontend/src/components/layout/header.tsx
autonomous: true
gap_closure: true
requirements: []
must_haves:
  truths:
    - "Mobile hamburger menu shows only [Home, Catalogo] links"
    - "No Chat IA link visible in mobile navigation"
  artifacts:
    - path: "frontend/src/components/layout/header.tsx"
      provides: "Mobile nav structure"
      contains: "navLinks array without Chat IA"
  key_links:
    - from: "mobile nav"
      to: "navLinks array"
      via: "map over navLinks"
---

<objective>
Fix mobile header navigation by ensuring the hamburger menu does not display the "Chat IA" standalone link.

Purpose: Per D-02 from 08-CONTEXT.md, the quiz gate should be the only entry point to the AI chat. The "Chat IA" nav link bypasses this UX pattern.
Output: Mobile nav with only [Home, Catalogo] + Encontrar raquete CTA
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/phases/08-navigation-ux-fixes/08-CONTEXT.md
@.planning/phases/08-navigation-ux-fixes/08-HUMAN-UAT.md
@frontend/src/components/layout/header.tsx

## Gap Analysis (from 08-HUMAN-UAT.md)
- truth: "Header nav shows only [Home, Catalogo] + Encontrar raquete CTA, no Chat IA standalone link"
- status: failed
- reason: "Mobile hamburger menu still shows Chat IA link"
- missing: "Remove Chat IA from mobile navLinks array"
- severity: major

## Current State
The header.tsx file already uses a shared `navLinks` array (lines 16-19) for both desktop and mobile navigation. This array contains only [Home, Catalogo]. If the UAT is failing, there may be a separate mobileLinks array or the file has diverged from what's deployed.

## Note
Current grep shows no "Chat IA" in header.tsx - this gap may already be fixed. Verify before making changes.
</context>

<tasks>

<task type="auto">
  <name>Task 1: Verify mobile navLinks structure</name>
  <files>frontend/src/components/layout/header.tsx</files>
  <read_first>
    - frontend/src/components/layout/header.tsx
  </read_first>
  <action>
    Verify the header.tsx file structure:

    1. Check if there is a separate `mobileNavLinks` or `mobileLinks` array defined anywhere in the file
    2. Check the mobile navigation section (lines 77-87) to see what array it maps over
    3. If mobile nav uses a different array than `navLinks`, update it to use the same `navLinks` array
    4. If there is NO separate mobile array and mobile already uses `navLinks`, the gap may already be fixed

    The `navLinks` array at lines 16-19 must be:
    ```typescript
    const navLinks = [
      { href: "/", label: "Home" },
      { href: "/paddles", label: "Catalogo" },
    ]
    ```

    If mobile navigation iterates over any array containing `{ href: "/chat", label: "Chat IA" }`, remove that entry.
  </action>
  <verify>
    <automated>grep -n "Chat IA" frontend/src/components/layout/header.tsx | wc -l | xargs -I {} test {} -eq 0</automated>
  </verify>
  <acceptance_criteria>
    - grep -c "Chat IA" frontend/src/components/layout/header.tsx returns 0
    - grep "navLinks" frontend/src/components/layout/header.tsx shows only [Home, Catalogo] entries
    - Mobile hamburger menu renders same links as desktop
  </acceptance_criteria>
</task>

</tasks>

<verification>
Run verification commands:
- grep -E "navLinks|mobileNavLinks" frontend/src/components/layout/header.tsx
- grep "Chat IA" frontend/src/components/layout/header.tsx (should return empty)
</verification>

<success_criteria>
- header.tsx contains no references to "Chat IA" in any nav array
- Mobile hamburger menu renders same links as desktop: [Home, Catalogo]
- Encontrar raquete CTA button remains in both desktop and mobile headers
</success_criteria>

<output>
After completion, create `.planning/phases/08-navigation-ux-fixes/08-GAP-01-SUMMARY.md`
</output>
