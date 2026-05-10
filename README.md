# ai-html-tools

Lightweight AI tools that run directly in the browser using HTML and JavaScript.

## Live Site

GitHub Pages: https://menes127.github.io/ai-html-tools/

## Pages

- Home: `index.html`
- Pick's Theorem Visualizer: `pick_theorem.html`
- Plane Shooter (English): `plane_shooter.html`
- Ping Pong (Player vs CPU): `ping_pong.html`
- AMD Insider Monitor: `amd-insider/index.html`

## AMD Insider Monitor (Auto Update)

- Data source: SEC Form 4 filings for AMD insiders
- Script: `amd-insider/amd_insider_monitor.py`
- Data files: `amd-insider/data/index.json` + `amd-insider/data/YYYY.json` (按年分片)
- Daily update workflow: `.github/workflows/update-amd-insider.yml`
- Schedule: every day 01:00 UTC (09:00 Asia/Shanghai)

## Daily Stock Report Generator

- Generator: `tools/daily-stock-report/`
- Purpose: fetch/cache market data, compute technical signals, and render single-stock daily HTML reports with compact summary JSON output.
- Safe sample output:

```bash
node tools/daily-stock-report/scripts/generate_daily_report.js \
  --input-json tools/daily-stock-report/examples/amd_daily_report.sample.json \
  --output tools/daily-stock-report/out
```

- Generate into the AMD report folder:

```bash
node tools/daily-stock-report/scripts/generate_daily_report.js \
  --input-json tools/daily-stock-report/examples/amd_daily_report.sample.json \
  --output AMD
```

- Script-pipeline form:

```bash
node tools/daily-stock-report/scripts/generate_daily_report.js \
  --ticker AMD \
  --date 2026-05-10 \
  --output AMD \
  --benchmarks SPY,QQQ,SOXX,SMH
```

## Plane Shooter Controls

- Type the enemy letter key to destroy that plane
- Pause/Resume: `Esc`

## Typing Training Features

- Each enemy carries one English letter (A-Z)
- Correct key = explode enemy + score bonus
- Wrong key = light penalty
- Real-time typing metrics: Accuracy and WPM
- 5 levels with increasing speed and spawn rate
