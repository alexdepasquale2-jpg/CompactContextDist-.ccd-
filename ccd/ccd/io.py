"""Pack markdown or JSON into a document, and unpack back out."""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

from ccd.model import ID_RE, SUMMARY_MAX, CcdError, Document, Node, problems

_FRONT_KEYS = (
    "id",
    "parent",
    "summary",
    "src",
    "see",
    "inferred",
    "requires",
    "supersedes",
    "derived-from",
)
_JSON_NODE_KEYS = {
    "id",
    "parent",
    "summary",
    "src",
    "see",
    "inferred",
    "body",
    "requires",
    "supersedes",
    "derived-from",
}
_PREFIXED = re.compile(r"^\d+-(.+)$")
_HEADING = re.compile(r"^#{1,6}\s+(.*\S)\s*$")


def pack_markdown(paths: list[Path], title: str) -> Document:
    if not paths:
        raise CcdError("pack needs at least one path")
    records: list[tuple[tuple[int, str], Node]] = []
    implied_ids: set[str] = set()
    for ordinal, raw in enumerate(paths):
        root = Path(raw)
        if not root.exists():
            raise CcdError(f"not found: {root}")
        if root.is_file():
            files = [root]
            base = root.parent
            input_name: str | None = _segment(root.stem, root)
        else:
            files = sorted(root.rglob("*.md"), key=lambda path: path.relative_to(root).as_posix())
            base = root
            # Report folders are named 2026-10-25-slug, which is not an id.
            # The directory name is only a prefix for files that omit id.
            input_name = None
        for path in files:
            rel = path.relative_to(base)
            text = path.read_text(encoding="utf-8")
            meta, body = _split_frontmatter(text, path)
            explicit = meta.get("id")
            if explicit:
                node_id = explicit
            else:
                if input_name is None and root.is_dir():
                    try:
                        input_name = _segment(root.name, root)
                    except CcdError:
                        # 2026-10-25-slug is a run folder, not an id prefix.
                        input_name = ""
                node_id = _default_id(
                    input_name or None, rel, path, single_file=root.is_file()
                )
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
            see = _see_value(meta.get("see", "-"), path, "see")
            requires = _see_value(meta.get("requires", "-"), path, "requires")
            supersedes = _see_value(meta.get("supersedes", "-"), path, "supersedes")
            derived_from = _see_value(meta.get("derived-from", "-"), path, "derived-from")
            inferred = _bool_value(meta.get("inferred", "false"), path)
            implied = "parent" not in meta
            pieces = _plain_heading_nodes(
                body,
                path,
                node_id=node_id,
                parent=parent,
                src=src,
                summary=summary,
                see=see,
                inferred=inferred,
                requires=requires,
                supersedes=supersedes,
                derived_from=derived_from,
                split=not explicit,
            )
            for index, node in enumerate(pieces):
                records.append(((ordinal, f"{rel.as_posix()}#{index:04d}"), node))
                if implied:
                    implied_ids.add(node.id)
    records = _ensure_parents(records, implied_ids)
    doc = Document(title=title, nodes=_arrange(records), version=3)
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
    doc = Document(title=title, nodes=_arrange(records), version=3)
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
                "requires": list(node.requires),
                "supersedes": list(node.supersedes),
                "derived-from": list(node.derived_from),
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
    requires = "-" if not node.requires else " ".join(node.requires)
    supersedes = "-" if not node.supersedes else " ".join(node.supersedes)
    derived = "-" if not node.derived_from else " ".join(node.derived_from)
    inferred = "true" if node.inferred else "false"
    lines = [
        "---",
        f"id: {node.id}",
        f"parent: {parent}",
        f"summary: {node.summary}",
        f"src: {node.src}",
        f"see: {see}",
        f"requires: {requires}",
        f"supersedes: {supersedes}",
        f"derived-from: {derived}",
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
    raw = text[4:end]
    # Skill files and other notes use a `---` block that is not a CCD node.
    # Only a block that names `id` is frontmatter. Otherwise the fence is body.
    if not any(line.startswith("id: ") for line in raw.split("\n")):
        return {}, text[:-1]
    meta = _parse_meta(raw, path)
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


def _see_value(value: str, path: Path, field: str = "see") -> tuple[str, ...]:
    if value == "-":
        return ()
    if value == "" or value != value.strip() or "  " in value:
        raise CcdError(f"{path}: {field} must be '-' or single-spaced ids")
    refs = tuple(value.split(" "))
    for ref in refs:
        if not ID_RE.match(ref):
            raise CcdError(f"{path}: invalid {field} id {ref}")
    return refs


def _bool_value(value: str, path: Path) -> bool:
    if value == "true":
        return True
    if value == "false":
        return False
    raise CcdError(f"{path}: inferred must be true or false")


def _derive_summary(body: str, path: Path) -> str:
    text = ""
    skipped_fence = False
    lines = body.split("\n")
    index = 0
    if lines and lines[0] == "---":
        index = 1
        while index < len(lines) and lines[index] != "---":
            index += 1
        if index < len(lines) and lines[index] == "---":
            index += 1
            skipped_fence = True
    for line in lines[index:] if skipped_fence else lines:
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


def _plain_heading_nodes(
    body: str,
    path: Path,
    *,
    node_id: str,
    parent: str | None,
    src: str,
    summary: str,
    see: tuple[str, ...],
    inferred: bool,
    requires: tuple[str, ...],
    supersedes: tuple[str, ...],
    derived_from: tuple[str, ...],
    split: bool,
) -> list[Node]:
    """One node, or a file node plus ## and ### children when there is no id.

    A CCD frontmatter file stays one node. Plain markdown with no ## or ###
    stays one node. Otherwise each ## and ### is its own node so focus can
    load that section without the rest of the file. Deeper headings stay in
    the ### body. Fenced lines are not headings.
    """
    root = Node(
        node_id,
        parent,
        summary,
        src,
        see,
        inferred,
        body,
        "expanded",
        requires,
        supersedes,
        derived_from,
    )
    if not split:
        return [root]
    lines = body.split("\n")
    marks = _heading_marks(lines)
    if not marks:
        return [root]
    preamble = "\n".join(lines[: marks[0][0]]).strip("\n")
    if preamble.strip():
        root_summary = _derive_summary(preamble, path)
    else:
        root_summary = node_id.rsplit(".", 1)[-1]
    nodes = [
        Node(
            node_id,
            parent,
            root_summary,
            src,
            see,
            inferred,
            preamble,
            "expanded",
            requires,
            supersedes,
            derived_from,
        )
    ]
    used: dict[str, set[str]] = defaultdict(set)
    stack: list[tuple[int, str]] = [(1, node_id)]
    for index, (start, level, title) in enumerate(marks):
        end = marks[index + 1][0] if index + 1 < len(marks) else len(lines)
        chunk = "\n".join(lines[start:end]).strip("\n")
        while stack and stack[-1][0] >= level:
            stack.pop()
        parent_id = stack[-1][1] if stack else node_id
        slug = _heading_slug(title, path, used[parent_id])
        child_id = f"{parent_id}.{slug}"
        if not ID_RE.match(child_id):
            raise CcdError(f"{path}: heading is not an id {title}")
        heading_summary = title if len(title) <= SUMMARY_MAX else title[: SUMMARY_MAX - 3] + "..."
        nodes.append(
            Node(
                child_id,
                parent_id,
                heading_summary,
                src,
                (),
                False,
                chunk,
                "expanded",
            )
        )
        stack.append((level, child_id))
    return nodes


def _heading_marks(lines: list[str]) -> list[tuple[int, int, str]]:
    marks: list[tuple[int, int, str]] = []
    fenced = False
    for index, line in enumerate(lines):
        if line.startswith("```"):
            fenced = not fenced
            continue
        if fenced:
            continue
        match = re.match(r"^(#{2,3})\s+(.*\S)\s*$", line)
        if match is None:
            continue
        marks.append((index, len(match.group(1)), match.group(2).strip()))
    return marks


def _heading_slug(title: str, path: Path, used: set[str]) -> str:
    chars: list[str] = []
    dash = False
    for char in title.casefold():
        if "a" <= char <= "z" or "0" <= char <= "9":
            chars.append(char)
            dash = False
        elif not dash:
            chars.append("-")
            dash = True
    slug = "".join(chars).strip("-")
    if slug == "" or not slug[0].isalpha():
        slug = ("s-" + slug) if slug else "section"
    if not re.match(rf"^{_segment_pattern()}$", slug):
        raise CcdError(f"{path}: heading is not an id {title}")
    base = slug
    number = 2
    while slug in used:
        slug = f"{base}-{number}"
        number += 1
    used.add(slug)
    return slug


def _ensure_parents(
    records: list[tuple[tuple[int, str], Node]],
    implied_ids: set[str],
) -> list[tuple[tuple[int, str], Node]]:
    """Add path parents for ids that were derived, not declared in frontmatter.

    A frontmatter `parent:` that does not exist is still an error. A dated run
    folder can hold `docs/batches/card.md` with no index files; those parents
    are path labels, so the pack creates them.
    """
    by_id = {node.id: node for _key, node in records}
    extra: list[tuple[tuple[int, str], Node]] = []
    pending = [node for node in by_id.values() if node.id in implied_ids]
    guard = 0
    while pending:
        node = pending.pop()
        parent_id = node.parent
        if parent_id is None or parent_id in by_id:
            continue
        grand = parent_id.rsplit(".", 1)[0] if "." in parent_id else None
        parent = Node(
            parent_id,
            grand,
            parent_id.rsplit(".", 1)[-1],
            "-",
            (),
            False,
            "",
            "expanded",
        )
        by_id[parent_id] = parent
        extra.append(((0, f"~{parent_id}"), parent))
        pending.append(parent)
        guard += 1
        if guard > 10000:
            raise CcdError("parent chain too deep")
    return records + extra


def _default_id(input_name: str | None, rel: Path, path: Path, *, single_file: bool = False) -> str:
    # A lone file is one root node. Its id is the stem, not stem.stem.
    if single_file:
        return _segment(rel.stem, path)
    parts: list[str] = []
    if input_name:
        parts.append(input_name)
    if str(rel.parent) != ".":
        for part in rel.parent.parts:
            parts.append(_segment(part, path))
    if rel.name != "_index.md":
        parts.append(_segment(rel.stem, path))
    if not parts:
        raise CcdError(f"{path}: cannot derive an id")
    return ".".join(parts)


def _segment(name: str, path: Path) -> str:
    prefixed = _PREFIXED.match(name)
    segment = prefixed.group(1) if prefixed else name
    segment = segment.lower()
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
    see = _json_ids(item, "see", node_id)
    requires = _json_ids(item, "requires", node_id)
    supersedes = _json_ids(item, "supersedes", node_id)
    derived_from = _json_ids(item, "derived-from", node_id)
    inferred = item.get("inferred", False)
    if not isinstance(inferred, bool):
        raise CcdError(f"{node_id}: inferred must be a boolean")
    if "\r" in summary or "\r" in src:
        raise CcdError(f"{node_id}: CR is not allowed")
    return Node(
        node_id,
        parent,
        summary,
        src,
        see,
        inferred,
        body,
        "expanded",
        requires,
        supersedes,
        derived_from,
    )


def _json_ids(item: dict[str, object], key: str, node_id: str) -> tuple[str, ...]:
    raw = item.get(key, [])
    if not isinstance(raw, list) or not all(isinstance(ref, str) for ref in raw):
        raise CcdError(f"{node_id}: {key} must be a list of ids")
    return tuple(raw)
