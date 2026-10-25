"""Pack a Seedforge report folder and focus the context node.

The comparison is the handoff read. Whole-markdown is every report file,
spec.md, and the handoff packet. Focus is map, find, the context node, the
spec section that context names, and the same packet.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

try:
    import tiktoken
except ImportError:
    tiktoken = None

ROOT = Path(__file__).resolve().parents[1]

CONTEXT_LINE = "CONTEXTLINEUNIQUE fog bell on the pier"
LOCK_LINE = "LOCKLINEUNIQUE one figure, no crowd, dusk fog"
PROCESS_FILLER = "PROCESSFILLERUNIQUE steps commands and exit codes for the pier bell"
NOTES_FILLER = "NOTESFILLERUNIQUE rejected a crowd and a second bell"
SPEC_NOISE = "SPECNOISEUNIQUE delivery rows sockets budgets and audio that the handoff does not need"
PACKET = "Packet\nLook lock is 2. Look lock.\n\nQuestion\nNone.\n\nNext\nBuild the bell.\n"


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "ccd", *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def _o200k(text: str) -> int:
    if tiktoken is None:
        raise unittest.SkipTest("tiktoken is not installed")
    return len(tiktoken.get_encoding("o200k_base").encode(text))


def _report(folder: Path) -> None:
    filler = (PROCESS_FILLER + " ") * 400
    notes = (NOTES_FILLER + " ") * 400
    (folder / "_index.md").write_text(
        "---\n"
        "id: report\n"
        "parent: -\n"
        "summary: Run record. Process, notes, and context for the next agent.\n"
        "src: -\n"
        "see: report.process report.notes report.context\n"
        "inferred: false\n"
        "---\n"
        "\n"
        "Replace this folder's three nodes before you pack the run.\n",
        encoding="utf-8",
    )
    (folder / "01-process.md").write_text(
        "---\n"
        "id: report.process\n"
        "parent: report\n"
        "summary: Steps in order, with files, commands, and skipped steps.\n"
        "src: -\n"
        "see: -\n"
        "inferred: false\n"
        "---\n"
        "\n"
        f"{filler}\n",
        encoding="utf-8",
    )
    (folder / "02-notes.md").write_text(
        "---\n"
        "id: report.notes\n"
        "parent: report\n"
        "summary: Creative decisions, rejected alternatives, and inferences.\n"
        "src: -\n"
        "see: -\n"
        "inferred: false\n"
        "---\n"
        "\n"
        f"{notes}\n",
        encoding="utf-8",
    )
    (folder / "03-context.md").write_text(
        "---\n"
        "id: report.context\n"
        "parent: report\n"
        "summary: Seed, look lock, ids, paths, and the next build step.\n"
        "src: -\n"
        "see: -\n"
        "inferred: false\n"
        "---\n"
        "\n"
        "- Seed: fog bell\n"
        "- Look lock: 2. Look lock\n"
        f"{CONTEXT_LINE}\n",
        encoding="utf-8",
    )


def _spec(path: Path) -> None:
    noise = (SPEC_NOISE + " ") * 400
    path.write_text(
        "# Fog bell\n"
        "\n"
        "## 1. Seed\n"
        "\n"
        f"{noise}\n"
        "\n"
        "## 2. Look lock\n"
        "\n"
        f"{LOCK_LINE}\n"
        "\n"
        "## 3. Delivery\n"
        "\n"
        f"{noise}\n",
        encoding="utf-8",
    )


class HandoffTests(unittest.TestCase):
    def test_pack_report_and_focus_context(self) -> None:
        if tiktoken is None:
            self.skipTest("tiktoken is not installed")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = root / "2026-10-25-fog-bell"
            report.mkdir()
            _report(report)
            spec = root / "spec.md"
            _spec(spec)
            packet = PACKET

            run_ccd = report / "run.ccd"
            packed = run(
                "pack",
                str(report),
                "-o",
                str(run_ccd),
                "--title",
                "2026-10-25-fog-bell",
            )
            self.assertEqual(packed.returncode, 0, packed.stderr)
            self.assertTrue(run_ccd.read_text(encoding="utf-8").startswith("ccd 3\n"))
            valid = run("validate", str(run_ccd))
            self.assertEqual(valid.returncode, 0, valid.stderr)

            mapped = run("map", str(run_ccd))
            self.assertEqual(mapped.returncode, 0, mapped.stderr)
            self.assertNotIn(PROCESS_FILLER, mapped.stdout)

            found = run("find", str(run_ccd), "context")
            self.assertEqual(found.returncode, 0, found.stderr)
            self.assertTrue(found.stdout.startswith("report.context "))

            focused = run("focus", str(run_ccd), "report.context")
            self.assertEqual(focused.returncode, 0, focused.stderr)
            self.assertIn(CONTEXT_LINE, focused.stdout)
            self.assertNotIn(PROCESS_FILLER, focused.stdout)
            self.assertNotIn(NOTES_FILLER, focused.stdout)

            spec_ccd = root / "spec.ccd"
            spec_pack = run("pack", str(spec), "-o", str(spec_ccd), "--title", "fog bell spec")
            self.assertEqual(spec_pack.returncode, 0, spec_pack.stderr)
            spec_text = spec_ccd.read_text(encoding="utf-8")
            self.assertTrue(spec_text.startswith("ccd 3\n"))
            self.assertIn("\nnode spec\n", spec_text)
            self.assertNotIn("node spec.spec", spec_text)
            spec_valid = run("validate", str(spec_ccd))
            self.assertEqual(spec_valid.returncode, 0, spec_valid.stderr)

            section = run("focus", str(spec_ccd), "spec", "--section", "2. Look lock")
            self.assertEqual(section.returncode, 0, section.stderr)
            self.assertIn(LOCK_LINE, section.stdout)
            self.assertNotIn(SPEC_NOISE, section.stdout)

            whole = "\n".join(
                path.read_text(encoding="utf-8")
                for path in sorted(report.glob("*.md"))
            )
            whole = whole + "\n" + spec.read_text(encoding="utf-8") + "\n" + packet
            loaded = mapped.stdout + found.stdout + focused.stdout + section.stdout + packet
            before = _o200k(whole)
            after = _o200k(loaded)
            sys.__stdout__.write(
                f"handoff read tokens o200k whole-markdown={before} focus={after}\n"
            )
            self.assertLess(after, before)
            self.assertLess(after * 5, before)

    def test_dated_report_folder_without_ids_uses_the_filename(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            report = Path(tmp) / "2026-10-25-fog-bell"
            report.mkdir()
            (report / "notes.md").write_text("# Note\n\nA note with no id.\n", encoding="utf-8")
            dest = Path(tmp) / "run.ccd"
            packed = run("pack", str(report), "-o", str(dest), "--title", "fog")
            self.assertEqual(packed.returncode, 0, packed.stderr)
            text = dest.read_text(encoding="utf-8")
            self.assertIn("\nnode notes\n", text)
            self.assertNotIn("invalid path segment", packed.stderr)


if __name__ == "__main__":
    unittest.main()
