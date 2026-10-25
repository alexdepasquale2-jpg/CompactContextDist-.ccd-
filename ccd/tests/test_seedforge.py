"""The demo .ccd is the packed evidence and protocols, and it validates."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ccd import outline_lines, pack_markdown, parse, problems, render, unpack_markdown

ROOT = Path(__file__).resolve().parents[1]
AGENTS = ROOT.parent / "agents"


class SeedforgeTests(unittest.TestCase):
    def test_committed_ccd_matches_pack_and_round_trips(self) -> None:
        doc = pack_markdown([AGENTS / "evidence", AGENTS / "protocols"], "Seedforge")
        text = render(doc)
        committed = ROOT / "examples" / "seedforge.ccd"
        self.assertEqual(committed.read_text(encoding="utf-8"), text)
        self.assertEqual(problems(parse(text)), [])
        outline = outline_lines(text, depth=1)
        self.assertIn("evidence 1 ", outline)
        self.assertIn("protocols 1 ", outline)
        self.assertNotIn("evidence.lincoln", outline)
        lincoln = next(node for node in doc.nodes if node.id == "evidence.lincoln")
        self.assertIn("verify_kit.py", lincoln.body)
        self.assertTrue(lincoln.body.find("[INFERRED]") != -1)
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "docs"
            unpack_markdown(doc, dest)
            again = pack_markdown([dest], "Seedforge")
            self.assertEqual(render(again), text)
        result = subprocess.run(
            [sys.executable, "-m", "ccd", "validate", str(committed)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("ok", result.stdout)


if __name__ == "__main__":
    unittest.main()
