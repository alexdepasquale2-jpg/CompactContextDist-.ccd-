"""Parse and render canonical .ccd text."""

from __future__ import annotations

import re

from ccd.compact import decode_v2, encode_v2
from ccd.model import (
    VERSION,
    ID_RE,
    CcdError,
    Document,
    Fold,
    Node,
    build_index,
    build_index_v3,
)

_INT = re.compile(r"^(0|[1-9][0-9]*)$")
_DEPTH = re.compile(r"^[1-9][0-9]*$")


def _lines(text: str) -> list[tuple[int, str]]:
    if text.startswith("\ufeff"):
        raise CcdError("BOM is not allowed")
    if "\r" in text:
        raise CcdError("CR is not allowed; use LF")
    if not text.endswith("\n"):
        raise CcdError("file must end with a newline")
    return list(enumerate(text.split("\n")[:-1], start=1))


class _Parser:
    def __init__(self, text: str) -> None:
        self.lines = _lines(text)
        self.index = 0

    def done(self) -> bool:
        return self.index >= len(self.lines)

    def peek(self) -> tuple[int, str]:
        if self.done():
            raise CcdError("unexpected end of file")
        return self.lines[self.index]

    def take(self) -> tuple[int, str]:
        line = self.peek()
        self.index += 1
        return line

    def expect(self, value: str) -> None:
        lineno, line = self.take()
        if line != value:
            raise CcdError(f"expected {value!r}", lineno)


def _structural(lineno: int, line: str) -> str:
    if line != line.rstrip():
        raise CcdError("trailing whitespace", lineno)
    return line


def _value(lineno: int, line: str, key: str) -> str:
    prefix = f"{key}: "
    if not line.startswith(prefix):
        raise CcdError(f"expected {key}", lineno)
    return line[len(prefix) :]


def _parent(lineno: int, value: str) -> str | None:
    if value == "-":
        return None
    if not ID_RE.match(value):
        raise CcdError(f"invalid parent {value}", lineno)
    return value


def _see(lineno: int, value: str, field: str = "see") -> tuple[str, ...]:
    if value == "-":
        return ()
    if value != value.strip() or "  " in value or value == "":
        raise CcdError(f"{field} must be '-' or single-spaced ids", lineno)
    refs = tuple(value.split(" "))
    for ref in refs:
        if not ID_RE.match(ref):
            raise CcdError(f"invalid {field} id {ref}", lineno)
    return refs


def _bool(lineno: int, value: str) -> bool:
    if value == "true":
        return True
    if value == "false":
        return False
    raise CcdError("inferred must be true or false", lineno)


def _fold(lineno: int, value: str) -> Fold:
    if value == "expanded" or value == "collapsed":
        return value
    raise CcdError("fold must be expanded or collapsed", lineno)


def _read_body(parser: _Parser) -> str:
    parts: list[str] = []
    while True:
        lineno, line = parser.take()
        if line == ".":
            return "\n".join(parts) if parts else ""
        if not line.startswith(" "):
            raise CcdError("body line must start with a space", lineno)
        parts.append(line[1:])


def _read_header(parser: _Parser) -> tuple[str, int, tuple[tuple[str, int, str], ...]]:
    _take_version(parser, VERSION)

    lineno, line = parser.take()
    title = _value(lineno, _structural(lineno, line), "title")
    if title == "" or _controls(title):
        raise CcdError("invalid title", lineno)

    lineno, line = parser.take()
    count_text = _value(lineno, _structural(lineno, line), "nodes")
    if not _INT.match(count_text):
        raise CcdError("invalid nodes count", lineno)
    declared = int(count_text)

    parser.expect("index:")
    rows: list[tuple[str, int, str]] = []
    while True:
        lineno, line = parser.take()
        line = _structural(lineno, line)
        if line == ".":
            break
        parts = line.split(" ", 2)
        if len(parts) != 3:
            raise CcdError("index line needs id, depth, summary", lineno)
        node_id, depth_text, summary = parts
        if not ID_RE.match(node_id):
            raise CcdError("invalid index id", lineno)
        if not _DEPTH.match(depth_text):
            raise CcdError("invalid index depth", lineno)
        if summary == "" or summary != summary.strip() or _controls(summary):
            raise CcdError("invalid index summary", lineno)
        rows.append((node_id, int(depth_text), summary))
    if len(rows) != declared:
        raise CcdError(f"nodes: {declared} but index has {len(rows)} entries")
    return title, declared, tuple(rows)


