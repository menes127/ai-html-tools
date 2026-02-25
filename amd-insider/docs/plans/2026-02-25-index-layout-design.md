# AMD Insider Index Layout Design

## Context
The current `index.html` uses a single-column flow (`header -> filters -> chart -> table`). Functional behavior is correct, but information hierarchy is weak on desktop and filters are not persistent while scrolling.

## Goal
Refactor page layout to a dashboard structure without changing data behavior:
- Desktop: dual-column layout with sticky filter sidebar.
- Main content: market signal, summary cards, and trend chart.
- Table: full-width section below dashboard area.
- Mobile: fallback to single column and disable sticky behavior.

## Approved Decisions
- Use pure CSS layout reflow first (minimal-risk approach).
- Keep all existing control IDs and runtime JS behavior unchanged.
- Keep existing fetch/filter/chart logic and event wiring unchanged.

## Layout Specification
### Desktop (`>= 980px`)
- Root dashboard area uses CSS Grid: `300px 1fr`.
- Left column:
  - Filter panel card containing existing controls:
    - `yearFilter`
    - `nameFilter`
    - `codeFilter`
    - `onlySignal`
    - `b5Filter`
    - `refreshBtn`
  - `position: sticky; top: 16px`.
- Right column:
  - `marketSignal`
  - `summary` cards (responsive internal grid)
  - Existing chart card and controls.

### Table Section
- Render table in a dedicated full-width card below the two-column dashboard.
- Preserve existing `tbody` target and table headers/columns.

### Mobile (`< 980px`)
- Switch to single-column flow.
- Disable sticky sidebar and allow natural vertical scroll.

## Non-Goals
- No JS module split in this change.
- No API, schema, or data-flow changes.
- No visual redesign beyond layout and spacing consistency.

## Compatibility Constraints
- Do not change existing control IDs used by JS.
- Do not alter filter semantics, chart aggregation logic, or render order.
- Limit DOM changes to wrapper containers and section grouping.

## Validation Criteria
- Desktop layout shows sticky filter sidebar and right-column insights.
- Table remains full width and readable.
- Mobile stacks all blocks in one column without overlap.
- Existing interactions still work: year switch, name/code/10b5-1 filters, refresh, chart granularity/insider selection.
- No new console/runtime errors.
