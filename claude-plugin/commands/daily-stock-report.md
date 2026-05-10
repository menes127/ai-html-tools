---
description: Generate a daily single-stock HTML report with benchmark context
argument-hint: "[ticker] [date=YYYY-MM-DD, optional] [output=path, optional] [benchmarks=CSV, optional] [refresh=true|false, optional] [provider=auto|fallback, optional]"
---

Load the `daily-stock-report` skill and generate the report via:

`node tools/daily-stock-report/scripts/generate_daily_report.js`

Workflow requirements:
1. Parse args into ticker/date/output/benchmarks/refresh/provider.
2. Execute script command with those args.
3. Read only the generated `.summary.json` for response.
4. Return outputHtml path, headlineSignal, keyLevels, and dataWarnings.
