# Daily Stock Report Generator

Script-first generator for single-stock daily HTML reports.

The generator is designed to minimize Claude token usage:

1. Scripts fetch/cache market data.
2. Scripts compute technical indicators and trading levels.
3. Scripts render the HTML report from a normalized JSON payload.
4. Claude reads only `summary.json`, not full raw data or generated HTML.

## Usage

Render from sample JSON without fetching data:

```bash
node tools/daily-stock-report/scripts/generate_daily_report.js \
  --input-json tools/daily-stock-report/examples/amd_daily_report.sample.json \
  --output tools/daily-stock-report/out
```

Generate with real daily market data from StockAnalysis:

```bash
node tools/daily-stock-report/scripts/generate_daily_report.js \
  --ticker AMD \
  --date 2026-05-10 \
  --output tools/daily-stock-report/out \
  --benchmarks SPY,QQQ,SOXX,SMH \
  --refresh
```

## Outputs

For each run, the script writes:

- `{ticker}_daily_stock_report_{YYYY-MM-DD}.html`
- `{ticker}_daily_stock_report_{YYYY-MM-DD}.summary.json`

The summary JSON is intentionally compact so Claude can report results without reading the full HTML.

## Data sources

The script pipeline fetches daily OHLCV data from StockAnalysis historical pages using Node's built-in `https` module. It requires no API key or npm dependencies. If the provider fails, the script falls back to deterministic sample data and surfaces that warning in the compact summary JSON.
