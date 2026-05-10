# Repository Guidelines

## Project Structure & Module Organization
This repository hosts static browser tools and AMD-related reporting pages for GitHub Pages. Root-level HTML files such as `index.html`, `pick_theorem.html`, `ping_pong.html`, `plane_shooter.html`, and `typing_game.html` are standalone pages. AMD research pages live in `AMD/`, with generated daily report outputs in `AMD/report/`. The `tools/daily-stock-report/` directory contains the Node script pipeline, templates, schemas, examples, cache, and output folders for stock reports. The `amd-insider/` subproject contains its own dashboard, Python SEC ingestion script, Supabase schema, tests, and local `AGENTS.md`.

## Build, Test, and Development Commands
- `python -m http.server 8000`: preview the static site locally, then open `http://localhost:8000/`.
- `node tools/daily-stock-report/scripts/generate_daily_report.js --input-json tools/daily-stock-report/examples/amd_daily_report.sample.json --output tools/daily-stock-report/out`: render a report from sample data without network access.
- `node tools/daily-stock-report/scripts/generate_daily_report.js --ticker AMD --date 2026-05-10 --output AMD --benchmarks SPY,QQQ,SOXX,SMH`: generate a dated AMD report.
- `python -m unittest discover -s amd-insider/tests -v`: run the Python tests for the AMD insider monitor.
- `python -m py_compile amd-insider/amd_insider_monitor.py`: syntax-check the ingestion script.

## Coding Style & Naming Conventions
Keep standalone pages dependency-light: plain HTML, CSS, and JavaScript are preferred unless a page already uses a library. Use 2-space indentation for HTML/CSS/JS and 4 spaces for Python. Name generated stock reports with the existing pattern `amd_daily_stock_report_YYYY-MM-DD.html` plus matching `.summary.json`. Python uses `snake_case`; frontend JavaScript uses `camelCase` and descriptive DOM IDs.

## Testing Guidelines
Add Python tests under `amd-insider/tests/` using `test_*.py` and `unittest`. For report-generator changes, verify with the sample JSON command and inspect both generated HTML and summary JSON. For UI changes, run a local static server and check the affected page in a browser at desktop and mobile widths.

## Commit & Pull Request Guidelines
Recent commits use concise Conventional Commit-style subjects, for example `feat(amd-insider): add top data-scope hint for TSM disclosure mode` and `fix: include J code and decouple end-holding from code filters`. Follow that pattern with an imperative summary and optional scope. PRs should include a short change summary, verification commands, linked issues when applicable, and screenshots for visible HTML/dashboard changes.

## Security & Configuration Tips
Do not commit secrets, local `.env` files, or private API keys. Keep generated cache data in `tools/daily-stock-report/cache/` and avoid adding large raw provider dumps unless they are intentional fixtures. The `amd-insider` frontend should only expose read-only public credentials; service-role keys belong in local env files or GitHub Secrets.
