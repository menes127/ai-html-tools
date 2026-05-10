# Daily Stock Report Skill

Generate a single-stock daily HTML report by running local Node scripts.

## Inputs
- ticker (default: AMD)
- date (default: today)
- output (default: AMD)
- benchmarks (default: SPY,QQQ,SOXX,SMH)
- refresh (default: false)
- provider (default: auto)

## Command

```bash
node tools/daily-stock-report/scripts/generate_daily_report.js \
  --ticker <TICKER> \
  --date <DATE> \
  --output <OUTPUT_DIR> \
  --benchmarks <CSV> \
  [--refresh] \
  [--provider <PROVIDER>]
```

## Response Contract
After execution, read only:
- `<output>/<ticker>_daily_stock_report_<date>.summary.json`

Return compactly:
- summaryPath
- outputHtml
- provider
- marketDataDate
- headlineSignal
- positionSize
- keyLevels (breakout/firstSupport/invalidation/target)
- dataWarnings

## Rules
- Do not read generated HTML unless user asks.
- Prefer `--refresh` when user asks for real-time/latest data.
- If report date is non-trading day, accept provider backfill date and surface warning.
