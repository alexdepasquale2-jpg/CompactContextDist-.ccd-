"""Behavior contract for Compact Context Distributable (.ccd)."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from ccd import (
    CcdError,
    Document,
    Node,
    collapse_document,
    expand_document,
    outline_lines,
    pack_json,
    pack_markdown,
    parse,
    problems,
    read_index,
    render,
    search_document,
    unpack_json,
    unpack_markdown,
)

ROOT = Path(__file__).resolve().parents[1]


def N(
    id: str,
    parent: str | None,
    summary: str,
    body: str,
    *,
    src: str = "-",
    see: tuple[str, ...] = (),
    inferred: bool = False,
    fold: str = "expanded",
) -> Node:
    return Node(id, parent, summary, src, see, inferred, body, fold)  # type: ignore[arg-type]


def fixture() -> Document:
    return Document(
        title="Fixture",
        nodes=(
            N(
                "root",
                None,
                "Top of the fixture.",
                "Hello.\n\n. not a terminator\n  spaced\nnode decoy\n[[root.child]]\n",
                src="src/a.md",
                see=("root.child",),
            ),
            N(
                "root.child",
                "root",
                "Nested child.",
                "café 日本語\n\tindented\n",
                src="src/a.md:4",
                see=("root",),
                inferred=True,
            ),
            N("other", None, "Second root.", ""),
        ),
    )


def logical(doc: Document) -> tuple[object, ...]:
    expanded = tuple(
        Node(n.id, n.parent, n.summary, n.src, n.see, n.inferred, n.body, "expanded")
        for n in doc.nodes
    )
    return (doc.version, doc.title, expanded)


class FormatTests(unittest.TestCase):
    def test_render_parse_round_trip(self) -> None:
        doc = fixture()
        text = render(doc)
        self.assertTrue(text.endswith("\n"))
        self.assertNotIn("\r", text)
        again = parse(text)
        self.assertEqual(logical(again), logical(doc))
        self.assertEqual(render(again), text)
        self.assertEqual(problems(again), [])

    def test_index_is_the_cheap_header(self) -> None:
        text = render(fixture())
        title, count, rows = read_index(text)
        self.assertEqual(title, "Fixture")
        self.assertEqual(count, 3)
        self.assertEqual(
            rows,
            (
                ("root", 1, "Top of the fixture."),
                ("root.child", 2, "Nested child."),
                ("other", 1, "Second root."),
            ),
        )
        # A broken body does not stop a header read.
        broken = text.replace("parent: root", "parent: NOT-A-FIELD", 1)
        self.assertEqual(read_index(broken)[2][1][0], "root.child")
        with self.assertRaises(CcdError):
            parse(broken)

    def test_outline_depth_uses_index_not_rewritten_body(self) -> None:
        text = render(fixture())
        corrupted = text.replace("summary: Nested child.", "summary: CHANGED.", 1)
        self.assertIn("CHANGED", corrupted)
        shown = outline_lines(corrupted, depth=1)
        self.assertIn("root 1 Top of the fixture.", shown)
        self.assertNotIn("root.child", shown)
        self.assertNotIn("CHANGED", shown)
        self.assertTrue(any("index" in item for item in problems(parse(corrupted))))

    def test_empty_document(self) -> None:
        doc = Document(title="Empty", nodes=())
        text = render(doc)
        self.assertEqual(logical(parse(text)), logical(doc))
        self.assertEqual(read_index(text)[1], 0)

    def test_body_edges(self) -> None:
        bodies = ["", "a", "a\n", "a\n\n", "\n", " .", ".", "  x", "line\n. \nnode z\n"]
        for body in bodies:
            doc = Document(title="B", nodes=(N("solo", None, "One line.", body),))
            self.assertEqual(parse(render(doc)).nodes[0].body, body)

    def test_collapse_expand_keeps_bodies(self) -> None:
        doc = fixture()
        original = render(doc)
        one = collapse_document(doc, "root.child")
        stored = render(one)
        self.assertIn("fold: collapsed", stored)
        self.assertIn("\nstore:\n", stored)
        self.assertNotIn("café", stored.split("store:", 1)[0])
        self.assertEqual(parse(stored).nodes[1].body, doc.nodes[1].body)
        self.assertEqual(parse(stored).nodes[0].fold, "expanded")
        back = render(expand_document(parse(stored), None))
        self.assertEqual(back, original)
        all_collapsed = render(collapse_document(doc, None))
        self.assertEqual(render(expand_document(parse(all_collapsed), None)), original)

    def test_search_finds_summary_and_stored_body(self) -> None:
        doc = collapse_document(fixture(), "root.child")
        hits = search_document(doc, "CAFÉ")
        self.assertEqual(hits[0].node_id, "root.child")
        self.assertEqual(hits[0].field, "body")
        summary_hits = search_document(doc, "second root")
        self.assertEqual(summary_hits[0].field, "summary")
        self.assertEqual(search_document(doc, "no-such-token"), ())

    def test_json_round_trip_reorders_to_preorder(self) -> None:
        payload = {
            "title": "Tree",
            "nodes": [
                {
                    "id": "world.look",
                    "parent": "world",
                    "summary": "Look lock.",
                    "src": "spec.md:1",
                    "see": ["world"],
                    "inferred": True,
                    "body": "Vertex lit.\n",
                },
                {
                    "id": "world",
                    "parent": None,
                    "summary": "World spec.",
                    "src": "-",
                    "see": [],
                    "inferred": False,
                    "body": "[[world.look]]\n",
                },
            ],
        }
        doc = pack_json(json.dumps(payload))
        self.assertEqual([n.id for n in doc.nodes], ["world", "world.look"])
        text = unpack_json(doc)
        again = pack_json(text)
        self.assertEqual(logical(again), logical(doc))
        self.assertEqual(unpack_json(again), text)
        self.assertEqual(problems(parse(render(doc))), [])

    def test_markdown_round_trip(self) -> None:
        doc = fixture()
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "docs"
            unpack_markdown(doc, out)
            packed = pack_markdown([out], "Fixture")
            self.assertEqual(logical(packed), logical(doc))
            self.assertEqual(render(packed), render(doc))
            second = Path(tmp) / "docs2"
            unpack_markdown(packed, second)
            names = sorted(p.relative_to(out).as_posix() for p in out.rglob("*.md"))
            names2 = sorted(p.relative_to(second).as_posix() for p in second.rglob("*.md"))
            self.assertEqual(names, names2)
            for rel in names:
                self.assertEqual((out / rel).read_text(encoding="utf-8"), (second / rel).read_text(encoding="utf-8"))

    def test_markdown_derives_missing_frontmatter(self) -> None:
        long_line = "L" * 250
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder = root / "notes"
            folder.mkdir()
            (folder / "_index.md").write_text("# Notes\n\nParent body.\n", encoding="utf-8")
            (folder / "01-page.md").write_text(long_line + "\n\nRest.\n", encoding="utf-8")
            doc = pack_markdown([folder], "Notes")
            self.assertEqual([n.id for n in doc.nodes], ["notes", "notes.page"])
            self.assertEqual(doc.nodes[0].summary, "Notes")
            self.assertEqual(len(doc.nodes[1].summary), 200)
            self.assertTrue(doc.nodes[1].summary.endswith("..."))
            self.assertIn(long_line, doc.nodes[1].body)
            self.assertEqual(doc.nodes[1].parent, "notes")

    def test_missing_parent_is_an_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "orphan"
            folder.mkdir()
            (folder / "01-only.md").write_text(
                "---\nid: kit.socket\nparent: kit\nsummary: Socket.\nsrc: -\nsee: -\ninferred: false\n---\nGrip.\n",
                encoding="utf-8",
            )
            with self.assertRaises(CcdError):
                pack_markdown([folder], "Bad")

    def test_validate_catches_semantic_damage(self) -> None:
        text = render(fixture())
        # Point a cross-reference at a node that does not exist.
        damaged = text.replace("see: root.child", "see: root.missing", 1)
        errs = problems(parse(damaged))
        self.assertTrue(any("root.missing" in item for item in errs))

        cycle = (
            "ccd 1\n"
            "title: Cycle\n"
            "nodes: 2\n"
            "index:\n"
            "a 1 A.\n"
            "b 1 B.\n"
            ".\n"
            "node a\n"
            "parent: b\n"
            "summary: A.\n"
            "src: -\n"
            "see: -\n"
            "inferred: false\n"
            "fold: expanded\n"
            "body:\n"
            " .\n"
            ".\n"
            "node b\n"
            "parent: a\n"
            "summary: B.\n"
            "src: -\n"
            "see: -\n"
            "inferred: false\n"
            "fold: expanded\n"
            "body:\n"
            " .\n"
            ".\n"
        )
        errs = problems(parse(cycle))
        self.assertTrue(errs)

        self_see = render(
            Document(title="S", nodes=(N("solo", None, "Self.", "x", see=("solo",)),))
        )
        self.assertTrue(any("itself" in item for item in problems(parse(self_see))))

    def test_syntax_rejections(self) -> None:
        good = render(fixture())
        with self.assertRaises(CcdError):
            parse("\ufeff" + good)
        with self.assertRaises(CcdError):
            parse(good.replace("\n", "\r\n"))
        with self.assertRaises(CcdError):
            parse(good.replace("ccd 1", "ccd 2", 1))
        with self.assertRaises(CcdError):
            parse(good.replace("ccd 1\n", "ccd 1\nextra: no\n", 1))
        # Drop the store entry but mark a node collapsed.
        collapsed = render(collapse_document(fixture(), "other"))
        self.assertIn("store:", collapsed)
        chopped = collapsed.split("store:", 1)[0]
        with self.assertRaises(CcdError):
            parse(chopped if chopped.endswith("\n") else chopped + "\n")

    def test_summary_limit(self) -> None:
        ok = Document(title="T", nodes=(N("solo", None, "x" * 200, "b"),))
        self.assertEqual(problems(parse(render(ok))), [])
        bad = render(ok).replace("x" * 200, "x" * 201)
        self.assertTrue(any("summary" in item for item in problems(parse(bad))))

    def test_spec_example_validates(self) -> None:
        spec = (ROOT / "SPEC.md").read_text(encoding="utf-8")
        start = spec.index("```ccd\n") + len("```ccd\n")
        example = spec[start : spec.index("```", start)]
        self.assertTrue(example.endswith("\n"))
        doc = parse(example)
        self.assertEqual(problems(doc), [])
        self.assertEqual(read_index(example)[1], len(doc.nodes))
        self.assertIn("kit.socket", example)


if __name__ == "__main__":
    unittest.main()
