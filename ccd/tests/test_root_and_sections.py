"""Repo-root `python3 -m ccd`, and section focus on a heading-split spec."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent

LOCK_LINE = "LOCKLINEUNIQUE one figure"
NOISE = "SPECNOISEUNIQUE the rest of the spec"
PALETTE = "PALETTEUNIQUE gray dusk"


def run(*args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "ccd", *args],
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )


class RootAndSectionTests(unittest.TestCase):
    def test_python_m_ccd_from_repo_root(self) -> None:
        checked = run("validate", "ccd/examples/seedforge.ccd", cwd=REPO)
        self.assertEqual(checked.returncode, 0, checked.stderr)
        self.assertIn("ok", checked.stdout)
        listed = run("--help", cwd=REPO)
        self.assertEqual(listed.returncode, 0, listed.stderr)
        self.assertIn("focus", listed.stdout)

    def test_plain_markdown_splits_on_headings_and_focus_returns_one_section(self) -> None:
        spec = (
            "# Fog bell\n"
            "\n"
            "intro stays on the file node\n"
            "\n"
            "## 1. Seed\n"
            "\n"
            f"{NOISE}\n"
            "\n"
            "## 2. Look lock\n"
            "\n"
            f"{LOCK_LINE}\n"
            "\n"
            "### Palette\n"
            "\n"
            f"{PALETTE}\n"
            "\n"
            "## 3. Delivery\n"
            "\n"
            f"{NOISE} again\n"
            "\n"
            "```\n"
            "## not a heading\n"
            "```\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            path = folder / "spec.md"
            path.write_text(spec, encoding="utf-8")
            dest = folder / "spec.ccd"
            packed = run("pack", str(path), "-o", str(dest), "--title", "fog bell spec", cwd=REPO)
            self.assertEqual(packed.returncode, 0, packed.stderr)
            text = dest.read_text(encoding="utf-8")
            self.assertIn("\nnode spec\n", text)
            self.assertIn("\nnode spec.s-2-look-lock\n", text)
            self.assertIn("\nnode spec.s-2-look-lock.palette\n", text)
            self.assertNotIn("node spec.spec", text)
            self.assertNotIn("node spec.not-a-heading", text)
            focused = run(
                "focus",
                str(dest),
                "spec",
                "--section",
                "2. Look lock",
                cwd=REPO,
            )
            self.assertEqual(focused.returncode, 0, focused.stderr)
            self.assertIn(LOCK_LINE, focused.stdout)
            self.assertIn(PALETTE, focused.stdout)
            self.assertNotIn(NOISE, focused.stdout)
            self.assertNotIn("intro stays on the file node", focused.stdout)
            self.assertNotIn("not a heading", focused.stdout)


if __name__ == "__main__":
    unittest.main()
