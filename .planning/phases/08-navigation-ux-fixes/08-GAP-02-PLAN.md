---
phase: 08-navigation-ux-fixes
plan: GAP-02
type: execute
wave: 1
depends_on: []
files_modified:
  - frontend/src/app/paddles/page.tsx
autonomous: true
gap_closure: true
requirements: []
must_haves:
  truths:
    - "Catalog cards have proper <a> links with href attribute"
    - "Test selectors can find card links"
  artifacts:
    - path: "frontend/src/app/paddles/page.tsx"
      provides: "Card link structure"
      contains: "<a> tag with href wrapping card content"
  key_links:
    - from: "card component"
      to: "paddle detail page"
      via: "<a href=\"/paddles/{brand}/{slug}\">"
---

<objective>
Fix catalog card link structure to ensure proper `<a>` tags with href attributes for test selectors and accessibility.

Purpose: The UAT test expects cards to have clickable `<a>` links. Current structure may have the `<a>` inside `<article>` which could confuse test selectors.
Output: Cards with clear `<a>` link structure that test selectors can target
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/phases/08-navigation-ux-fixes/08-HUMAN-UAT.md
@frontend/src/app/paddles/page.tsx

## Gap Analysis (from 08-HUMAN-UAT.md)
- truth: "Catalog card numeric-ID fallback works (no 404)"
- status: failed
- reason: "Card structure does not have <a> links in expected format"
- severity: major
- root_cause: "Card component structure mismatch with test selector"
- missing: "Verify card component has proper <a> href"

## Current State
The paddles/page.tsx currently has:
```tsx
<article key={paddle.id} className="...">
  <a href={`/paddles/...`} className="block">
    {/* card content */}
  </a>
</article>
```

The `<a>` is nested inside `<article>`. Test selectors may expect the `<a>` to be the root or have specific attributes.
</context>

<tasks>

<task type="auto">
  <name>Task 1: Refactor card link structure</name>
  <files>frontend/src/app/paddles/page.tsx</files>
  <read_first>
    - frontend/src/app/paddles/page.tsx
  </read_first>
  <action>
    Refactor the paddle card structure in paddles/page.tsx to ensure test selectors can find the links:

    Current structure (lines 43-94):
    ```tsx
    <article key={paddle.id} className="...">
      <a href={`/paddles/...`} className="block">
        {/* content */}
      </a>
    </article>
    ```

    Update to ensure the `<a>` element has proper accessibility and test attributes:

    ```tsx
    <article
      key={paddle.id}
      className="border rounded-lg overflow-hidden hover:shadow-md transition-shadow"
    >
      <a
        href={`/paddles/${encodeURIComponent(paddle.brand?.toLowerCase() ?? '')}/${encodeURIComponent(paddle.model_slug ?? String(paddle.id))}`}
        className="block p-4"
        data-testid="paddle-card-link"
      >
        {/* existing card content - image, name, brand, badges */}
      </a>
    </article>
    ```

    Key changes:
    1. Move `p-4` padding from article to the `<a>` element (className="block p-4")
    2. Add `data-testid="paddle-card-link"` attribute for test selectors
    3. Ensure `overflow-hidden` is on article for border-radius to clip content properly
    4. Keep all existing inner content (image, name, brand, skill_level badge, specs, stock, price)
  </action>
  <verify>
    <automated>grep -q 'data-testid="paddle-card-link"' frontend/src/app/paddles/page.tsx && echo "PASS" || echo "FAIL"</automated>
  </verify>
  <acceptance_criteria>
    - grep -q 'data-testid="paddle-card-link"' frontend/src/app/paddles/page.tsx returns true
    - grep -E '<a.*href=' frontend/src/app/paddles/page.tsx shows <a> tags with href attributes
    - grep -c 'data-testid="paddle-card-link"' frontend/src/app/paddles/page.tsx matches number of paddle cards
  </acceptance_criteria>
</task>

</tasks>

<verification>
Run verification commands:
- grep "data-testid=\"paddle-card-link\"" frontend/src/app/paddles/page.tsx
- Verify <a> tag wraps card content with href attribute present
</verification>

<success_criteria>
- Each paddle card has an <a> element with data-testid="paddle-card-link"
- The <a> element has proper href pointing to /paddles/{brand}/{slug}
- All card content (image, name, brand, badges) is inside the <a> tag
- Test selectors can find and click card links
</success_criteria>

<output>
After completion, create `.planning/phases/08-navigation-ux-fixes/08-GAP-02-SUMMARY.md`
</output>
