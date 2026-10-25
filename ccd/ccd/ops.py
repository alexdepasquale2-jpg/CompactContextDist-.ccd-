"""Outline, search, collapse, expand, and the attention loop (map, find, focus)."""

from __future__ import annotations

import re
from dataclasses import replace

from ccd.codec import read_index
from ccd.compact import estimate_tokens
from ccd.model import CcdError, Document, Hit, Node, compute_depths

_WORD = re.compile(r"[A-Za-z0-9]+(?:_[A-Za-z0-9]+)*")
_HEADING = re.compile(r"^(#{1,6})\s+(.*\S)\s*$")


def outline_lines(text: str, depth: int | None = None) -> str:
    if depth is not None and depth < 1:
        raise CcdError("depth must be >= 1")
    title, count, rows = read_index(text)
    shown: list[str] = []
    for row in rows:
        node_id, row_depth, tokens, summary = _unpack_row(row)
        if depth is not None and row_depth > depth:
            continue
        if tokens is None:
            shown.append(f"{node_id} {row_depth} {summary}")
        else:
            shown.append(f"{node_id} {row_depth} {tokens} {summary}")
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


def format_expand(
    node: Node,
    *,
    section: str | None = None,
    budget: int | None = None,
) -> str:
    parent = "-" if node.parent is None else node.parent
    see = "-" if not node.see else " ".join(node.see)
    inferred = "true" if node.inferred else "false"
    body = view_body(node.body, section=section, budget=budget)
    if body != "" and not body.endswith("\n"):
        body += "\n"
    lines = [
        f"node {node.id}",
        f"parent: {parent}",
        f"summary: {node.summary}",
        f"src: {node.src}",
        f"see: {see}",
        f"inferred: {inferred}",
    ]
    lines.extend(_ref_lines(node))
    lines.append("body:")
    return "\n".join(lines) + "\n" + body


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


def map_lines(text: str, *, budget: int = 400, depth: int = 1) -> str:
    """Depth-limited index the model can load. Does not include bodies.

    `budget` is an estimate_tokens cap on the text returned. Rows that would
    pass the cap are omitted and the result says to use `ccd find`.
    """
    if budget < 1:
        raise CcdError("budget must be >= 1")
    if depth < 1:
        raise CcdError("depth must be >= 1")
    title, count, rows = read_index(text)
    parsed = [_unpack_row(row) for row in rows]
    chosen: list[str] = []
    for index, (node_id, row_depth, tokens, summary) in enumerate(parsed):
        if row_depth > depth:
            continue
        if tokens is None:
            chosen.append(f"{node_id} - - {summary}")
        else:
            chosen.append(f"{node_id} {tokens} {_subtree_tokens(parsed, index)} {summary}")
    header = [f"# {title}", f"# nodes {count}", f"# map depth {depth}"]
    output = list(header)
    truncated = False
    for line in chosen:
        trial = "\n".join([*output, line]) + "\n"
        if estimate_tokens(trial) > budget:
            truncated = True
            break
        output.append(line)
    if truncated or len(output) - len(header) < len(chosen):
        output.append("# truncated; use ccd find")
    return "\n".join(output) + "\n"


def rank_ids(
    doc: Document,
    query: str,
    *,
    summaries: dict[str, str] | None = None,
) -> tuple[str, ...]:
    """Rank node ids from the index text only. Bodies are not scored."""
    if query == "":
        raise CcdError("empty query")
    query_terms = _terms(query)
    if not query_terms:
        raise CcdError("empty query")
    blobs: list[set[str]] = []
    id_terms: list[set[str]] = []
    for node in doc.nodes:
        summary = node.summary if summaries is None else summaries.get(node.id, node.summary)
        ident = _terms(node.id.replace(".", " ").replace("-", " "))
        blobs.append(ident | _terms(summary))
        id_terms.append(ident)
    df: dict[str, int] = {}
    for blob in blobs:
        for term in blob:
            df[term] = df.get(term, 0) + 1
    scored: list[tuple[float, int, str]] = []
    for node, blob, ident in zip(doc.nodes, blobs, id_terms, strict=True):
        score = 0.0
        for term in query_terms:
            if term not in blob:
                continue
            weight = 3.0 if term in ident else 1.0
            score += weight / df[term]
        if score > 0:
            scored.append((score, estimate_tokens(node.body), node.id))
    scored.sort(key=lambda item: (-item[0], item[1], item[2]))
    return tuple(item[2] for item in scored)


def find_lines(
    doc: Document,
    query: str,
    *,
    limit: int = 8,
    summaries: dict[str, str] | None = None,
) -> str:
    """Ranked one-liners. The caller prints these and does not open bodies."""
    if limit < 1:
        raise CcdError("limit must be >= 1")
    ranked = rank_ids(doc, query, summaries=summaries)
    if not ranked:
        raise CcdError("no hits")
    by_id = {node.id: node for node in doc.nodes}
    lines: list[str] = []
    for node_id in ranked[:limit]:
        node = by_id[node_id]
        summary = node.summary if summaries is None else summaries.get(node.id, node.summary)
        tokens = estimate_tokens(node.body)
        suffix = _ref_suffix(node)
        lines.append(f"{node.id} {tokens} {summary}{suffix}")
    return "\n".join(lines) + "\n"


