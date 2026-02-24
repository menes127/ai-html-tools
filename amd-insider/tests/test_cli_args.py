import subprocess
import sys
import unittest


class CliArgsTests(unittest.TestCase):
    def test_requires_some_output_target(self) -> None:
        proc = subprocess.run(
            [sys.executable, "amd_insider_monitor.py", "--no-to-supabase"],
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("At least one output is required", proc.stderr)


if __name__ == "__main__":
    unittest.main()
