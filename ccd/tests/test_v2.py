"""Version 2 codebook, version 1 compatibility, and zip."""

from __future__ import annotations

import unittest
from pathlib import Path

from ccd import (
    Document,
    Node,
    decode_v2,
    encode_v2,
    estimate_tokens,
    pack_markdown,
    parse,
    problems,
    render,
    unzip_bytes,
    zip_text,
)
from ccd.compact import _restore_defaults, _strip_defaults

ROOT = Path(__file__).resolve().parents[1]
AGENTS = ROOT.parent / "agents"


def _node(body: str, *, inferred: bool = False, fold: str = "expanded") -> Document:
    return Document(
        title="T",
        nodes=(
            Node("solo", None, "One line.", "-", (), inferred, body, fold),  # type: ignore[arg-type]
        ),
    )


class Version2Tests(unittest.TestCase):
    def test_round_trip_is_exact_v1_text(self) -> None:
        doc = pack_markdown([AGENTS / "evidence", AGENTS / "protocols"], "Seedforge")
        v1 = render(doc, version=1)
        v2 = render(doc, version=2)
        self.assertTrue(v2.startswith("ccd 2\n"))
        self.assertIn("codebook: inline\n", v2)
        self.assertLess(estimate_tokens(v2), estimate_tokens(v1))
        self.assertEqual(decode_v2(v2), v1)
        self.assertEqual(problems(parse(v2)), [])
        self.assertEqual(render(parse(v2)), v2)

    def test_real_tokenizers_when_installed(self) -> None:
        try:
            import tiktoken
        except ImportError:
            self.skipTest("tiktoken is not installed")
        doc = pack_markdown([AGENTS / "evidence", AGENTS / "protocols"], "Seedforge")
        v1 = render(doc, version=1)
        v2 = render(doc, version=2)
        for name in ("cl100k_base", "o200k_base"):
            enc = tiktoken.get_encoding(name)
            self.assertLess(len(enc.encode(v2)), len(enc.encode(v1)), name)

    def test_v1_file_still_parses(self) -> None:
        v1 = render(_node("Hello.\n"), version=1)
        self.assertTrue(v1.startswith("ccd 1\n"))
        self.assertEqual(parse(v1).version, 1)
        self.assertEqual(parse(v1).nodes[0].body, "Hello.\n")

    def test_codebook_does_not_eat_a_longer_word(self) -> None:
        # "is the" is a frequent bigram. "is there" must survive the round trip.
        body = "\n".join(["is the place" for _ in range(24)] + ["is there"]) + "\n"
        v1 = render(_node(body), version=1)
        v2 = encode_v2(v1)
        self.assertTrue(v2.startswith("ccd 2\n"), "the repeated phrase should pay for a codebook")
        self.assertEqual(decode_v2(v2), v1)
        self.assertIn("is there", decode_v2(v2))

    def test_defaults_restore_collapsed_and_inferred(self) -> None:
        v1 = render(
            Document(
                title="T",
                nodes=(
                    Node("a", None, "A.", "-", ("b",), False, "plain\n", "expanded"),
                    Node("b", "a", "B.", "-", (), True, "kept\n", "collapsed"),
                ),
            ),
            version=1,
        )
        stripped = _strip_defaults(v1)
        self.assertNotIn("\ninferred: false\n", "\n" + stripped)
        self.assertIn("inferred: true", stripped)
        self.assertIn("fold: collapsed", stripped)
        self.assertEqual(_restore_defaults(stripped), v1)

    def test_external_codebook(self) -> None:
        v1 = render(_node("This supersedes the old brief.\n"), version=1)
        self.assertNotIn("→", v1)
        body = v1.replace("supersedes", "→")
        v2 = "ccd 2\ncodebook: ext:relations\n.\n" + body
        self.assertEqual(decode_v2(v2, root=ROOT), v1)
        self.assertIn("supersedes", parse(v2).nodes[0].body)

    def test_unknown_version_still_fails(self) -> None:
        from ccd import CcdError

        with self.assertRaises(CcdError):
            parse("ccd 9\ntitle: X\nnodes: 0\nindex:\n.\n")

    def test_zip_round_trip_raw_and_armor(self) -> None:
        text = render(_node("zip me\n"), version=1)
        raw = zip_text(text)
        self.assertEqual(unzip_bytes(raw), text)
        armor = zip_text(text, armor=True)
        self.assertTrue(armor.startswith(b"ccd-zip 1\n"))
        self.assertTrue(all(byte < 128 for byte in armor))
        self.assertEqual(unzip_bytes(armor), text)


if __name__ == "__main__":
    unittest.main()