def focus_text(
    doc: Document,
    ids: list[str] | tuple[str, ...],
    *,
    budget: int | None = None,
    section: str | None = None,
) -> str:
    """Ancestor one-liners plus the target bodies. Ancestor bodies stay unloaded."""
    if not ids:
        raise CcdError("focus needs an id")
    by_id = {node.id: node for node in doc.nodes}
    for node_id in ids:
        if node_id not in by_id:
            raise CcdError(f"unknown id {node_id}")
    targets = set(ids)
    seen: set[str] = set()
    ancestor_ids: list[str] = []
    for node_id in ids:
        chain: list[str] = []
        current = by_id[node_id].parent
        guard: set[str] = set()
        while current is not None and current not in guard and current in by_id:
            guard.add(current)
            chain.append(current)
            current = by_id[current].parent
        for ancestor in reversed(chain):
            if ancestor in targets or ancestor in seen:
                continue
            seen.add(ancestor)
            ancestor_ids.append(ancestor)
    depths = compute_depths(doc.nodes)
    lines = ["# focus"]
    for ancestor in ancestor_ids:
        node = by_id[ancestor]
        lines.append(
            f"# {node.id} {depths[node.id]} {estimate_tokens(node.body)} {node.summary}"
        )
    parts = ["\n".join(lines)]
    for node_id in ids:
        parts.append(format_expand(by_id[node_id], section=section, budget=budget).rstrip("\n"))
    return "\n".join(parts) + "\n"


def links_lines(doc: Document, node_id: str | None = None) -> str:
    """Typed cross-references and see-links. No bodies."""
    lines: list[str] = []
    for node in doc.nodes:
        if node_id is not None and node.id != node_id:
            continue
        lines.append(
            f"{node.id} see: {_fmt_refs(node.see)} requires: {_fmt_refs(node.requires)} "
            f"supersedes: {_fmt_refs(node.supersedes)} derived-from: {_fmt_refs(node.derived_from)}"
        )
    if node_id is not None and not lines:
        raise CcdError(f"unknown id {node_id}")
    return "\n".join(lines) + "\n"


def view_body(body: str, *, section: str | None = None, budget: int | None = None) -> str:
    text = body if section is None else slice_section(body, section)
    if budget is None:
        return text
    if budget < 1:
        raise CcdError("budget must be >= 1")
    if estimate_tokens(text) <= budget:
        return text
    kept: list[str] = []
    for line in text.split("\n"):
        trial = line if not kept else "\n".join([*kept, line])
        if estimate_tokens(trial) > budget:
            break
        kept.append(line)
    clipped = "\n".join(kept)
    note = "[truncated to budget]"
    if clipped == "":
        return note
    return clipped + "\n" + note


def slice_section(body: str, heading: str) -> str:
    """Return one markdown section, from its heading through the next peer heading."""
    target = heading.strip().casefold()
    if target == "":
        raise CcdError("empty section")
    lines = body.split("\n")
    start: int | None = None
    level = 0
    for index, line in enumerate(lines):
        match = _HEADING.match(line)
        if match is None:
            continue
        if match.group(2).strip().casefold() == target:
            start = index
            level = len(match.group(1))
            break
    if start is None:
        raise CcdError(f"section not found: {heading}")
    end = len(lines)
    for index in range(start + 1, len(lines)):
        match = _HEADING.match(lines[index])
        if match is not None and len(match.group(1)) <= level:
            end = index
            break
    return "\n".join(lines[start:end])


def _unpack_row(row: tuple[object, ...]) -> tuple[str, int, int | None, str]:
    if len(row) == 4:
        node_id, depth, tokens, summary = row
        if not isinstance(node_id, str) or not isinstance(depth, int) or not isinstance(tokens, int):
            raise CcdError("bad index row")
        if not isinstance(summary, str):
            raise CcdError("bad index row")
        return node_id, depth, tokens, summary
    if len(row) == 3:
        node_id, depth, summary = row
        if not isinstance(node_id, str) or not isinstance(depth, int) or not isinstance(summary, str):
            raise CcdError("bad index row")
        return node_id, depth, None, summary
    raise CcdError("bad index row")


def _subtree_tokens(rows: list[tuple[str, int, int | None, str]], index: int) -> int:
    _node_id, depth, tokens, _summary = rows[index]
    total = 0 if tokens is None else tokens
    for _node_id, row_depth, row_tokens, _summary in rows[index + 1 :]:
        if row_depth <= depth:
            break
        total += 0 if row_tokens is None else row_tokens
    return total


def _terms(text: str) -> set[str]:
    return {match.group(0).casefold() for match in _WORD.finditer(text) if len(match.group(0)) >= 2}


def _fmt_refs(refs: tuple[str, ...]) -> str:
    return "-" if not refs else " ".join(refs)


def _ref_lines(node: Node) -> list[str]:
    lines: list[str] = []
    if node.requires:
        lines.append(f"requires: {_fmt_refs(node.requires)}")
    if node.supersedes:
        lines.append(f"supersedes: {_fmt_refs(node.supersedes)}")
    if node.derived_from:
        lines.append(f"derived-from: {_fmt_refs(node.derived_from)}")
    return lines


def _ref_suffix(node: Node) -> str:
    parts = _ref_lines(node)
    if not parts:
        return ""
    return " | " + " ".join(parts)
