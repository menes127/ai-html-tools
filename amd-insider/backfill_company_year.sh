#!/usr/bin/env bash
set -euo pipefail

# Backfill Form 4 data by company x year (one company/year per run)
# Example:
#   ./backfill_company_year.sh
#   START_YEAR=2012 END_YEAR=2026 COMPANIES="TSM TSLA" SLEEP_SECONDS=2 ./backfill_company_year.sh

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

START_YEAR="${START_YEAR:-2012}"
END_YEAR="${END_YEAR:-$(date +%Y)}"
COMPANIES="${COMPANIES:-TSM TSLA}"
SLEEP_SECONDS="${SLEEP_SECONDS:-2}"
LOG_FILE="${LOG_FILE:-$ROOT_DIR/backfill.log}"

if [[ -z "${SUPABASE_URL:-}" || -z "${SUPABASE_SERVICE_ROLE_KEY:-}" ]]; then
  echo "[ERROR] SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY are required." >&2
  echo "        export them first (or load from .env)." >&2
  exit 1
fi

if [[ -z "${SEC_USER_AGENT:-}" ]]; then
  echo "[WARN] SEC_USER_AGENT not set, using fallback contact placeholder." >&2
  export SEC_USER_AGENT="backfill-script sec-monitor-contact@example.com"
fi

echo "== Backfill start: $(date -Iseconds) ==" | tee -a "$LOG_FILE"
echo "Companies: $COMPANIES | Years: $START_YEAR..$END_YEAR | Sleep: ${SLEEP_SECONDS}s" | tee -a "$LOG_FILE"

for company in $COMPANIES; do
  for year in $(seq "$START_YEAR" "$END_YEAR"); do
    echo "[$(date -Iseconds)] RUN company=$company year=$year" | tee -a "$LOG_FILE"
    if python3 amd_insider_monitor.py --company "$company" --year "$year"; then
      echo "[$(date -Iseconds)] OK  company=$company year=$year" | tee -a "$LOG_FILE"
    else
      echo "[$(date -Iseconds)] FAIL company=$company year=$year" | tee -a "$LOG_FILE"
      # continue so one bad year won't block all remaining years
    fi
    sleep "$SLEEP_SECONDS"
  done

done

echo "== Backfill done: $(date -Iseconds) ==" | tee -a "$LOG_FILE"