def _controls(text: str) -> bool:
    return any(ord(char) < 32 for char in text)


def _take_version(parser: _Parser, expected: int) -> None:
    lineno, line = parser.take()
    line = _structural(lineno, line)
    match = re.match(r"^ccd ([1-9][0-9]*)$", line)
    if match is None:
        raise CcdError("first line must be 'ccd <version>'", lineno)
    version = int(match.group(1))
    if version != expected:
        raise CcdError(f"unsupported version {version}", lineno)


def _read_title_count(parser: _Parser) -> tuple[str, int]:
    lineno, line = parser.take()
    title = _value(lineno, _structural(lineno, line), "title")
    if title == "" or _controls(title):
        raise CcdError("invalid title", lineno)

    lineno, line = parser.take()
    count_text = _value(lineno, _structural(lineno, line), "nodes")
    if not _INT.match(count_text):
        raise CcdError("invalid nodes count", lineno)
    return title, int(count_text)


def read_index(text: str) -> tuple[str, int, tuple[tuple[str, int, str], ...] | tuple[tuple[str, int, int, str], ...]]:
    """Read only the header index. Does not parse node bodies.

    A version 2 file is decoded first, so the rows are the plain summaries.
    A version 3 row is id, depth, body-token estimate, summary.
    """
    if text.startswith("ccd 2\n"):
        text = decode_v2(text)
    if text.startswith("ccd 3\n"):
        return _read_header_v3(_Parser(text))
    return _read_header(_Parser(text))


def _read_header_v3(parser: _Parser) -> tuple[str, int, tuple[tuple[str, int, int, str], ...]]:
    _take_version(parser, 3)
    title, declared = _read_title_count(parser)
    parser.expect("index:")
    rows: list[tuple[str, int, int, str]] = []
    while True:
        lineno, line = parser.take()
        line = _structural(lineno, line)
        if line == ".":
            break
        parts = line.split(" ", 3)
        if len(parts) != 4:
            raise CcdError("index line needs id, depth, tokens, summary", lineno)
        node_id, depth_text, token_text, summary = parts
        if not ID_RE.match(node_id):
            raise CcdError("invalid index id", lineno)
        if not _DEPTH.match(depth_text):
            raise CcdError("invalid index depth", lineno)
        if not _INT.match(token_text):
            raise CcdError("invalid index token count", lineno)
        if summary == "" or summary != summary.strip() or _controls(summary):
            raise CcdError("invalid index summary", lineno)
        rows.append((node_id, int(depth_text), int(token_text), summary))
    if len(rows) != declared:
        raise CcdError(f"nodes: {declared} but index has {len(rows)} entries")
    return title, declared, tuple(rows)


def _read_node(parser: _Parser, *, version: int) -> Node:
    lineno, line = parser.take()
    line = _structural(lineno, line)
    if not line.startswith("node "):
        raise CcdError("expected node", lineno)
    node_id = line[len("node ") :]
    if not ID_RE.match(node_id):
        raise CcdError(f"invalid id {node_id}", lineno)

    lineno, line = parser.take()
    parent = _parent(lineno, _value(lineno, _structural(lineno, line), "parent"))
    lineno, line = parser.take()
    summary = _value(lineno, _structural(lineno, line), "summary")
    if summary == "" or _controls(summary) or summary != summary.strip():
        raise CcdError("invalid summary", lineno)
    lineno, line = parser.take()
    src = _value(lineno, _structural(lineno, line), "src")
    if src == "" or _controls(src):
        raise CcdError("invalid src", lineno)
    lineno, line = parser.take()
    see = _see(lineno, _value(lineno, _structural(lineno, line), "see"))
    requires: tuple[str, ...] = ()
    supersedes: tuple[str, ...] = ()
    derived_from: tuple[str, ...] = ()
    if version == 3:
        lineno, line = parser.take()
        requires = _see(lineno, _value(lineno, _structural(lineno, line), "requires"), "requires")
        lineno, line = parser.take()
        supersedes = _see(lineno, _value(lineno, _structural(lineno, line), "supersedes"), "supersedes")
        lineno, line = parser.take()
        derived_from = _see(
            lineno, _value(lineno, _structural(lineno, line), "derived-from"), "derived-from"
        )
    elif version == VERSION:
        pass
    else:
        raise CcdError(f"unhandled version {version}")
    lineno, line = parser.take()
    inferred = _bool(lineno, _value(lineno, _structural(lineno, line), "inferred"))
    lineno, line = parser.take()
    fold = _fold(lineno, _value(lineno, _structural(lineno, line), "fold"))

    body = ""
    if fold == "expanded":
        parser.expect("body:")
        body = _read_body(parser)
    elif fold == "collapsed":
        parser.expect(".")
        body = ""
    else:
        raise CcdError(f"unhandled fold {fold}", lineno)
    return Node(
        node_id,
        parent,
        summary,
        src,
        see,
        inferred,
        body,
        fold,
        requires,
        supersedes,
        derived_from,
    )


