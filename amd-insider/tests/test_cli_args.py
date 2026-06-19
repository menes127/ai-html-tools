import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from amd_insider_monitor import resolve_companies


class CliArgsTests(unittest.TestCase):
    def test_requires_supabase_credentials_by_default(self) -> None:
        project_dir = Path(__file__).resolve().parents[1]
        script = project_dir / "amd_insider_monitor.py"
        proc = subprocess.run(
            [sys.executable, str(script), "--days", "1", "--sleep", "0"],
            capture_output=True,
            text=True,
            cwd=str(project_dir),
        )
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are required", proc.stderr)

    def test_rejects_legacy_output_flags(self) -> None:
        project_dir = Path(__file__).resolve().parents[1]
        script = project_dir / "amd_insider_monitor.py"
        proc = subprocess.run(
            [sys.executable, str(script), "--output", "legacy.json"],
            capture_output=True,
            text=True,
            cwd=str(project_dir),
        )
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("unrecognized arguments: --output legacy.json", proc.stderr)

    def test_resolves_sofi_company_config(self) -> None:
        companies = resolve_companies(["SOFI"])

        self.assertEqual(companies[0]["ticker"], "SOFI")
        self.assertEqual(companies[0]["cik"], "0001818874")
        self.assertEqual(companies[0]["name"], "SoFi Technologies, Inc.")


if __name__ == "__main__":
    unittest.main()
