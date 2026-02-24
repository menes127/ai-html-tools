# Supabase Migration Design (AMD Insider)

## Goal
Migrate from local JSON shard storage to Supabase as the only runtime data source, while keeping the existing Python SEC parser and GitHub Actions scheduler for low maintenance.

## Chosen Direction
- Storage/API: Supabase Postgres + PostgREST
- Ingestion: GitHub Actions (daily)
- Frontend access: public read-only queries (anon key)
- Explicitly out of scope: Cloudflare D1/Worker API and local JSON runtime files

## Alternatives Considered
1. Supabase with JSON fallback
- Pros: easy rollback
- Cons: dual-source complexity

2. Cloudflare D1 + Worker
- Pros: edge-native architecture
- Cons: larger refactor, less aligned with simple maintenance

Decision: Supabase-only architecture for fastest reliable migration.

## Architecture
- `amd_insider_monitor.py` remains the SEC parser.
- Workflow runs daily in GitHub Actions.
- Parsed filing/transaction rows are upserted into Supabase tables.
- `index.html` reads from Supabase views instead of `data/index.json` and `data/YYYY.json`.

## Data Model
### Table: `filings`
- `accession_number` text primary key
- `filing_date` date not null
- `accepted_datetime` timestamptz null
- `filing_url` text not null
- `created_at` timestamptz default now()
- `updated_at` timestamptz default now()

### Table: `transactions`
- `id` uuid primary key default gen_random_uuid()
- `accession_number` text not null references `filings(accession_number)`
- `transaction_date` date not null
- `insider_name` text not null
- `insider_title` text null
- `relationship` text[] not null default '{}'
- `security_title` text not null
- `code` text not null
- `shares` numeric null
- `price` numeric null
- `acquired_disposed` text null
- `shares_owned_after` numeric null
- `ownership_nature` text null
- `is_10b5_1` boolean not null default false
- `footnote_hint` text null
- `created_at` timestamptz default now()
- `updated_at` timestamptz default now()

### Deduplication
Unique constraint on:
- (`accession_number`, `transaction_date`, `insider_name`, `code`, `shares`, `price`)

## Read Views (Frontend)
- `v_summary`: total rows, latest transaction date, code distribution, buy/sell/net amounts
- `v_years`: yearly counts + latest date
- `v_transactions`: filter-ready transaction rows for list rendering

## Security
- Enable RLS.
- Grant `anon` role `SELECT` on `v_summary`, `v_years`, `v_transactions` only.
- No direct write access from frontend.

## Ingestion and Backfill
### Daily Ingestion
- Parse SEC filings in date window.
- Upsert `filings` by `accession_number`.
- Upsert `transactions` using unique dedupe key.
- Emit run metrics: scanned, parsed, inserted, updated, skipped.

### One-Time Backfill
- Read all existing `data/YYYY.json` files.
- Transform and batch upsert (500-1000 rows per batch).
- Validate counts; then stop local JSON generation.

## Error Handling and Reliability
- Keep current SEC retry/backoff behavior.
- Add retry/backoff for Supabase write failures.
- Keep ingestion idempotent so reruns are safe.
- Fail CI on partial write errors.

## Rollout Plan
1. Create schema, constraints, and views in Supabase.
2. Add backfill script and load historical JSON into Supabase.
3. Update ingestion script and workflow to write Supabase only.
4. Update frontend data fetch from local files to Supabase views.
5. Verify end-to-end and remove JSON runtime path.

## Validation Criteria
- Summary and year dropdown match expected historical totals.
- Filter behavior (name/code/10b5-1/year) matches old UI behavior.
- Latest filing date updates after daily workflow run.
- No duplicate transaction rows after reruns.

## Risks and Mitigations
- API quota/rate limits on free tier: batch writes, reduce polling, cache stable reads.
- Exposed anon key misuse: strict RLS and read-only view access.
- Migration mismatch: parallel compare old JSON vs Supabase outputs before cutover.
