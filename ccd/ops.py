"""Outline, search, collapse, and expand."""

from __future__ import annotations

from dataclasses import replace

from ccd.codec import read_index
from ccd.model import CcdError, Document, Hit, Node


def outline_lines(text: str, depth: int | None = None) -> str:
    if depth is not None and depth < 1:
        raise CcdError("depth must be >= 1")
    title, count, rows = read_index(text)
    shown = [
        f"{node_id} {row_depth} {summary}"
        for node_id, row_depth, summary in rows
        if depth is None or row_depth <= depth
    ]
    return "\n".join([f"# {title}", f"# nodes {count}", *shown]) + "\n"


def search_document(doc: Document, query: str) -> tuple[Hit, ...]:
    if query == "":
        raise CcdError("empty query")
    needle = query.casefold()
    hits: list[Hit] = []
    for node in doc.nodes:
        if needle in node.summary.casefold():
            hits.append(Hit(node.id, "summary", None, node.summary))
        if needle in node.src.casefold():
            hits.append(Hit(node.id, "src", None, node.src))
        if node.body == "":
            continue
        for line_no, line in enumerate(node.body.split("\n"), start=1):
            if needle in line.casefold():
                hits.append(Hit(node.id, "body", line_no, line))
    return tuple(hits)


def collapse_document(doc: Document, node_id: str | None) -> Document:
    return _refold(doc, node_id, "collapsed")


def expand_document(doc: Document, node_id: str | None) -> Document:
    return _refold(doc, node_id, "expanded")


def format_expand(node: Node) -> str:
    parent = "-" if node.parent is None else node.parent
    see = "-" if not node.see else " ".join(node.see)
    inferred = "true" if node.inferred else "false"
    body = node.body
    if body != "" and not body.endswith("\n"):
        body += "\n"
    return (
        f"node {node.id}\n"
        f"parent: {parent}\n"
        f"summary: {node.summary}\n"
        f"src: {node.src}\n"
        f"see: {see}\n"
        f"inferred: {inferred}\n"
        f"body:\n"
        f"{body}"
    )


def _refold(doc: Document, node_id: str | None, fold: str) -> Document:
    known = {node.id for node in doc.nodes}
    if node_id is not None and node_id not in known:
        raise CcdError(f"unknown id {node_id}")
    if fold == "expanded":
        target = "expanded"
    elif fold == "collapsed":
        target = "collapsed"
    else:
        raise CcdError(f"unhandled fold {fold}")
    nodes = tuple(
        replace(node, fold=target) if node_id is None or node.id == node_id else node
        for node in doc.nodes
    )
    return Document(title=doc.title, nodes=nodes, version=doc.version)
