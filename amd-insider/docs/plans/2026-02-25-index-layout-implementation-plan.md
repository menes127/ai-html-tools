# Index Layout Refactor Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Refactor `index.html` into a desktop dual-column dashboard with a sticky filter sidebar and a full-width table section, while preserving existing behavior.

**Architecture:** Keep all existing data and event logic intact and perform a layout-only DOM/CSS refactor. Introduce wrapper sections for filter/insights/table regions and add responsive CSS rules to switch between desktop grid and mobile single-column layouts.

**Tech Stack:** Static HTML, inline CSS, vanilla JavaScript (existing runtime)

---

### Task 1: Restructure Layout Containers in `index.html`

**Files:**
- Modify: `index.html`

**Step 1: Create wrapper sections for dashboard layout**
- Add a root `main`/`div` container around current filter, signal/summary/chart, and table blocks.
- Create sections:
  - `.dashboard-grid`
  - `.panel.filters-panel`
  - `.panel.insights-panel`
  - `.panel.table-panel`

**Step 2: Keep existing IDs unchanged**
- Ensure these IDs remain exactly the same: `marketSignal`, `summary`, `yearFilter`, `nameFilter`, `codeFilter`, `onlySignal`, `b5Filter`, `refreshBtn`, `chartGranularity`, `chartInsider`, `chartMeta`, `chartRows`, `tbody`.

**Step 3: Preserve chart and table internals**
- Move blocks only as whole sections; avoid changing cell markup or script tag placement.

**Step 4: Verify structure sanity**
Run: `rg -n "id=\"(marketSignal|summary|yearFilter|nameFilter|codeFilter|onlySignal|b5Filter|refreshBtn|chartGranularity|chartInsider|chartMeta|chartRows|tbody)\"" index.html`
Expected: each ID appears exactly once.

**Step 5: Commit**
```bash
git add index.html
git commit -m "refactor: add dashboard layout containers"
```

### Task 2: Add Responsive Grid + Sticky Sidebar Styles

**Files:**
- Modify: `index.html`

**Step 1: Add desktop grid layout styles**
- Add `.dashboard-grid { display:grid; grid-template-columns: 300px 1fr; gap: 16px; }`
- Add `.filters-panel { position: sticky; top: 16px; align-self: start; }`

**Step 2: Add panel and spacing consistency styles**
- Add shared `.panel` styles for border, radius, padding.
- Improve summary cards to use responsive card grid inside the insights column.

**Step 3: Add mobile breakpoint fallback**
- At `<980px`, set `.dashboard-grid` to single column and disable sticky behavior.

**Step 4: Verify CSS hooks are present**
Run: `rg -n "dashboard-grid|filters-panel|insights-panel|table-panel|@media \(max-width: 980px\)" index.html`
Expected: all selectors found.

**Step 5: Commit**
```bash
git add index.html
git commit -m "style: implement responsive dashboard and sticky filters"
```

### Task 3: Validate Runtime Behavior After Layout Refactor

**Files:**
- Modify: none (validation only)

**Step 1: Run syntax checks for Python tooling baseline**
Run: `python3 -m py_compile amd_insider_monitor.py`
Expected: no output.

**Step 2: Run unit tests baseline**
Run: `python3 -m unittest discover -s tests -v`
Expected: all tests pass.

**Step 3: Quick static verification for key IDs**
Run: `rg -n "id=\"(yearFilter|refreshBtn|chartRows|tbody)\"" index.html`
Expected: IDs present once.

**Step 4: Manual UI checks**
- Start: `python3 -m http.server 8000`
- Open `/amd-insider/` and validate:
  - Desktop: sticky filter sidebar, right-column insights, full-width table below.
  - Mobile width: single-column layout, no sticky overlap.
  - Functional checks: year switch, filters, refresh, chart controls.

**Step 5: Commit**
```bash
git add index.html
git commit -m "chore: verify dashboard layout refactor"
```
