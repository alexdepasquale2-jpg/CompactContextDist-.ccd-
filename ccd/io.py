"""Pack markdown or JSON into a document, and unpack back out."""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

from ccd.model import ID_RE, SUMMARY_MAX, CcdError, Document, Node, problems

_FRONT_KEYS = ("id", "parent", "summary", "src", "see", "inferred")
_JSON_NODE_KEYS = {"id", "parent", "summary", "src", "see", "inferred", "body"}
_PREFIXED = re.compile(r"^\d+-(.+)$")
_HEADING = re.compile(r"^#{1,6}\s+(.*\S)\s*$")


def pack_markdown(paths: list[Path], title: str) -> Document:
    if not paths:
        raise CcdError("pack needs at least one path")
    records: list[tuple[tuple[int, str], Node]] = []
    for ordinal, raw in enumerate(paths):
        root = Path(raw)
        if not root.exists():
            raise CcdError(f"not found: {root}")
        if root.is_file():
            files = [root]
            base = root.parent
            input_name = _segment(root.stem, root)
        else:
            files = sorted(root.rglob("*.md"), key=lambda path: path.relative_to(root).as_posix())
            base = root
            input_name = _segment(root.name, root)
        for path in files:
            rel = path.relative_to(base)
            text = path.read_text(encoding="utf-8")
            meta, body = _split_frontmatter(text, path)
            node_id = meta.get("id") or _default_id(input_name, rel, path)
            if not ID_RE.match(node_id):
                raise CcdError(f"{path}: invalid id {node_id}")
            if "parent" in meta:
                parent = None if meta["parent"] == "-" else meta["parent"]
                if parent is not None and not ID_RE.match(parent):
                    raise CcdError(f"{path}: invalid parent {parent}")
            else:
                parent = node_id.rsplit(".", 1)[0] if "." in node_id else None
            summary = meta.get("summary") or _derive_summary(body, path)
            src = meta.get("src") or path.as_posix()
            see = _see_value(meta.get("see", "-"), path)
            inferred = _bool_value(meta.get("inferred", "false"), path)
            node = Node(node_id, parent, summary, src, see, inferred, body, "expanded")
            records.append(((ordinal, rel.as_posix()), node))
    doc = Document(title=title, nodes=_arrange(records), version=2)
    found = problems(doc)
    if found:
        raise CcdError("\n".join(found))
    return doc


def pack_json(text: str, title_override: str | None = None) -> Document:
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise CcdError(f"invalid json: {exc}") from exc
    if not isinstance(data, dict):
        raise CcdError("json root must be an object")
    extra = set(data) - {"title", "nodes"}
    if extra:
        raise CcdError(f"unknown json keys: {', '.join(sorted(extra))}")
    if title_override is not None:
        title = title_override
    else:
        title = data.get("title")
        if not isinstance(title, str):
            raise CcdError("json title must be a string")
    items = data.get("nodes")
    if not isinstance(items, list):
        raise CcdError("json nodes must be a list")
    records: list[tuple[tuple[int, str], Node]] = []
    for index, item in enumerate(items):
        records.append(((index, ""), _node_from_json(item)))
    doc = Document(title=title, nodes=_arrange(records), version=2)
    found = problems(doc)
    if found:
        raise CcdError("\n".join(found))
    return doc


def unpack_markdown(doc: Document, dest: Path, *, force: bool = False) -> None:
    if dest.exists():
        if not dest.is_dir():
            raise CcdError(f"{dest} is not a directory")
        if any(dest.iterdir()) and not force:
            raise CcdError(f"{dest} is not empty")
    else:
        dest.mkdir(parents=True)
    children: dict[str | None, list[Node]] = defaultdict(list)
    for node in doc.nodes:
        children[node.parent].append(node)
    _write_level(children[None], dest, children)


