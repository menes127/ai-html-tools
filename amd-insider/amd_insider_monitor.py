#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from urllib.error import HTTPError, URLError
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from typing import Any, Dict, Iterable, List, Optional

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
            if e.code in (403, 429, 500, 502, 503, 504) and attempt < retries:
                time.sleep(min(2**attempt, 12))
                continue
            raise
        except URLError as e:
            last_err = e
            if attempt < retries:
                time.sleep(min(2**attempt, 12))
                continue
            raise
    if last_err:
        raise last_err
    raise RuntimeError("http_get failed")


def http_post_json(url: str, payload: Any, headers: Dict[str, str], timeout: int = 30, retries: int = 4) -> bytes:
    last_err: Optional[Exception] = None
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(
                url,
                data=data,
                headers={"Content-Type": "application/json", **headers},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read()
        except HTTPError as e:
            last_err = e
            if e.code in (408, 409, 425, 429, 500, 502, 503, 504) and attempt < retries:
                time.sleep(min(2**attempt, 12))
                continue
            detail = e.read().decode("utf-8", errors="ignore")[:600]
            raise RuntimeError(f"POST {url} failed ({e.code}): {detail}") from e
        except URLError as e:
            last_err = e
            if attempt < retries:
                time.sleep(min(2**attempt, 12))
                continue
            raise
    if last_err:
        raise last_err
    raise RuntimeError("http_post_json failed")


def load_json(url: str, ua: str) -> Dict[str, Any]:
    return json.loads(http_get(url, ua).decode("utf-8"))


def iter_submission_blocks(ua: str) -> List[Dict[str, Any]]:
    root = load_json(SUBMISSIONS_URL, ua)
    blocks = [{"recent": root.get("filings", {}).get("recent", {})}]
    for f in root.get("filings", {}).get("files", []) or []:
        name = f.get("name")
        if not name:
            continue
        try:
            part = load_json(f"https://data.sec.gov/submissions/{name}", ua)
            blocks.append({"recent": part})
        except Exception:
            continue
    return blocks


def collect_form4_filings(blocks: List[Dict[str, Any]], *, start: date, end: date) -> List[Dict[str, str]]:
    out: List[Dict[str, str]] = []
    seen = set()
    for blk in blocks:
        recent = blk.get("recent", {})
        forms = recent.get("form", [])
        accs = recent.get("accessionNumber", [])
        fdates = recent.get("filingDate", [])
        accepts = recent.get("acceptanceDateTime", [])
        docs = recent.get("primaryDocument", [])

        for i, form in enumerate(forms):
            if form not in ("4", "4/A"):
                continue
            if i >= len(fdates) or i >= len(accs) or i >= len(docs):
                continue
            try:
                d = datetime.strptime(fdates[i], "%Y-%m-%d").date()
            except Exception:
                continue
            if d < start or d > end:
                continue
            acc = accs[i]
            if acc in seen:
                continue
            seen.add(acc)
            nodash = acc.replace("-", "")
            out.append(
                {
                    "accession": acc,
                    "filing_date": fdates[i],
                    "accepted_datetime": accepts[i] if i < len(accepts) else None,
                    "filing_url": f"https://www.sec.gov/Archives/edgar/data/{int(AMD_CIK)}/{nodash}/{docs[i]}",
                }
            )
    out.sort(key=lambda x: x["filing_date"], reverse=True)
    return out


def text_of(node: Optional[ET.Element]) -> Optional[str]:
    return node.text.strip() if node is not None and node.text else None


def to_float(s: Optional[str]) -> Optional[float]:
    if not s:
        return None
    try:
        return float(s.replace(",", "").strip())
    except Exception:
        return None


def boolish(s: Optional[str]) -> bool:
    return (s or "").strip().lower() in {"1", "true", "yes", "y"}


def parse_relationship(root: ET.Element) -> tuple[str, Optional[str], List[str]]:
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
    return insider_name or "Unknown", insider_title, rel


def parse_form4_xml(xml_bytes: bytes, filing_meta: Dict[str, str]) -> List[Trade]:
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError:
        return []
    if root.tag != "ownershipDocument":
        found = root.find(".//ownershipDocument")
        if found is not None:
            root = found
    if root.tag != "ownershipDocument":
        return []

    owner_name, owner_title, relationship = parse_relationship(root)
    footnotes = {
        fn.attrib.get("id"): text_of(fn)
        for fn in root.findall("footnotes/footnote")
        if fn.attrib.get("id") and text_of(fn)
    }
    nd_table = root.find("nonDerivativeTable")
    if nd_table is None:
        return []

    trades: List[Trade] = []
    for tx in nd_table.findall("nonDerivativeTransaction"):
        tx_footnote_ids = [n.attrib.get("id") for n in tx.findall(".//footnoteId") if n.attrib.get("id")]
        texts = [footnotes[fid] for fid in tx_footnote_ids if fid in footnotes]
        hint = " | ".join(texts) if texts else None
        hint_lower = (hint or "").lower()

        trades.append(
            Trade(
                filing_date=filing_meta["filing_date"],
                accepted_datetime=filing_meta.get("accepted_datetime"),
                accession_number=filing_meta["accession"],
                filing_url=filing_meta["filing_url"],
                insider_name=owner_name,
                insider_title=owner_title,
                relationship=relationship,
                transaction_date=text_of(tx.find("transactionDate/value")) or filing_meta["filing_date"],
                security_title=text_of(tx.find("securityTitle/value")) or "Common Stock",
                code=text_of(tx.find("transactionCoding/transactionCode")) or "",
                shares=to_float(text_of(tx.find("transactionAmounts/transactionShares/value"))),
                price=to_float(text_of(tx.find("transactionAmounts/transactionPricePerShare/value"))),
                acquired_disposed=text_of(tx.find("transactionAmounts/transactionAcquiredDisposedCode/value")),
                shares_owned_after=to_float(text_of(tx.find("postTransactionAmounts/sharesOwnedFollowingTransaction/value"))),
                ownership_nature=text_of(tx.find("ownershipNature/directOrIndirectOwnership/value")),
                is_10b5_1=("10b5-1" in hint_lower or "10b5" in hint_lower),
                footnote_hint=hint,
            )
        )
    return trades


def fetch_and_parse_filing(filing_meta: Dict[str, str], ua: str) -> List[Trade]:
    primary_url = filing_meta["filing_url"]
    try:
        raw = http_get(primary_url, ua)
    except HTTPError:
        return []

    trades = parse_form4_xml(raw, filing_meta)
    if trades:
        return trades

    nodash = filing_meta["accession"].replace("-", "")
    dir_url = f"https://www.sec.gov/Archives/edgar/data/{int(AMD_CIK)}/{nodash}/index.json"
    try:
        listing = load_json(dir_url, ua)
    except Exception:
        return []

    for item in listing.get("directory", {}).get("item", []) or []:
        name = item.get("name", "")
        if not name.lower().endswith(".xml"):
            continue
        try:
            xml_raw = http_get(f"https://www.sec.gov/Archives/edgar/data/{int(AMD_CIK)}/{nodash}/{name}", ua)
            trades = parse_form4_xml(xml_raw, filing_meta)
            if trades:
                return trades
        except Exception:
            continue
    return []


def filing_to_row(filing_meta: Dict[str, str]) -> Dict[str, Any]:
    return {
        "accession_number": filing_meta["accession"],
        "filing_date": filing_meta["filing_date"],
        "accepted_datetime": filing_meta.get("accepted_datetime"),
        "filing_url": filing_meta["filing_url"],
    }


def trade_to_row(t: Trade) -> Dict[str, Any]:
    return {
        "accession_number": t.accession_number,
        "transaction_date": t.transaction_date,
        "filing_date": t.filing_date,
        "filing_url": t.filing_url,
        "insider_name": t.insider_name,
        "insider_title": t.insider_title,
        "relationship": t.relationship,
        "security_title": t.security_title,
        "code": t.code,
        "shares": t.shares,
        "price": t.price,
        "acquired_disposed": t.acquired_disposed,
        "shares_owned_after": t.shares_owned_after,
        "ownership_nature": t.ownership_nature,
        "is_10b5_1": t.is_10b5_1,
        "footnote_hint": t.footnote_hint,
    }


def chunks(rows: List[Dict[str, Any]], size: int) -> Iterable[List[Dict[str, Any]]]:
    for i in range(0, len(rows), size):
        yield rows[i : i + size]


def upsert_rows(
    *,
    supabase_url: str,
    api_key: str,
    table: str,
    rows: List[Dict[str, Any]],
    on_conflict: str,
    batch_size: int,
) -> int:
    if not rows:
        return 0

    encoded_conflict = urllib.parse.quote(on_conflict, safe=",")
    url = f"{supabase_url.rstrip('/')}/rest/v1/{table}?on_conflict={encoded_conflict}"
    headers = {
        "apikey": api_key,
        "Authorization": f"Bearer {api_key}",
        "Prefer": "resolution=merge-duplicates,return=minimal",
    }
    written = 0
    for batch in chunks(rows, batch_size):
        http_post_json(url, batch, headers)
        written += len(batch)
    return written


def upsert_to_supabase(
    *,
    filings: List[Dict[str, str]],
    trades: List[Trade],
    supabase_url: str,
    api_key: str,
    batch_size: int,
) -> Dict[str, int]:
    filing_rows = [filing_to_row(f) for f in filings]
    tx_rows = [trade_to_row(t) for t in trades]

    filed = upsert_rows(
        supabase_url=supabase_url,
        api_key=api_key,
        table="filings",
        rows=filing_rows,
        on_conflict="accession_number",
        batch_size=batch_size,
    )
    transacted = upsert_rows(
        supabase_url=supabase_url,
        api_key=api_key,
        table="transactions",
        rows=tx_rows,
        on_conflict="accession_number,transaction_date,insider_name,code,shares,price",
        batch_size=batch_size,
    )
    return {"filings_upserted": filed, "transactions_upserted": transacted}


def main() -> int:
    parser = argparse.ArgumentParser(description="AMD Form 4 insider monitor")
    parser.add_argument("--days", type=int, default=3650, help="Lookback days (default 10 years)")
    parser.add_argument("--year", type=int, default=None, help="Only update one specific year, e.g. 2021")
    parser.add_argument("--supabase-url", default=os.getenv("SUPABASE_URL"), help="Supabase project URL")
    parser.add_argument("--supabase-key", default=os.getenv("SUPABASE_SERVICE_ROLE_KEY"), help="Supabase service role key")
    parser.add_argument("--batch-size", type=int, default=500, help="Supabase upsert batch size")
    parser.add_argument("--sleep", type=float, default=0.2, help="Pause between SEC requests")
    parser.add_argument("--user-agent", default=os.getenv("SEC_USER_AGENT", "amd-monitor contact: your@email.com"))
    args = parser.parse_args()

    if not args.supabase_url or not args.supabase_key:
        parser.error("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are required (or pass --supabase-url/--supabase-key)")

    if args.year:
        start = date(args.year, 1, 1)
        end = date(args.year, 12, 31)
    else:
        end = datetime.now(timezone.utc).date()
        start = end - timedelta(days=args.days)

    ua = args.user_agent
    if "@" not in ua and "contact" not in ua.lower():
        print("[WARN] SEC_USER_AGENT should include contact email.", file=sys.stderr)

    blocks = iter_submission_blocks(ua)
    filings = collect_form4_filings(blocks, start=start, end=end)

    trades: List[Trade] = []
    for f in filings:
        trades.extend(fetch_and_parse_filing(f, ua))
        if args.sleep > 0:
            time.sleep(args.sleep)

    trades.sort(key=lambda t: (t.transaction_date, t.filing_date), reverse=True)
    result = upsert_to_supabase(
        filings=filings,
        trades=trades,
        supabase_url=args.supabase_url,
        api_key=args.supabase_key,
        batch_size=args.batch_size,
    )
    print(
        "Upserted to Supabase: "
        f"filings={result['filings_upserted']} transactions={result['transactions_upserted']}"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
