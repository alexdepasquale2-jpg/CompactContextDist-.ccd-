"""CLI contract for python -m ccd."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "ccd", *args],
        cwd=cwd or ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


class CliTests(unittest.TestCase):
    def test_pack_outline_expand_search_collapse_unpack_validate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            src = tmp_path / "src"
            (src / "kit").mkdir(parents=True)
            (src / "kit" / "_index.md").write_text(
                "---\n"
                "id: kit\n"
                "parent: -\n"
                "summary: Finished kit is the quality bar.\n"
                "src: sources/evidence.md\n"
                "see: kit.socket\n"
                "inferred: false\n"
                "---\n"
                "Match the contact sheet.\n",
                encoding="utf-8",
            )
            (src / "kit" / "01-socket.md").write_text(
                "---\n"
                "id: kit.socket\n"
                "parent: kit\n"
                "summary: Child pivot named by the build prompt.\n"
                "src: -\n"
                "see: -\n"
                "inferred: true\n"
                "---\n"
                "Pivot at the grip.\n",
                encoding="utf-8",
            )
            ccd = tmp_path / "kit.ccd"
            packed = run("pack", str(src / "kit"), "-o", str(ccd), "--title", "Kit")
            self.assertEqual(packed.returncode, 0, packed.stderr)
            self.assertTrue(ccd.is_file())

            outlined = run("outline", str(ccd), "-d", "1")
            self.assertEqual(outlined.returncode, 0, outlined.stderr)
            self.assertIn("kit 1 Finished kit is the quality bar.", outlined.stdout)
            self.assertNotIn("kit.socket", outlined.stdout)

            deep = run("outline", str(ccd), "-d", "2")
            self.assertIn("kit.socket 2 Child pivot named by the build prompt.", deep.stdout)

            expanded = run("expand", str(ccd), "kit.socket")
            self.assertEqual(expanded.returncode, 0, expanded.stderr)
            self.assertIn("Pivot at the grip.", expanded.stdout)
            self.assertIn("inferred: true", expanded.stdout)

            missing = run("expand", str(ccd), "nope")
            self.assertEqual(missing.returncode, 1)

            found = run("search", str(ccd), "contact")
            self.assertEqual(found.returncode, 0, found.stderr)
            self.assertIn("kit", found.stdout)
            none = run("search", str(ccd), "zzznone")
            self.assertEqual(none.returncode, 1)

            valid = run("validate", str(ccd))
            self.assertEqual(valid.returncode, 0, valid.stderr)
            self.assertIn("ok", valid.stdout)

            collapsed_path = tmp_path / "collapsed.ccd"
            collapsed = run("collapse", str(ccd), "kit", "-o", str(collapsed_path))
            self.assertEqual(collapsed.returncode, 0, collapsed.stderr)
            stored = collapsed_path.read_text(encoding="utf-8")
            self.assertIn("fold: collapsed", stored)
            self.assertIn("store:", stored)
            still = run("expand", str(collapsed_path), "kit")
            self.assertIn("Match the contact sheet.", still.stdout)

            restored = tmp_path / "restored.ccd"
            back = run("expand", str(collapsed_path), "--all", "-o", str(restored))
            self.assertEqual(back.returncode, 0, back.stderr)
            self.assertEqual(
                restored.read_text(encoding="utf-8"),
                ccd.read_text(encoding="utf-8"),
            )

            unpacked = tmp_path / "out"
            unpack = run("unpack", str(ccd), "-o", str(unpacked))
            self.assertEqual(unpack.returncode, 0, unpack.stderr)
            files = list(unpacked.rglob("*.md"))
            self.assertEqual(len(files), 2)
            repacked = tmp_path / "again.ccd"
            again = run("pack", str(unpacked), "-o", str(repacked), "--title", "Kit")
            self.assertEqual(again.returncode, 0, again.stderr)
            self.assertEqual(
                repacked.read_text(encoding="utf-8"),
                ccd.read_text(encoding="utf-8"),
            )

            blocked = run("unpack", str(ccd), "-o", str(unpacked))
            self.assertEqual(blocked.returncode, 1)

    def test_json_pack(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "tree.json"
            src.write_text(
                '{"title":"J","nodes":[{"id":"a","parent":null,"summary":"A.","src":"-","see":[],"inferred":false,"body":"body"}]}',
                encoding="utf-8",
            )
            out = Path(tmp) / "j.ccd"
            result = run("pack", str(src), "-o", str(out))
            self.assertEqual(result.returncode, 0, result.stderr)
            unpacked = Path(tmp) / "j.json"
            back = run("unpack", str(out), "-o", str(unpacked), "--json")
            self.assertEqual(back.returncode, 0, back.stderr)
            self.assertIn('"id": "a"', unpacked.read_text(encoding="utf-8"))

    def test_validate_bad_version(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "bad.ccd"
            bad.write_text("ccd 9\ntitle: X\nnodes: 0\nindex:\n.\n", encoding="utf-8")
            result = run("validate", str(bad))
            self.assertEqual(result.returncode, 1)
            self.assertIn("version", result.stderr)


if __name__ == "__main__":
    unittest.main()