def unpack_json(doc: Document) -> str:
    payload = {
        "title": doc.title,
        "nodes": [
            {
                "id": node.id,
                "parent": node.parent,
                "summary": node.summary,
                "src": node.src,
                "see": list(node.see),
                "inferred": node.inferred,
                "body": node.body,
            }
            for node in doc.nodes
        ],
    }
    return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"


def render_markdown(node: Node) -> str:
    parent = "-" if node.parent is None else node.parent
    see = "-" if not node.see else " ".join(node.see)
    inferred = "true" if node.inferred else "false"
    lines = [
        "---",
        f"id: {node.id}",
        f"parent: {parent}",
        f"summary: {node.summary}",
        f"src: {node.src}",
        f"see: {see}",
        f"inferred: {inferred}",
        "---",
    ]
    text = "\n".join(lines) + "\n"
    if node.body:
        text += node.body + "\n"
    return text


def _write_level(
    nodes: list[Node],
    directory: Path,
    children: dict[str | None, list[Node]],
) -> None:
    if not nodes:
        return
    slugs = _slugs(nodes)
    width = len(str(len(nodes)))
    for index, node in enumerate(nodes):
        prefix = f"{index + 1:0{width}d}-"
        kids = children.get(node.id, [])
        if kids:
            folder = directory / f"{prefix}{slugs[index]}"
            folder.mkdir(exist_ok=True)
            (folder / "_index.md").write_text(render_markdown(node), encoding="utf-8")
            _write_level(kids, folder, children)
        else:
            path = directory / f"{prefix}{slugs[index]}.md"
            path.write_text(render_markdown(node), encoding="utf-8")


def _slugs(nodes: list[Node]) -> list[str]:
    last = [node.id.rsplit(".", 1)[-1] for node in nodes]
    if len(set(last)) == len(last):
        return last
    return [node.id.replace(".", "--") for node in nodes]


def _arrange(records: list[tuple[tuple[int, str], Node]]) -> tuple[Node, ...]:
    by_id: dict[str, Node] = {}
    sort_of: dict[str, tuple[int, str]] = {}
    for key, node in records:
        if node.id in by_id:
            raise CcdError(f"duplicate id {node.id}")
        by_id[node.id] = node
        sort_of[node.id] = key
    for node in by_id.values():
        if node.parent is not None and node.parent not in by_id:
            raise CcdError(f"{node.id}: missing parent {node.parent}")
    children: dict[str | None, list[Node]] = defaultdict(list)
    for node in by_id.values():
        children[node.parent].append(node)
    for kids in children.values():
        kids.sort(key=lambda node: sort_of[node.id])
    ordered: list[Node] = []

    def walk(parent: str | None, stack: frozenset[str]) -> None:
        for node in children.get(parent, []):
            if node.id in stack:
                raise CcdError(f"{node.id}: cycle")
            ordered.append(node)
            walk(node.id, stack | {node.id})

    walk(None, frozenset())
    if len(ordered) != len(by_id):
        raise CcdError("cycle or unreachable node")
    return tuple(ordered)


def _split_frontmatter(text: str, path: Path) -> tuple[dict[str, str], str]:
    if "\r" in text:
        raise CcdError(f"{path}: CR is not allowed; use LF")
    if not text.endswith("\n"):
        raise CcdError(f"{path}: must end with a newline")
    if not text.startswith("---\n"):
        return {}, text[:-1]
    end = text.find("\n---\n", 3)
    if end == -1:
        raise CcdError(f"{path}: unclosed frontmatter")
    meta = _parse_meta(text[4:end], path)
    rest = text[end + len("\n---\n") :]
    if rest == "":
        return meta, ""
    if not rest.endswith("\n"):
        raise CcdError(f"{path}: must end with a newline")
    return meta, rest[:-1]


