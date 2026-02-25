# Name Filter Datalist Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add native dropdown suggestions to the name filter using `datalist`, while keeping current `key in` filtering behavior.

**Architecture:** Keep all existing runtime logic and IDs, only add one HTML datalist and one JS helper to populate options from `yearRows` after each year load.

**Tech Stack:** Static HTML + vanilla JavaScript

---

### Task 1: Add `datalist` markup

**Files:**
- Modify: `index.html`

**Step 1: Bind input to datalist**
- Update `nameFilter` input to include `list="nameOptions"`.

**Step 2: Add datalist element**
- Insert `<datalist id="nameOptions"></datalist>` near the filters section.

**Step 3: Verify IDs**
Run: `rg -n "id=\"nameFilter\"|id=\"nameOptions\"" index.html`
Expected: both IDs exist exactly once.

### Task 2: Populate name options from current rows

**Files:**
- Modify: `index.html`

**Step 1: Add helper**
- Implement `updateNameFilterOptions()`:
  - Build unique, non-empty insider names from `yearRows`
  - Sort names
  - Render as `<option value="...">` inside `#nameOptions`

**Step 2: Wire helper into year loading**
- In `loadYear()`, after `yearRows` is assigned, call `updateNameFilterOptions()`.

**Step 3: Keep filter logic unchanged**
- Ensure `applyFilters()` still uses case-insensitive includes.

### Task 3: Verify

**Files:**
- Modify: none (verification only)

**Step 1:** `python3 -m py_compile amd_insider_monitor.py`

**Step 2:** `python3 -m unittest discover -s tests -v`

**Step 3:** Manual UI check
- Open page and verify name input supports both typing and dropdown selection.
- Confirm `key in` behavior still works.
