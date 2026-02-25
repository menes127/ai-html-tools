# Trend Type Toggle + Insider Net Leaderboard Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implement transaction type toggles and insider net buy/sell leaderboard in the trend panel.

**Architecture:** Keep existing trend rendering pipeline, add selected-type state and pass it into aggregate logic. Reuse filtered row set from current granularity and insider keyword to compute leaderboard summary.

**Tech Stack:** Static HTML/CSS + vanilla JS

---

### Task 1: Add trend controls and leaderboard container
- Modify `index.html`
- Add type toggle controls and leaderboard render target.

### Task 2: Add state, type filter logic, and leaderboard calculation
- Modify `index.html`
- Add selected type set, include/exclude helper, aggregate update.
- Add `renderLeaderboard(rows)` and link to `renderChart()`.

### Task 3: Wire events and verification
- Modify `index.html`
- Add toggle handlers and refresh chain.
- Run `python3 -m py_compile amd_insider_monitor.py` and `python3 -m unittest discover -s tests -v`.
