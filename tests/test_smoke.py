"""Basic smoke tests for the project skeleton."""

import subprocess
import sys
import unittest


class SmokeTest(unittest.TestCase):
    """Validate the CLI starts and renders output successfully."""

    def test_module_runs_without_args(self) -> None:
        """The module should run and print a parsed network summary."""
        result = subprocess.run(
            [sys.executable, "-m", "src"],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("Network Summary", result.stdout)


if __name__ == "__main__":
    unittest.main()
