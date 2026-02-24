import subprocess
import sys
import unittest
from pathlib import Path


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


if __name__ == "__main__":
    unittest.main()
