#!/usr/bin/env python3
"""
AMD insider monitor (Form 4 parser)

What it does:
1) Pulls AMD recent filings from SEC submissions endpoint
2) Filters Form 4 / 4-A filings
3) Downloads each filing's XML and parses insider transactions
4) Outputs JSON for dashboard use

Usage:
  python amd_insider_monitor.py --days 30 --output amd_insider_trades.json

Optional:
  export SEC_USER_AGENT="Your Name your@email.com"
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from urllib.error import HTTPError, URLError
import xml.etree.ElementTree as ET
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

AMD_CIK = "0000002488"
SUBMISSIONS_URL = f"https://data.sec.gov/submissions/CIK{AMD_CIK}.json"


@dataclass
class Trade:
    filing_date: str
    accepted_datetime: Optional[str]
    accession_number: str
    filing_url: str
    insider_name: str
    insider_title: Optional[str]
    relationship: List[str]
    transaction_date: str
    security_title: str
    code: str
    shares: Optional[float]
    price: Optional[float]
    acquired_disposed: Optional[str]
    shares_owned_after: Optional[float]
    ownership_nature: Optional[str]
    is_10b5_1: bool
    footnote_hint: Optional[str]


def http_get(url: str, user_agent: str, timeout: int = 25, retries: int = 4) -> bytes:
    last_err: Optional[Exception] = None
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": user_agent,
                    "Accept": "application/json,text/plain,*/*",
                    "Accept-Language": "en-US,en;q=0.9",
                    "Connection": "close",
                    "Referer": "https://www.sec.gov/",
                    "Host": "data.sec.gov" if "data.sec.gov" in url else "www.sec.gov",
                },
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read()
        except HTTPError as e:
            last_err = e
            # Retry on temporary or rate-limit style errors
            if e.code in (403, 429, 500, 502, 503, 504) and attempt < retries:
                time.sleep(min(2 ** attempt, 12))
                continue
            raise
        except URLError as e:
            last_err = e
            if attempt < retries:
                time.sleep(min(2 ** attempt, 12))
                continue
            raise

    if last_err:
        raise last_err
    raise RuntimeError("http_get failed without specific error")


def load_submissions(user_agent: str) -> Dict[str, Any]:
    raw = http_get(SUBMISSIONS_URL, user_agent)
    return json.loads(raw.decode("utf-8"))


def get_recent_form4_filings(submissions: Dict[str, Any], days: int) -> List[Dict[str, str]]:
    recent = submissions.get("filings", {}).get("recent", {})
    forms = recent.get("form", [])
    accession_numbers = recent.get("accessionNumber", [])
    filing_dates = recent.get("filingDate", [])
    acceptance_datetimes = recent.get("acceptanceDateTime", [])
    primary_docs = recent.get("primaryDocument", [])

    cutoff = datetime.now(timezone.utc).date() - timedelta(days=days)
    out = []

    for i, form in enumerate(forms):
        if form not in ("4", "4/A"):
            continue

        fdate = filing_dates[i]
        try:
            fdate_obj = datetime.strptime(fdate, "%Y-%m-%d").date()
        except Exception:
            continue

        if fdate_obj < cutoff:
            continue

        accession = accession_numbers[i]
        accession_nodash = accession.replace("-", "")
        primary_doc = primary_docs[i]

        filing_url = (
            f"https://www.sec.gov/Archives/edgar/data/{int(AMD_CIK)}/{accession_nodash}/{primary_doc}"
        )

        out.append(
            {
                "form": form,
                "accession": accession,
                "filing_date": fdate,
                "accepted_datetime": acceptance_datetimes[i] if i < len(acceptance_datetimes) else None,
                "filing_url": filing_url,
            }
        )

    return out


def text_of(node: Optional[ET.Element]) -> Optional[str]:
    if node is None or node.text is None:
        return None
    return node.text.strip()


def to_float(s: Optional[str]) -> Optional[float]:
    if s is None:
        return None
    s = s.replace(",", "").strip()
    if s == "":
        return None
    try:
        return float(s)
    except ValueError:
        return None


def boolish(s: Optional[str]) -> bool:
    if s is None:
        return False
    return s.strip().lower() in {"1", "true", "yes", "y"}


def parse_relationship(root: ET.Element) -> (str, Optional[str], List[str]):
    owner = root.find("reportingOwner")
    if owner is None:
        return "Unknown", None, []

    owner_id = owner.find("reportingOwnerId")
    owner_rel = owner.find("reportingOwnerRelationship")

    insider_name = text_of(owner_id.find("rptOwnerName")) if owner_id is not None else "Unknown"
    insider_title = text_of(owner_rel.find("officerTitle")) if owner_rel is not None else None

    rel = []
    if owner_rel is not None:
        if boolish(text_of(owner_rel.find("isDirector"))):
            rel.append("Director")
        if boolish(text_of(owner_rel.find("isOfficer"))):
            rel.append("Officer")
        if boolish(text_of(owner_rel.find("isTenPercentOwner"))):
            rel.append("10% Owner")
        if boolish(text_of(owner_rel.find("isOther"))):
            rel.append("Other")

    return (insider_name or "Unknown", insider_title, rel)


def parse_footnotes(root: ET.Element) -> Dict[str, str]:
    notes = {}
    for fn in root.findall("footnotes/footnote"):
        fid = fn.attrib.get("id")
        txt = text_of(fn)
        if fid and txt:
            notes[fid] = txt
    return notes


def parse_non_derivative_transactions(
    root: ET.Element,
    filing_meta: Dict[str, str],
) -> List[Trade]:
    trades: List[Trade] = []

    insider_name, insider_title, relationship = parse_relationship(root)
    footnotes = parse_footnotes(root)

    nd_table = root.find("nonDerivativeTable")
    if nd_table is None:
        return trades

    tx_nodes = nd_table.findall("nonDerivativeTransaction")
    for tx in tx_nodes:
        security_title = text_of(tx.find("securityTitle/value")) or "Common Stock"
        tx_date = text_of(tx.find("transactionDate/value")) or filing_meta["filing_date"]

        code = text_of(tx.find("transactionCoding/transactionCode")) or ""
        shares = to_float(text_of(tx.find("transactionAmounts/transactionShares/value")))
        price = to_float(text_of(tx.find("transactionAmounts/transactionPricePerShare/value")))
        acq_disp = text_of(tx.find("transactionAmounts/transactionAcquiredDisposedCode/value"))

        shares_after = to_float(text_of(tx.find("postTransactionAmounts/sharesOwnedFollowingTransaction/value")))
        ownership_nature = text_of(tx.find("ownershipNature/directOrIndirectOwnership/value"))

        # detect 10b5-1 hints via footnotes references in this transaction
        refs = []
        for ref in tx.findall(".//*[@id]"):
            pass

        tx_footnote_ids = [
            node.attrib.get("id")
            for node in tx.findall(".//footnoteId")
            if node.attrib.get("id")
        ]
        texts = [footnotes[fid] for fid in tx_footnote_ids if fid in footnotes]
        hint = " | ".join(texts) if texts else None

        hint_lower = (hint or "").lower()
        is_10b5_1 = "10b5-1" in hint_lower or "10b5" in hint_lower

        trades.append(
            Trade(
                filing_date=filing_meta["filing_date"],
                accepted_datetime=filing_meta.get("accepted_datetime"),
                accession_number=filing_meta["accession"],
                filing_url=filing_meta["filing_url"],
                insider_name=insider_name,
                insider_title=insider_title,
                relationship=relationship,
                transaction_date=tx_date,
                security_title=security_title,
                code=code,
                shares=shares,
                price=price,
                acquired_disposed=acq_disp,
                shares_owned_after=shares_after,
                ownership_nature=ownership_nature,
                is_10b5_1=is_10b5_1,
                footnote_hint=hint,
            )
        )

    return trades


def parse_form4_xml(xml_bytes: bytes, filing_meta: Dict[str, str]) -> List[Trade]:
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError:
        return []

    # Some documents may wrap inside ownershipDocument; normalize if needed
    if root.tag != "ownershipDocument":
        found = root.find(".//ownershipDocument")
        if found is not None:
            root = found

    if root.tag != "ownershipDocument":
        return []

    return parse_non_derivative_transactions(root, filing_meta)


def fetch_and_parse_filing(filing_meta: Dict[str, str], user_agent: str) -> List[Trade]:
    # primaryDocument may be .txt or .xml
    primary_url = filing_meta["filing_url"]

    try:
        raw = http_get(primary_url, user_agent)
    except urllib.error.HTTPError:
        return []

    # If primary doc is XML and parseable, use it directly
    trades = parse_form4_xml(raw, filing_meta)
    if trades:
        return trades

    # fallback: find XML doc listed in filing directory index
    accession_nodash = filing_meta["accession"].replace("-", "")
    dir_url = f"https://www.sec.gov/Archives/edgar/data/{int(AMD_CIK)}/{accession_nodash}/index.json"

    try:
        listing_raw = http_get(dir_url, user_agent)
        listing = json.loads(listing_raw.decode("utf-8"))
        items = listing.get("directory", {}).get("item", [])
    except Exception:
        return []

    xml_candidates = [x.get("name") for x in items if x.get("name", "").lower().endswith(".xml")]
    for name in xml_candidates:
        xml_url = f"https://www.sec.gov/Archives/edgar/data/{int(AMD_CIK)}/{accession_nodash}/{name}"
        try:
            xml_raw = http_get(xml_url, user_agent)
            trades = parse_form4_xml(xml_raw, filing_meta)
            if trades:
                return trades
        except Exception:
            continue

    return []


def summarize(trades: List[Trade]) -> Dict[str, Any]:
    code_counts: Dict[str, int] = {}
    insiders: Dict[str, int] = {}
    for t in trades:
        code_counts[t.code] = code_counts.get(t.code, 0) + 1
        insiders[t.insider_name] = insiders.get(t.insider_name, 0) + 1

    latest_date = max((t.transaction_date for t in trades), default=None)
    return {
        "total_transactions": len(trades),
        "codes": code_counts,
        "insiders": insiders,
        "latest_transaction_date": latest_date,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="AMD Form 4 insider transaction monitor")
    parser.add_argument("--days", type=int, default=90, help="Look back N days in filings.recent")
    parser.add_argument("--output", default="amd_insider_trades.json", help="Output JSON path")
    parser.add_argument("--sleep", type=float, default=0.25, help="Pause between SEC requests")
    parser.add_argument(
        "--user-agent",
        default=os.getenv("SEC_USER_AGENT", "amd-monitor/1.0 contact: your-email@example.com"),
        help="SEC-compatible User-Agent",
    )
    args = parser.parse_args()

    ua = args.user_agent
    if "@" not in ua and "contact" not in ua.lower():
        print("[WARN] Consider setting SEC_USER_AGENT with contact info to comply with SEC guidance.", file=sys.stderr)

    submissions = load_submissions(ua)
    filings = get_recent_form4_filings(submissions, args.days)

    all_trades: List[Trade] = []
    for idx, filing in enumerate(filings, start=1):
        trades = fetch_and_parse_filing(filing, ua)
        all_trades.extend(trades)
        if args.sleep > 0:
            time.sleep(args.sleep)

    # newest first
    all_trades.sort(key=lambda t: (t.transaction_date, t.filing_date), reverse=True)

    payload = {
        "company": "AMD",
        "cik": AMD_CIK,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "lookback_days": args.days,
        "filings_scanned": len(filings),
        "summary": summarize(all_trades),
        "transactions": [asdict(t) for t in all_trades],
    }

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(all_trades)} transactions from {len(filings)} filings -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
