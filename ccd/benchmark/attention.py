"""Compare tokens a model must load: full index, map/find/focus, whole markdown.

The ranker sees id and summary only. Bodies are loaded after the pick.
Token counts in the table are tiktoken o200k of the strings the model would see.
Index numbers inside a .ccd file stay on the dependency-free estimate.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

from ccd import (
    Document,
    Node,
    find_lines,
    focus_text,
    format_expand,
    map_lines,
    pack_markdown,
    rank_ids,
    render,
)
from ccd.model import compute_depths

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
AGENTS = REPO / "agents"

# Frozen index text from before the summaries were rewritten for find.
OLD = {
    "evidence": "Recovered facts for Regliobecky, Lincoln, and the seed method.",
    "evidence.regliobecky": "Designer direction, plus owner-stated original intent (Alex, 2026-10-25).",
    "evidence.lincoln": "Lincoln built kits with local tools, one regenerate script, and verify checks.",
    "evidence.seed-method": "Alex's seed method expands a seed, distills principles, and resynthesizes.",
    "evidence.dawn-whistle": "Dawn Whistle is the recovered instance of spec, batches, seeds, and export.",
    "evidence.gaps": "Searches that returned nothing, and facts that must not be invented.",
    "protocols": "Regliobecky writes the spec, Lincoln builds batches, handoff is the contract.",
    "protocols.regliobecky-generation": "Seed to spec in four phases: seedinitialization, seedgermination, seedexpansion, sensesprocessing.",
    "protocols.lincoln-creation": "Build one batch with local tools, a regenerate script, and a verify gate.",
    "protocols.handoff": "How the two modes pass work, and the condensate that remains.",
}

LOOSE_SUMMARY = {
    "sources": "Raw notes the evidence cites. answers: where a recovered claim was copied from",
    "sources.evidence": "Recovered 2026-10-25 memo of terminal logs and the PC copy limit. answers: the raw evidence file",
    "sources.rea-seed-method": "REA skill source: Ghidra, rea-agents MCP, seed-mode variant. answers: the workflow file",
    "sources.system-prompt-combined": "Later combined draft of both modes. answers: draft, not a recovered prompt",
    "sources.system-prompt-lincoln": "Later draft of the asset-builder prompt. answers: draft, not a recovered prompt",
    "sources.system-prompt-regliobecky": "Later draft of the spec-owner prompt. answers: draft, not a recovered prompt",
    "schematics": "Layout diagrams for the spec, the kit directory, and the handoff. answers: which diagram",
    "schematics.readme": "Index of the layout diagrams. answers: list of schematics",
    "schematics.handoff-flow": "Flow diagram from seed through both modes to the coding agent. answers: the arrow picture",
    "schematics.asset-kit": "Kit directory layout: regenerate script, verify.json, previews. answers: output folder shape",
    "schematics.world-spec": "World spec file tree: spec.md, asset-list, promptN, common.md. answers: which path holds a section",
    "templates": "Blank forms for the brief, the spec, the prompt, and the report. answers: which blank to copy",
    "templates.readme": "Index of blank forms. answers: template list",
    "templates.seed-brief": "Blank seed brief: phrase, mood, placeholder lines. answers: empty brief",
    "templates.spec": "Blank spec form, sections for look lock through delivery. answers: empty spec.md",
    "templates.batch-prompt": "Blank engine prompt that names asset ids and pivots. answers: empty promptN",
    "templates.report": "Blank report folder: process, notes, context. answers: empty run record",
    "templates.report.process": "Blank process log with a heading per phase. answers: empty process file",
    "templates.report.notes": "Blank notes page for rejections and inferences. answers: empty notes file",
    "templates.report.context": "Blank context page for ids and the next step. answers: empty context file",
    "skills": "Short procedures, one file per mode. answers: which skill",
    "skills.regliobecky-generation": "Regliobecky skill folder. answers: the skill directory",
    "skills.regliobecky-generation.skill": "Short Regliobecky procedure. answers: the skill file",
    "skills.lincoln-creation": "Lincoln skill folder. answers: the skill directory",
    "skills.lincoln-creation.skill": "Short Lincoln procedure. answers: the skill file",
    "docs": "Practical guide for the format tool. answers: the docs directory",
    "docs.using-ccd": "How to run map, find, and focus from the ccd directory. answers: the command sequence",
    "spec": "Format grammar for version 3: index token estimates and typed refs. answers: format rules",
    "guide.system-prompt": "Both modes in one instruction file. answers: the bot prompt",
    "guide.connect": "How to attach Cursor or a chat agent. answers: setup without the format tool",
    "guide.agents": "Short index of the agent folder. answers: where each file sits",
    "guide.readme": "Seedforge folder overview and the quickstart block. answers: how the folder is laid out",
    "guide.testing": "Sample fog-bell drill and the per-phase checklist. answers: how to test a run",
}


@dataclass(frozen=True)
class Task:
    pack: str
    query: str
    target: str


TASKS: tuple[Task, ...] = (
    Task("seedforge", "rubber-band snap latent space axis_forward", "evidence.regliobecky"),
    Task("seedforge", "verify_kit.py make_scrapdune.sh numpy scipy ffmpeg", "evidence.lincoln"),
    Task("seedforge", "resynthesizes no DRM REA hard rules", "evidence.seed-method"),
    Task("seedforge", "Scrapdune Unity HUD prompt 15 Cinderstride", "evidence.dawn-whistle"),
    Task("seedforge", "Lincolnlogious spelling state.vscdb unnamed Pillow", "evidence.gaps"),
    Task("seedforge", "which child holds a fact", "evidence"),
    Task("seedforge", "seedinitialization seedgermination seedexpansion sensesprocessing", "protocols.regliobecky-generation"),
    Task("seedforge", "headless test contact-sheet gate P0 kit steps", "protocols.lincoln-creation"),
    Task("seedforge", "condensate Packet Question Next who changes", "protocols.handoff"),
    Task("seedforge", "which mode to open", "protocols"),
    Task("large", "asset-builder later draft", "sources.system-prompt-lincoln"),
    Task("large", "where each file sits", "guide.agents"),
    Task("large", "flow diagram coding agent arrow picture", "schematics.handoff-flow"),
    Task("large", "kit directory layout previews output folder", "schematics.asset-kit"),
    Task("large", "world spec file tree promptN common.md", "schematics.world-spec"),
    Task("large", "blank spec form empty spec.md", "templates.spec"),
    Task("large", "blank seed brief mood placeholder", "templates.seed-brief"),
    Task("large", "blank process log phase headings", "templates.report.process"),
    Task("large", "blank engine prompt empty promptN", "templates.batch-prompt"),
    Task("large", "blank notes page rejections inferences", "templates.report.notes"),
)


def _seg(name: str) -> str:
    match = re.match(r"^\d+-(.+)$", name)
    segment = match.group(1) if match else name
    return segment.lower()


def _body(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    if text.endswith("\n"):
        text = text[:-1]
    return text


def _weak(body: str, fallback: str) -> str:
    for line in body.split("\n"):
        stripped = line.strip()
        if stripped.startswith("#"):
            text = stripped.lstrip("#").strip()
            if text:
                return text[:200]
        if stripped.startswith("---") or stripped == "" or stripped.startswith("id:"):
            continue
        if stripped.startswith(("parent:", "summary:", "src:", "see:", "inferred:", "name:", "description:")):
            continue
        return stripped[:200]
    return fallback[:200]


def _node(node_id: str, parent: str | None, summary: str, src: str, body: str) -> Node:
    if len(summary) > 200:
        summary = summary[:197] + "..."
    return Node(node_id, parent, summary, src, (), False, body, "expanded")


def _add_tree(nodes: list[Node], directory: Path, root_id: str) -> None:
    root_summary = LOOSE_SUMMARY.get(root_id, f"Notes for {root_id}.")
    nodes.append(_node(root_id, None, root_summary, directory.as_posix(), f"# {root_id}\n"))
    known = {root_id}
    files = sorted(directory.rglob("*.md"))
    indexed: dict[str, Path] = {}
    leaves: list[tuple[str, Path]] = []
    for path in files:
        rel = path.relative_to(directory)
        dir_parts = [] if str(rel.parent) == "." else [_seg(part) for part in rel.parent.parts]
        if rel.name == "_index.md":
            node_id = root_id if not dir_parts else root_id + "." + ".".join(dir_parts)
            if node_id == root_id:
                continue
            indexed[node_id] = path
            continue
        parts = [*dir_parts, _seg(rel.stem)]
        leaves.append((root_id + "." + ".".join(parts), path))

    def ensure(node_id: str) -> None:
        if node_id in known or node_id == root_id:
            return
        parent = node_id.rsplit(".", 1)[0]
        ensure(parent)
        if node_id in indexed:
            body = _body(indexed[node_id])
            src = indexed[node_id].as_posix()
        else:
            body = ""
            src = node_id
        summary = LOOSE_SUMMARY.get(node_id) or _weak(body, f"Notes for {node_id}.")
        nodes.append(_node(node_id, parent, summary, src, body))
        known.add(node_id)

    for node_id in indexed:
        ensure(node_id)
    for node_id, path in leaves:
        parent = node_id.rsplit(".", 1)[0]
        ensure(parent)
        if node_id in known:
            continue
        body = _body(path)
        summary = LOOSE_SUMMARY.get(node_id) or _weak(body, f"Notes for {node_id}.")
        nodes.append(_node(node_id, parent, summary, path.as_posix(), body))
        known.add(node_id)


def seedforge_document() -> Document:
    return pack_markdown([AGENTS / "evidence", AGENTS / "protocols"], "Seedforge")


def large_document() -> Document:
    base = seedforge_document()
    nodes = list(base.nodes)
    _add_tree(nodes, AGENTS / "sources", "sources")
    _add_tree(nodes, AGENTS / "schematics", "schematics")
    _add_tree(nodes, AGENTS / "templates", "templates")
    _add_tree(nodes, AGENTS / "skills", "skills")
    singles = [
        ("guide.system-prompt", AGENTS / "system-prompt.md"),
        ("guide.connect", AGENTS / "CONNECT.md"),
        ("guide.agents", AGENTS / "AGENTS.md"),
        ("guide.readme", AGENTS / "README.md"),
        ("guide.testing", AGENTS / "TESTING.md"),
        ("docs.using-ccd", ROOT / "docs" / "USING-CCD.md"),
        ("spec", ROOT / "SPEC.md"),
    ]
    nodes.append(_node("guide", None, LOOSE_SUMMARY.get("guide", "Agent entry files."), "agents", "# guide\n"))
    nodes.append(_node("docs", None, LOOSE_SUMMARY["docs"], "ccd/docs", "# docs\n"))
    for node_id, path in singles:
        parent = node_id.rsplit(".", 1)[0] if "." in node_id else None
        nodes.append(_node(node_id, parent, LOOSE_SUMMARY[node_id], path.as_posix(), _body(path)))
    return Document(title="Repo docs", nodes=tuple(nodes), version=3)


def _before_summaries(doc: Document) -> dict[str, str]:
    out: dict[str, str] = {}
    for node in doc.nodes:
        if node.id in OLD:
            out[node.id] = OLD[node.id]
        else:
            out[node.id] = _weak(node.body, node.id.replace(".", " "))
    return out


def _outline(doc: Document, summaries: dict[str, str]) -> str:
    depths = compute_depths(doc.nodes)
    lines = [f"# {doc.title}", f"# nodes {len(doc.nodes)}"]
    for node in doc.nodes:
        lines.append(f"{node.id} {depths[node.id]} {summaries[node.id]}")
    return "\n".join(lines) + "\n"


def _loaded_before(doc: Document, query: str, summaries: dict[str, str]) -> tuple[str, str | None]:
    ranked = rank_ids(doc, query, summaries=summaries)
    outline = _outline(doc, summaries)
    if not ranked:
        return outline, None
    chosen = next(node for node in doc.nodes if node.id == ranked[0])
    return outline + format_expand(chosen), ranked[0]


def _loaded_after(doc: Document, query: str) -> tuple[str, str | None]:
    text = render(doc)
    ranked = rank_ids(doc, query)
    parts = [map_lines(text, budget=400, depth=1)]
    if not ranked:
        return "".join(parts), None
    parts.append(find_lines(doc, query, limit=3))
    parts.append(focus_text(doc, [ranked[0]]))
    return "".join(parts), ranked[0]


def _markdown_blob(doc: Document) -> str:
    chunks: list[str] = []
    for node in doc.nodes:
        path = Path(node.src)
        if path.is_file():
            chunks.append(path.read_text(encoding="utf-8"))
        elif node.body:
            chunks.append(node.body)
    return "\n".join(chunks)


def _count(encoder: object, text: str) -> int:
    return len(encoder.encode(text))  # type: ignore[attr-defined]


def _waste(encoder: object, loaded: str, target_body: str, hit: bool) -> int:
    loaded_n = _count(encoder, loaded)
    if hit and target_body and target_body in loaded:
        return loaded_n - _count(encoder, target_body)
    return loaded_n


@dataclass(frozen=True)
class PackStats:
    name: str
    tasks: int
    before_tokens: float
    after_tokens: float
    before_hit: float
    after_hit: float
    before_waste: float
    after_waste: float
    baseline: int
    misses: tuple[str, ...]


def measure(encoder: object) -> tuple[PackStats, PackStats]:
    docs = {"seedforge": seedforge_document(), "large": large_document()}
    buckets: dict[str, list[tuple[int, int, bool, bool, int, int]]] = {name: [] for name in docs}
    misses: dict[str, list[str]] = {name: [] for name in docs}
    baselines = {name: _count(encoder, _markdown_blob(doc)) for name, doc in docs.items()}
    by_id = {name: {node.id: node for node in doc.nodes} for name, doc in docs.items()}
    before_summaries = {name: _before_summaries(doc) for name, doc in docs.items()}
    for task in TASKS:
        doc = docs[task.pack]
        if task.target not in by_id[task.pack]:
            misses[task.pack].append(f"{task.target} missing for {task.query!r}")
            continue
        target_body = by_id[task.pack][task.target].body
        before_text, before_pick = _loaded_before(doc, task.query, before_summaries[task.pack])
        after_text, after_pick = _loaded_after(doc, task.query)
        before_hit = before_pick == task.target
        after_hit = after_pick == task.target
        if not after_hit:
            top = rank_ids(doc, task.query)[:3]
            misses[task.pack].append(f"{task.query!r} -> {top} wanted {task.target}")
        buckets[task.pack].append(
            (
                _count(encoder, before_text),
                _count(encoder, after_text),
                before_hit,
                after_hit,
                _waste(encoder, before_text, target_body, before_hit),
                _waste(encoder, after_text, target_body, after_hit),
            )
        )

    def finish(name: str) -> PackStats:
        rows = buckets[name]
        count = len(rows)
        if count == 0:
            return PackStats(name, 0, 0, 0, 0, 0, 0, 0, baselines[name], tuple(misses[name]))
        return PackStats(
            name,
            count,
            sum(row[0] for row in rows) / count,
            sum(row[1] for row in rows) / count,
            sum(1 for row in rows if row[2]) / count,
            sum(1 for row in rows if row[3]) / count,
            sum(row[4] for row in rows) / count,
            sum(row[5] for row in rows) / count,
            baselines[name],
            tuple(misses[name]),
        )

    return finish("seedforge"), finish("large")


def table(stats: tuple[PackStats, ...]) -> str:
    header = (
        "pack | loop | avg tokens loaded | right-node hit rate | avg wasted tokens | whole-markdown baseline"
    )
    lines = [header]
    for item in stats:
        lines.append(
            f"{item.name} | before (full index + top body) | {item.before_tokens:.0f} | "
            f"{item.before_hit:.0%} | {item.before_waste:.0f} | {item.baseline}"
        )
        lines.append(
            f"{item.name} | after (map + find 3 + focus) | {item.after_tokens:.0f} | "
            f"{item.after_hit:.0%} | {item.after_waste:.0f} | {item.baseline}"
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    try:
        import tiktoken
    except ImportError:
        print("tiktoken is not installed", file=sys.stderr)
        return 1
    encoder = tiktoken.get_encoding("o200k_base")
    stats = measure(encoder)
    sys.stdout.write(table(stats))
    for item in stats:
        if item.misses:
            print(f"# {item.name} misses", file=sys.stderr)
            for miss in item.misses:
                print(miss, file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
