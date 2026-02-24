import subprocess
import sys
import unittest
from pathlib import Path


class CliArgsTests(unittest.TestCase):
    def test_requires_some_output_target(self) -> None:
        project_dir = Path(__file__).resolve().parents[1]
        script = project_dir / "amd_insider_monitor.py"
        proc = subprocess.run(
            [sys.executable, str(script), "--no-to-supabase"],
            capture_output=True,
            text=True,
            cwd=str(project_dir),
        )
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("At least one output is required", proc.stderr)


if __name__ == "__main__":
    unittest.main()
