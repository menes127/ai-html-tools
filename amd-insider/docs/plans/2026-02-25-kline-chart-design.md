# AMD K-Line Chart Design

## Goal
Add an interactive AMD K-line chart with day/week switching, zoom, pan, crosshair, and volume sub-chart below the existing market signal cards.

## Decision
Use third-party `Lightweight Charts` for robustness and speed, while preserving existing page data flow.

## Scope
- Add K-line panel in dashboard insights area.
- Reuse Alpha Vantage daily data already fetched for market signal.
- Support day/week toggle and render volume histogram.
- Keep all existing filters/table/chart behaviors unchanged.

## Data Model
Input candle:
- `date` (YYYY-MM-DD)
- `open`, `high`, `low`, `close`, `volume`

Weekly aggregation:
- `open`: first trading day open of week
- `close`: last trading day close of week
- `high`: max high of week
- `low`: min low of week
- `volume`: sum of week

## UX
- Toggle buttons: 日线 / 周线
- Built-in zoom/pan and crosshair from chart library
- Tooltip near crosshair shows OHLC + pct change + volume
- Resize-aware layout

## Error Handling
- If no key/data: show status text in K-line panel and keep page functional.
- If chart library fails to load: show fallback message.

## Non-Goals
- No backend proxy.
- No strategy signal generation from K-line.
