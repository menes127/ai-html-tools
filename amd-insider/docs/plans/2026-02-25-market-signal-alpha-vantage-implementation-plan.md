# Market Signal Alpha Vantage Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace unstable Yahoo browser fetch with Alpha Vantage free-key fetch and add explicit AMD stock price metrics in the market signal cards.

**Architecture:** Read `window.ALPHA_VANTAGE_API_KEY` from `config.js`, fetch daily series from Alpha Vantage, derive last/prev close and closes array for SMA/RSI, then render cards in `#marketSignal`. Keep existing dashboard structure and fallback behavior.

**Tech Stack:** Static HTML + vanilla JavaScript

---

### Task 1: Add config key surface

**Files:**
- Modify: `config.js`
- Modify: `index.html`

**Step 1:** Add `window.ALPHA_VANTAGE_API_KEY` placeholder in `config.js`.
**Step 2:** Read key in `index.html` script constants.

### Task 2: Replace market signal data fetch

**Files:**
- Modify: `index.html`

**Step 1:** Add helper to fetch and parse `TIME_SERIES_DAILY`.
**Step 2:** Handle API error fields (`Information`, `Note`, `Error Message`).
**Step 3:** Compute latest price, day change, change %, SMA20/SMA60, RSI14.
**Step 4:** Render upgraded cards with price metrics and update date.

### Task 3: Verify

**Files:**
- Modify: none (verification only)

**Step 1:** `python3 -m py_compile amd_insider_monitor.py`
**Step 2:** `python3 -m unittest discover -s tests -v`
**Step 3:** Manual page check with valid key in `config.js`.
