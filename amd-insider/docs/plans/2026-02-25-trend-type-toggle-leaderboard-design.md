# Trend Type Toggle + Insider Net Leaderboard Design

## Goal
Add two features in the trend section:
1. Transaction type breakdown toggles (`P/S/A/G/M/F/other`) that affect trend aggregation.
2. Insider net buy/sell leaderboard using net amount = sell - buy.

## Scope
- Trend panel only.
- No backend/schema changes.
- No behavior changes to monitor table filters.

## Rules
- Type toggles are multi-select, default all selected.
- At least one type must remain selected.
- Monthly view uses `yearRows`; yearly view uses all cached rows.
- Insider keyword filter applies to both trend and leaderboard.

## Leaderboard Calculation
- Amount per trade = `shares * price`
- Buy amount: `code === 'P'`
- Sell amount: `code === 'S'`
- Net amount: `sell - buy`
- Top net buy: smallest (most negative) net amounts
- Top net sell: largest positive net amounts

## UI
- Add type toggles in trend toolbar.
- Add leaderboard card below trend table with two columns:
  - Top net buy
  - Top net sell