def parse(text: str) -> Document:
    if text.startswith("ccd 2\n"):
        text = decode_v2(text)
        doc = _parse_v1(text)
        if doc.version == 2:
            return doc
        return Document(doc.title, doc.nodes, 2, doc.index, doc.declared_nodes)
    if text.startswith("ccd 3\n"):
        return _parse_v3(text)
    return _parse_v1(text)


def _parse_v1(text: str) -> Document:
    parser = _Parser(text)
    title, declared, index = _read_header(parser)
    nodes: list[Node] = []
    while not parser.done() and parser.peek()[1].startswith("node "):
        nodes.append(_read_node(parser, version=VERSION))
    collapsed = [node.id for node in nodes if node.fold == "collapsed"]
    bodies: dict[str, str] = {}
    if collapsed:
        parser.expect("store:")
        seen: list[str] = []
        while not parser.done() and parser.peek()[1].startswith("node "):
            lineno, line = parser.take()
            line = _structural(lineno, line)
            node_id = line[len("node ") :]
            if not ID_RE.match(node_id):
                raise CcdError(f"invalid store id {node_id}", lineno)
            parser.expect("body:")
            bodies[node_id] = _read_body(parser)
            seen.append(node_id)
        parser.expect(".")
        if seen != collapsed:
            raise CcdError("store nodes must match collapsed nodes in order")
    elif not parser.done():
        lineno, line = parser.peek()
        raise CcdError(f"unexpected trailing content {line!r}", lineno)
    if not parser.done():
        lineno, line = parser.peek()
        raise CcdError(f"unexpected trailing content {line!r}", lineno)

    filled: list[Node] = []
    for node in nodes:
        if node.fold == "collapsed":
            filled.append(
                Node(
                    node.id,
                    node.parent,
                    node.summary,
                    node.src,
                    node.see,
                    node.inferred,
                    bodies[node.id],
                    "collapsed",
                    node.requires,
                    node.supersedes,
                    node.derived_from,
                )
            )
        elif node.fold == "expanded":
            filled.append(node)
        else:
            raise CcdError(f"unhandled fold {node.fold}")
    return Document(
        title=title,
        nodes=tuple(filled),
        version=VERSION,
        index=index,
        declared_nodes=declared,
    )


def _parse_v3(text: str) -> Document:
    parser = _Parser(text)
    title, declared, index = _read_header_v3(parser)
    nodes: list[Node] = []
    while not parser.done() and parser.peek()[1].startswith("node "):
        nodes.append(_read_node(parser, version=3))
    collapsed = [node.id for node in nodes if node.fold == "collapsed"]
    bodies: dict[str, str] = {}
    if collapsed:
        parser.expect("store:")
        seen: list[str] = []
        while not parser.done() and parser.peek()[1].startswith("node "):
            lineno, line = parser.take()
            line = _structural(lineno, line)
            node_id = line[len("node ") :]
            if not ID_RE.match(node_id):
                raise CcdError(f"invalid store id {node_id}", lineno)
            parser.expect("body:")
            bodies[node_id] = _read_body(parser)
            seen.append(node_id)
        parser.expect(".")
        if seen != collapsed:
            raise CcdError("store nodes must match collapsed nodes in order")
    elif not parser.done():
        lineno, line = parser.peek()
        raise CcdError(f"unexpected trailing content {line!r}", lineno)
    if not parser.done():
        lineno, line = parser.peek()
        raise CcdError(f"unexpected trailing content {line!r}", lineno)

    filled: list[Node] = []
    for node in nodes:
        if node.fold == "collapsed":
            filled.append(
                Node(
                    node.id,
                    node.parent,
                    node.summary,
                    node.src,
                    node.see,
                    node.inferred,
                    bodies[node.id],
                    "collapsed",
                    node.requires,
                    node.supersedes,
                    node.derived_from,
                )
            )
        elif node.fold == "expanded":
            filled.append(node)
        else:
            raise CcdError(f"unhandled fold {node.fold}")
    return Document(
        title=title,
        nodes=tuple(filled),
        version=3,
        index=index,
        declared_nodes=declared,
    )