def _parse_meta(raw: str, path: Path) -> dict[str, str]:
    if raw == "":
        return {}
    fields: dict[str, str] = {}
    for line in raw.split("\n"):
        if line == "" or line != line.rstrip():
            raise CcdError(f"{path}: invalid frontmatter line")
        key, sep, value = line.partition(":")
        if sep == "" or not value.startswith(" "):
            raise CcdError(f"{path}: expected 'key: value'")
        if key not in _FRONT_KEYS:
            raise CcdError(f"{path}: unknown frontmatter key {key}")
        if key in fields:
            raise CcdError(f"{path}: duplicate frontmatter key {key}")
        fields[key] = value[1:]
    return fields


def _see_value(value: str, path: Path) -> tuple[str, ...]:
    if value == "-":
        return ()
    if value == "" or value != value.strip() or "  " in value:
        raise CcdError(f"{path}: see must be '-' or single-spaced ids")
    refs = tuple(value.split(" "))
    for ref in refs:
        if not ID_RE.match(ref):
            raise CcdError(f"{path}: invalid see id {ref}")
    return refs


def _bool_value(value: str, path: Path) -> bool:
    if value == "true":
        return True
    if value == "false":
        return False
    raise CcdError(f"{path}: inferred must be true or false")


def _derive_summary(body: str, path: Path) -> str:
    text = ""
    for line in body.split("\n"):
        heading = _HEADING.match(line)
        if heading:
            text = heading.group(1).strip()
            break
        if line.strip():
            text = line.strip()
            break
    if text == "":
        raise CcdError(f"{path}: cannot derive a summary")
    if len(text) > SUMMARY_MAX:
        return text[: SUMMARY_MAX - 3] + "..."
    return text


def _default_id(input_name: str, rel: Path, path: Path) -> str:
    parts = [input_name]
    if str(rel.parent) != ".":
        for part in rel.parent.parts:
            parts.append(_segment(part, path))
    if rel.name != "_index.md":
        parts.append(_segment(rel.stem, path))
    return ".".join(parts)


def _segment(name: str, path: Path) -> str:
    prefixed = _PREFIXED.match(name)
    segment = prefixed.group(1) if prefixed else name
    if not re.match(rf"^{_segment_pattern()}$", segment):
        raise CcdError(f"{path}: invalid path segment {name}")
    return segment


def _segment_pattern() -> str:
    return r"[a-z][a-z0-9-]*"


def _node_from_json(item: object) -> Node:
    if not isinstance(item, dict):
        raise CcdError("json node must be an object")
    extra = set(item) - _JSON_NODE_KEYS
    if extra:
        raise CcdError(f"unknown json node keys: {', '.join(sorted(extra))}")
    for key in ("id", "summary", "body"):
        if key not in item:
            raise CcdError(f"json node missing {key}")
    node_id = item["id"]
    summary = item["summary"]
    body = item["body"]
    if not isinstance(node_id, str) or not ID_RE.match(node_id):
        raise CcdError(f"invalid json id {node_id!r}")
    if not isinstance(summary, str):
        raise CcdError(f"{node_id}: summary must be a string")
    if not isinstance(body, str) or "\r" in body:
        raise CcdError(f"{node_id}: body must be an LF string")
    parent = item.get("parent")
    if parent is not None and (not isinstance(parent, str) or not ID_RE.match(parent)):
        raise CcdError(f"{node_id}: parent must be an id or null")
    src = item.get("src", "-")
    if not isinstance(src, str) or src == "":
        raise CcdError(f"{node_id}: src must be a string")
    see_raw = item.get("see", [])
    if not isinstance(see_raw, list) or not all(isinstance(ref, str) for ref in see_raw):
        raise CcdError(f"{node_id}: see must be a list of ids")
    see = tuple(see_raw)
    inferred = item.get("inferred", False)
    if not isinstance(inferred, bool):
        raise CcdError(f"{node_id}: inferred must be a boolean")
    if "\r" in summary or "\r" in src:
        raise CcdError(f"{node_id}: CR is not allowed")
    return Node(node_id, parent, summary, src, see, inferred, body, "expanded")
