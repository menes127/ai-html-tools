# K-Line Chart Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add an interactive K-line chart (day/week, zoom/pan, crosshair, volume) to the AMD dashboard using Lightweight Charts.

**Architecture:** Load Lightweight Charts via CDN in `index.html`, maintain a small chart state in JS, and update chart data from Alpha Vantage daily candles already fetched by `renderMarketSignal()`.

**Tech Stack:** Static HTML, vanilla JS, Lightweight Charts

---

### Task 1: Add chart panel markup and styles

**Files:**
- Modify: `index.html`

**Steps:**
1. Add K-line card block with timeframe controls and chart containers.
2. Add CSS for panel layout, buttons, chart area, tooltip, and status text.
3. Include Lightweight Charts script tag.

### Task 2: Add data transform and chart rendering

**Files:**
- Modify: `index.html`

**Steps:**
1. Extend Alpha Vantage parsing to return candle list with OHLCV.
2. Add weekly aggregation helper.
3. Add chart init/update functions for candlestick + volume series.
4. Add tooltip and timeframe switching logic.
5. Wire chart update into successful market-signal render path.

### Task 3: Verify and regression check

**Files:**
- Modify: none (verification)

**Steps:**
1. Run `python3 -m py_compile amd_insider_monitor.py`.
2. Run `python3 -m unittest discover -s tests -v`.
3. Manual check at `http://127.0.0.1:8000/`: day/week switch, zoom/pan, crosshair tooltip, volume bars.
