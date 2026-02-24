#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from amd_insider_monitor import upsert_rows


def load_rows(data_dir: Path) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    filings_by_accession: Dict[str, Dict[str, Any]] = {}
    tx_rows: List[Dict[str, Any]] = []

    for path in sorted(data_dir.glob("*.json")):
        if path.name == "index.json":
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        for tx in payload.get("transactions", []):
            accession = tx.get("accession_number")
            filing_date = tx.get("filing_date")
            filing_url = tx.get("filing_url")
            if not accession or not filing_date or not filing_url:
                continue

            filings_by_accession[accession] = {
                "accession_number": accession,
                "filing_date": filing_date,
                "accepted_datetime": tx.get("accepted_datetime"),
                "filing_url": filing_url,
            }

            tx_rows.append(
                {
                    "accession_number": accession,
                    "transaction_date": tx.get("transaction_date") or filing_date,
                    "filing_date": filing_date,
                    "filing_url": filing_url,
                    "insider_name": tx.get("insider_name") or "Unknown",
                    "insider_title": tx.get("insider_title"),
                    "relationship": tx.get("relationship") or [],
                    "security_title": tx.get("security_title") or "Common Stock",
                    "code": tx.get("code") or "",
                    "shares": tx.get("shares"),
                    "price": tx.get("price"),
                    "acquired_disposed": tx.get("acquired_disposed"),
                    "shares_owned_after": tx.get("shares_owned_after"),
                    "ownership_nature": tx.get("ownership_nature"),
                    "is_10b5_1": bool(tx.get("is_10b5_1")),
                    "footnote_hint": tx.get("footnote_hint"),
                }
            )

    return list(filings_by_accession.values()), tx_rows


def main() -> int:
    parser = argparse.ArgumentParser(description="Backfill existing AMD JSON shards into Supabase")
    parser.add_argument("--data-dir", default="data", help="Directory with yearly JSON files")
    parser.add_argument("--batch-size", type=int, default=500, help="Upsert batch size")
    parser.add_argument("--dry-run", action="store_true", help="Only print counts, do not upsert")
    parser.add_argument("--supabase-url", default=os.getenv("SUPABASE_URL"), help="Supabase project URL")
    parser.add_argument("--supabase-key", default=os.getenv("SUPABASE_SERVICE_ROLE_KEY"), help="Supabase service role key")
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    if not data_dir.exists():
        raise SystemExit(f"Data directory not found: {data_dir}")

    filings, tx_rows = load_rows(data_dir)
    print(f"Discovered files: {len([p for p in data_dir.glob('*.json') if p.name != 'index.json'])}")
    print(f"Prepared rows: filings={len(filings)} transactions={len(tx_rows)}")

    if args.dry_run:
        print("Dry run enabled; no database writes performed.")
        return 0

    if not args.supabase_url or not args.supabase_key:
        raise SystemExit("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are required when not using --dry-run")

    filings_written = upsert_rows(
        supabase_url=args.supabase_url,
        api_key=args.supabase_key,
        table="filings",
        rows=filings,
        on_conflict="accession_number",
        batch_size=args.batch_size,
    )
    tx_written = upsert_rows(
        supabase_url=args.supabase_url,
        api_key=args.supabase_key,
        table="transactions",
        rows=tx_rows,
        on_conflict="accession_number,transaction_date,insider_name,code,shares,price",
        batch_size=args.batch_size,
    )

    print(f"Backfill complete: filings_upserted={filings_written} transactions_upserted={tx_written}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
