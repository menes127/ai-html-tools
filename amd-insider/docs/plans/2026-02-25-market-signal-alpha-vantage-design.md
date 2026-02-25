# Market Signal Alpha Vantage Design

## Problem
Current market signal fetch relies on Yahoo chart API and frequently fails in browser due to 403/429 or non-JSON responses.

## Goal
Stabilize AMD market signal by switching to Alpha Vantage (free key), and display stock price metrics directly in the dashboard.

## Decisions
- Data source: Alpha Vantage `TIME_SERIES_DAILY`.
- Config key: `window.ALPHA_VANTAGE_API_KEY` in `config.js`.
- Keep existing market signal card area (`#marketSignal`) and extend content.

## Data Display
- AMD 价格强弱
- AI 信号（技术面）
- 最新价 / 日涨跌额 / 日涨跌幅
- SMA20 / SMA60 / RSI(14)
- 更新日期（Alpha Vantage 最新交易日）

## Error Handling
- If key is missing: explicit config hint.
- If API returns `Information`/`Note`/`Error Message`: show concise failure reason.
- If parsing fails: show fallback unavailable card without breaking page.

## Non-Goals
- No backend proxy in this change.
- No schema/API changes on Supabase side.