def _body_parts(body: str) -> list[str]:
    if body == "":
        return []
    return body.split("\n")


def render(doc: Document, *, version: int | None = None) -> str:
    """Render version 1, version 3, or version 2 as a lossless encoding of version 1."""
    chosen = doc.version if version is None else version
    if chosen == VERSION:
        return _render_v1(doc)
    if chosen == 2:
        return encode_v2(_render_v1(doc))
    if chosen == 3:
        return _render_v3(doc)
    raise CcdError(f"unsupported version {chosen}")


def _render_v1(doc: Document) -> str:
    rows = build_index(doc.nodes)
    lines = [
        "ccd 1",
        f"title: {doc.title}",
        f"nodes: {len(doc.nodes)}",
        "index:",
    ]
    for node_id, depth, summary in rows:
        lines.append(f"{node_id} {depth} {summary}")
    lines.append(".")
    collapsed: list[Node] = []
    for node in doc.nodes:
        parent = "-" if node.parent is None else node.parent
        see = "-" if not node.see else " ".join(node.see)
        inferred = "true" if node.inferred else "false"
        lines.append(f"node {node.id}")
        lines.append(f"parent: {parent}")
        lines.append(f"summary: {node.summary}")
        lines.append(f"src: {node.src}")
        lines.append(f"see: {see}")
        lines.append(f"inferred: {inferred}")
        lines.append(f"fold: {node.fold}")
        if node.fold == "expanded":
            lines.append("body:")
            lines.extend(f" {part}" for part in _body_parts(node.body))
            lines.append(".")
        elif node.fold == "collapsed":
            lines.append(".")
            collapsed.append(node)
        else:
            raise CcdError(f"unhandled fold {node.fold}")
    if collapsed:
        lines.append("store:")
        for node in collapsed:
            lines.append(f"node {node.id}")
            lines.append("body:")
            lines.extend(f" {part}" for part in _body_parts(node.body))
            lines.append(".")
        lines.append(".")
    return "\n".join(lines) + "\n"


def _refs(refs: tuple[str, ...]) -> str:
    return "-" if not refs else " ".join(refs)


def _render_v3(doc: Document) -> str:
    rows = build_index_v3(doc.nodes)
    lines = [
        "ccd 3",
        f"title: {doc.title}",
        f"nodes: {len(doc.nodes)}",
        "index:",
    ]
    for node_id, depth, tokens, summary in rows:
        lines.append(f"{node_id} {depth} {tokens} {summary}")
    lines.append(".")
    collapsed: list[Node] = []
    for node in doc.nodes:
        parent = "-" if node.parent is None else node.parent
        see = _refs(node.see)
        inferred = "true" if node.inferred else "false"
        lines.append(f"node {node.id}")
        lines.append(f"parent: {parent}")
        lines.append(f"summary: {node.summary}")
        lines.append(f"src: {node.src}")
        lines.append(f"see: {see}")
        lines.append(f"requires: {_refs(node.requires)}")
        lines.append(f"supersedes: {_refs(node.supersedes)}")
        lines.append(f"derived-from: {_refs(node.derived_from)}")
        lines.append(f"inferred: {inferred}")
        lines.append(f"fold: {node.fold}")
        if node.fold == "expanded":
            lines.append("body:")
            lines.extend(f" {part}" for part in _body_parts(node.body))
            lines.append(".")
        elif node.fold == "collapsed":
            lines.append(".")
            collapsed.append(node)
        else:
            raise CcdError(f"unhandled fold {node.fold}")
    if collapsed:
        lines.append("store:")
        for node in collapsed:
            lines.append(f"node {node.id}")
            lines.append("body:")
            lines.extend(f" {part}" for part in _body_parts(node.body))
            lines.append(".")
        lines.append(".")
    return "\n".join(lines) + "\n"
