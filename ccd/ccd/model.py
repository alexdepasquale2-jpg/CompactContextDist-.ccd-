"""Document model, grammar, and semantic checks for .ccd files."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal, Never, NoReturn

Fold = Literal["expanded", "collapsed"]

_SEGMENT = r"[a-z][a-z0-9-]*"
ID_RE = re.compile(rf"^{_SEGMENT}(?:\.{_SEGMENT})*$")
WIKILINK_RE = re.compile(rf"\[\[({_SEGMENT}(?:\.{_SEGMENT})*)\]\]")

SUMMARY_MAX = 200
TITLE_MAX = 200
SRC_MAX = 2000
VERSION = 1
SUPPORTED_VERSIONS = (1, 2, 3)
# Version 3 is the pack default. Its index carries a body-token estimate so a
# reader can budget without opening bodies. Version 2 stays a lossless encoding
# of version 1 and is not the default pack.


class CcdError(Exception):
    def __init__(self, message: str, line: int | None = None) -> None:
        self.line = line
        if line is None:
            super().__init__(message)
        else:
            super().__init__(f"line {line}: {message}")


def _assert_never(value: Never) -> NoReturn:
    raise CcdError(f"unhandled variant: {value}")


@dataclass(frozen=True)
class Node:
    id: str
    parent: str | None
    summary: str
    src: str
    see: tuple[str, ...]
    inferred: bool
    body: str
    fold: Fold = "expanded"
    requires: tuple[str, ...] = ()
    supersedes: tuple[str, ...] = ()
    derived_from: tuple[str, ...] = ()


IndexRowV1 = tuple[str, int, str]
IndexRowV3 = tuple[str, int, int, str]


@dataclass(frozen=True)
class Document:
    title: str
    nodes: tuple[Node, ...]
    version: int = VERSION
    index: tuple[IndexRowV1, ...] | tuple[IndexRowV3, ...] | None = None
    declared_nodes: int | None = None


@dataclass(frozen=True)
class Hit:
    node_id: str
    field: str
    line: int | None
    text: str


def wikilinks(body: str) -> list[str]:
    found: list[str] = []
    fenced = False
    for line in body.split("\n"):
        if line.startswith("```"):
            fenced = not fenced
            continue
        if fenced:
            continue
        found.extend(WIKILINK_RE.findall(line))
    return found


def compute_depths(nodes: tuple[Node, ...]) -> dict[str, int]:
    position = {node.id: index for index, node in enumerate(nodes)}
    depths: dict[str, int] = {}

    def depth_of(index: int, stack: frozenset[str]) -> int:
        node = nodes[index]
        if node.id in depths and node.id not in stack:
            return depths[node.id]
        if node.parent is None or node.parent not in position or node.id in stack:
            depths[node.id] = 1
            return 1
        parent_depth = depth_of(position[node.parent], stack | {node.id})
        depths[node.id] = parent_depth + 1
        return depths[node.id]

    for index in range(len(nodes)):
        depth_of(index, frozenset())
    return depths


def build_index(nodes: tuple[Node, ...]) -> tuple[IndexRowV1, ...]:
    depths = compute_depths(nodes)
    return tuple((node.id, depths[node.id], node.summary) for node in nodes)


def build_index_v3(nodes: tuple[Node, ...]) -> tuple[IndexRowV3, ...]:
    """Index rows for version 3. Token counts are the stable body estimate."""
    from ccd.compact import estimate_tokens

    depths = compute_depths(nodes)
    return tuple(
        (node.id, depths[node.id], estimate_tokens(node.body), node.summary) for node in nodes
    )


def problems(doc: Document) -> list[str]:
    """Semantic problems. Empty means the document is safe to trust."""
    errors: list[str] = []
    if doc.version not in SUPPORTED_VERSIONS:
        errors.append(f"unsupported version {doc.version}")
    if doc.title == "" or len(doc.title) > TITLE_MAX or _has_controls(doc.title):
        errors.append(f"title must be 1..{TITLE_MAX} characters on one line")

    seen_ids: set[str] = set()
    duplicate = False
    for node in doc.nodes:
        if node.id in seen_ids and not duplicate:
            errors.append(f"duplicate id {node.id}")
            duplicate = True
        seen_ids.add(node.id)
        if not ID_RE.match(node.id):
            errors.append(f"invalid id {node.id}")

    position = {node.id: index for index, node in enumerate(doc.nodes)}
    for node in doc.nodes:
        if node.parent is None:
            continue
        if node.parent not in position:
            errors.append(f"{node.id}: missing parent {node.parent}")
        elif position[node.parent] >= position[node.id]:
            errors.append(f"{node.id}: parent {node.parent} must appear earlier")

    for node in doc.nodes:
        if node.summary == "" or len(node.summary) > SUMMARY_MAX or _has_controls(node.summary):
            errors.append(f"{node.id}: summary must be 1..{SUMMARY_MAX} characters")
        if node.summary != node.summary.strip():
            errors.append(f"{node.id}: summary must not have surrounding space")
        if node.src == "" or len(node.src) > SRC_MAX or _has_controls(node.src):
            errors.append(f"{node.id}: src must be a single non-empty line")
        if node.fold == "expanded":
            pass
        elif node.fold == "collapsed":
            pass
        else:
            _assert_never(node.fold)
        _check_refs(node, "see", node.see, seen_ids, errors)
        _check_refs(node, "requires", node.requires, seen_ids, errors)
        _check_refs(node, "supersedes", node.supersedes, seen_ids, errors)
        _check_refs(node, "derived-from", node.derived_from, seen_ids, errors)
        for ref in wikilinks(node.body):
            if ref not in seen_ids:
                errors.append(f"{node.id}: wikilink missing {ref}")

    if doc.index is not None and doc.index != _expected_index(doc):
        errors.append("index does not match nodes")
    if doc.declared_nodes is not None and doc.declared_nodes != len(doc.nodes):
        errors.append(
            f"header nodes: {doc.declared_nodes} does not match {len(doc.nodes)} node blocks"
        )
    return errors


def _expected_index(doc: Document) -> tuple[IndexRowV1, ...] | tuple[IndexRowV3, ...]:
    if doc.version == 3:
        return build_index_v3(doc.nodes)
    if doc.version == 1 or doc.version == 2:
        return build_index(doc.nodes)
    return ()


def _check_refs(
    node: Node,
    field: str,
    refs: tuple[str, ...],
    seen_ids: set[str],
    errors: list[str],
) -> None:
    seen_refs: set[str] = set()
    for ref in refs:
        if not ID_RE.match(ref):
            errors.append(f"{node.id}: {field}: invalid id {ref}")
            continue
        if ref == node.id:
            errors.append(f"{node.id}: {field}: references itself")
        if ref in seen_refs:
            errors.append(f"{node.id}: {field}: duplicate {ref}")
        seen_refs.add(ref)
        if ref not in seen_ids:
            errors.append(f"{node.id}: {field}: missing {ref}")


def _has_controls(text: str) -> bool:
    return any(ord(char) < 32 for char in text)
