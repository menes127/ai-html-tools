---
description: Generate the AMD daily stock report with benchmark context
argument-hint: ""
---

Run:

`node tools/daily-stock-report/scripts/generate_daily_report.js --ticker AMD --output AMD/report --benchmarks SPY,QQQ,SOXX,SMH`

Workflow requirements:
1. Execute the command exactly as written.
2. Read only the generated `.summary.json` for response.
3. Return outputHtml path, headlineSignal, keyLevels, and dataWarnings.
4. Do not read generated HTML unless the user asks.
