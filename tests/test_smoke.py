"""Basic smoke tests for the project skeleton."""

from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]


class SmokeTest(unittest.TestCase):
    """Validate the CLI starts and renders output successfully."""

    def test_module_runs_without_args(self) -> None:
        """The module should run in headless mode and print summary output."""
        map_path = ROOT / "maps" / "easy" / "01_linear_path.txt"
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "src",
                str(map_path),
                "--no-display",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("Network Summary", result.stdout)


if __name__ == "__main__":
    unittest.main()
