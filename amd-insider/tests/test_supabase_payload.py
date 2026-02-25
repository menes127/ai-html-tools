import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from amd_insider_monitor import Trade, trade_to_row


class SupabasePayloadTests(unittest.TestCase):
    def test_trade_to_row_has_required_fields(self) -> None:
        trade = Trade(
            issuer_ticker="AMD",
            issuer_cik="0000002488",
            issuer_name="Advanced Micro Devices",
            filing_date="2026-01-10",
            accepted_datetime="2026-01-10T12:00:00Z",
            accession_number="0000002488-26-000001",
            filing_url="https://example.com/form4.xml",
            insider_name="Lisa Su",
            insider_title="CEO",
            relationship=["Officer"],
            transaction_date="2026-01-09",
            security_title="Common Stock",
            code="P",
            shares=1000.0,
            price=120.5,
            acquired_disposed="A",
            shares_owned_after=500000.0,
            ownership_nature="D",
            is_10b5_1=False,
            footnote_hint=None,
        )

        row = trade_to_row(trade)

        self.assertEqual(row["accession_number"], "0000002488-26-000001")
        self.assertEqual(row["issuer_ticker"], "AMD")
        self.assertEqual(row["issuer_cik"], "0000002488")
        self.assertEqual(row["transaction_date"], "2026-01-09")
        self.assertEqual(row["insider_name"], "Lisa Su")
        self.assertEqual(row["code"], "P")


if __name__ == "__main__":
    unittest.main()
