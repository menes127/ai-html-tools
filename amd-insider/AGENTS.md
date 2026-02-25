# Repository Guidelines

## Project Structure & Module Organization
- `amd_insider_monitor.py`: SEC Form 4 ingestion pipeline; parses filings and upserts to Supabase.
- `supabase/schema.sql`: canonical DB schema (tables, views, RLS, anon grants).
- `index.html`: static dashboard querying Supabase REST views.
- `tests/`: Python unit tests for payload mapping and CLI validation.

## Build, Test, and Development Commands
- `set -a && source .env && set +a`: load local env vars before write/read tests.
- `python3 amd_insider_monitor.py --days 365`: sync recent filings to Supabase.
- `python3 amd_insider_monitor.py --year 2025`: refresh one year.
- `python3 -m unittest discover -s tests -v`: run unit tests.
- `python3 -m py_compile amd_insider_monitor.py`: syntax check.
- `python3 -m http.server 8000`: local static preview (`/amd-insider/`).

## Coding Style & Naming Conventions
- Python: PEP 8, 4 spaces, snake_case for functions and variables, PascalCase for dataclasses.
- Keep network/parse/upsert concerns split into focused helpers.
- SQL objects use explicit names (`v_summary`, `v_years`, `v_transactions`) and stable column contracts.
- Frontend JS uses camelCase and descriptive DOM IDs.

## Testing Guidelines
- Add tests under `tests/` with `test_*.py` names using `unittest`.
- For ingestion changes, test payload field mapping and CLI guardrails.
- Before merge, run unit tests plus `py_compile`.

## Commit & Pull Request Guidelines
- Use concise, imperative commit messages (for example `feat: add supabase upsert pipeline`).
- Keep schema, ingestion, frontend, and workflow changes in logically separate commits when practical.
- PRs should include: change summary, verification commands, required secrets/env updates, and UI screenshots for `index.html` changes.

## Security & Configuration Tips
- Keep `.env` local-only and ignored by git.
- Never commit service role keys; store in GitHub Secrets.
- Frontend must use only `SUPABASE_ANON_KEY` with read-only view access.
- Keep RLS enabled and avoid granting anon access to base tables.
