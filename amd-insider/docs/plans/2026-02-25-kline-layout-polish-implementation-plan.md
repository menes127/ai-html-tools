# K-Line Layout Polish Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Improve K-line and market signal visual layout for readability without changing data or interaction behavior.

**Architecture:** Keep current data flow and chart logic unchanged while refining `index.html` styles and lightweight markup wrappers. Adjust chart height, segmented timeframe controls, fixed tooltip placement, and stronger section separation in the insights panel.

**Tech Stack:** Static HTML/CSS + existing vanilla JS

---

### Task 1: Refine insights section structure

**Files:**
- Modify: `index.html`

**Step 1:** Wrap `marketSignal` in a dedicated card with section title.
**Step 2:** Keep summary and existing chart blocks order unchanged.
**Step 3:** Ensure all existing IDs remain unchanged.

### Task 2: Polish K-line styles

**Files:**
- Modify: `index.html`

**Step 1:** Increase chart height (desktop and mobile).
**Step 2:** Convert day/week controls to segmented style.
**Step 3:** Improve K-line card emphasis and spacing.
**Step 4:** Make tooltip fixed top-right to avoid candle overlap.

### Task 3: Keep interaction behavior stable

**Files:**
- Modify: `index.html`

**Step 1:** Update tooltip JS to only update content/display (no pointer-follow positioning).
**Step 2:** Keep zoom/pan/crosshair/day-week switching unchanged.

### Task 4: Verify

**Files:**
- Modify: none (verification only)

**Step 1:** `python3 -m py_compile amd_insider_monitor.py`
**Step 2:** `python3 -m unittest discover -s tests -v`
**Step 3:** Manual visual check at `http://127.0.0.1:8000/`.
