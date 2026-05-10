# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Big picture
- This repo is mostly a collection of static HTML/JavaScript pages deployed to GitHub Pages.
- The two scripted subprojects are:
  - `amd-insider/`: a Python SEC Form 4 ingestion pipeline plus a Supabase-backed dashboard.
  - `tools/daily-stock-report/`: a Node-based daily report generator that fetches market data, computes technical signals, and renders HTML plus a compact summary JSON.
- Root-level `*.html` files are standalone browser demos; they generally do not share a framework or build pipeline.
- `amd-insider/supabase/schema.sql` is the canonical database shape. The dashboard reads Supabase views (`v_summary`, `v_years`, `v_transactions`) rather than base tables.
- `amd-insider/amd_insider_monitor.py` supports multiple tickers and has a TSM disclosure fallback when Form 4 data is not available.
- `tools/daily-stock-report/scripts/generate_daily_report.js` is the orchestration entry point. Its pipeline is: fetch/cache raw data -> compute technicals/levels/signals -> render HTML -> write `summary.json`.
- For daily report work, prefer reading the generated `*.summary.json` file; only open the rendered HTML when the user explicitly wants the page itself.
- `amd-insider/config.js` is loaded by the dashboard at runtime and should stay limited to public client-side values.

## Common commands

There is no repo-wide package manager manifest, build script, or lint script. The practical validation path is to run the Python checks, the Node generators, and the static preview server.

### Static preview
```bash
python3 -m http.server 8000
```
Open `http://localhost:8000/` for the root pages or `http://localhost:8000/amd-insider/` for the AMD dashboard.

### AMD insider sync
```bash
python3 amd-insider/amd_insider_monitor.py --days 365
python3 amd-insider/amd_insider_monitor.py --year 2025
python3 amd-insider/amd_insider_monitor.py --days 365 --company AMD --company NVDA --company TSM --company TSLA
```

### Python tests
```bash
python3 -m unittest discover -s amd-insider/tests -v
python3 -m unittest discover -s amd-insider/tests -p test_cli_args.py -v
python3 -m py_compile amd-insider/amd_insider_monitor.py
```

### Daily stock report generator
```bash
node tools/daily-stock-report/scripts/generate_daily_report.js \
  --input-json tools/daily-stock-report/examples/amd_daily_report.sample.json \
  --output tools/daily-stock-report/out

node tools/daily-stock-report/scripts/generate_daily_report.js \
  --ticker AMD \
  --date 2026-05-10 \
  --output AMD \
  --benchmarks SPY,QQQ,SOXX,SMH \
  --refresh
```

## Architecture notes
- The AMD insider flow is split between ingestion, storage, and presentation:
  - the Python script pulls SEC data and writes rows to Supabase;
  - `supabase/schema.sql` defines the tables, indexes, views, and RLS/anon grants;
  - `index.html` renders the dashboard entirely from the public views.
- GitHub Actions runs `update-amd-insider.yml` on a daily schedule and refreshes the recent-window insider data for the supported companies.
- The daily stock report flow is intentionally script-first and dependency-light: it uses Node built-ins, saves raw/cache artifacts under `tools/daily-stock-report/cache/`, and writes final outputs under the chosen output directory.
- The report generator’s compact summary JSON is the stable contract for downstream Claude/plugin usage; the full HTML is mainly for human viewing.
- Historical design and implementation notes for the AMD dashboard live under `amd-insider/docs/plans/` and are useful when you need context for why a UI/data shape changed.
