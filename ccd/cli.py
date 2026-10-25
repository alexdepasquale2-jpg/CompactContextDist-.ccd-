"""Command line for the .ccd reference tool."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from ccd.codec import parse, render
from ccd.compact import unzip_bytes, zip_text
from ccd.io import pack_json, pack_markdown, unpack_json, unpack_markdown
from ccd.model import CcdError, problems
from ccd.ops import collapse_document, expand_document, format_expand, outline_lines, search_document


def main(argv: list[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    command = args.cmd
    try:
        if command == "pack":
            return _pack(args)
        if command == "outline":
            return _outline(args)
        if command == "expand":
            return _expand(args)
        if command == "collapse":
            return _collapse(args)
        if command == "search":
            return _search(args)
        if command == "validate":
            return _validate(args)
        if command == "unpack":
            return _unpack(args)
        if command == "zip":
            return _zip(args)
        if command == "unzip":
            return _unzip(args)
        print(f"unhandled command {command}", file=sys.stderr)
        return 2
    except CcdError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except OSError as exc:
        print(str(exc), file=sys.stderr)
        return 1


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ccd",
        description="Read and write Compact Context Distributable (.ccd) files.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    pack = sub.add_parser("pack", help="pack markdown directories or a JSON tree")
    pack.add_argument("inputs", nargs="+")
    pack.add_argument("-o", "--output", required=True)
    pack.add_argument("--title", default=None)

    outline = sub.add_parser("outline", help="print the header index")
    outline.add_argument("file")
    outline.add_argument("-d", "--depth", type=int, default=None)

    expand = sub.add_parser("expand", help="show one node, or write bodies back inline")
    expand.add_argument("file")
    expand.add_argument("id", nargs="?")
    expand.add_argument("--all", action="store_true")
    expand.add_argument("--inplace", action="store_true")
    expand.add_argument("-o", "--output")

    collapse = sub.add_parser("collapse", help="move bodies into the store trailer")
    collapse.add_argument("file")
    collapse.add_argument("id", nargs="?")
    collapse.add_argument("--inplace", action="store_true")
    collapse.add_argument("-o", "--output")

    search = sub.add_parser("search", help="substring search over summaries, src, and bodies")
    search.add_argument("file")
    search.add_argument("query")

    validate = sub.add_parser("validate", help="check grammar and cross-references")
    validate.add_argument("files", nargs="+")

    unpack = sub.add_parser("unpack", help="write markdown files or JSON")
    unpack.add_argument("file")
    unpack.add_argument("-o", "--output", required=True)
    unpack.add_argument("--json", action="store_true")
    unpack.add_argument("--force", action="store_true")

    zipping = sub.add_parser("zip", help="deflate a .ccd with zlib; --armor writes ASCII")
    zipping.add_argument("file")
    zipping.add_argument("-o", "--output", required=True)
    zipping.add_argument("--armor", action="store_true")

    unzipping = sub.add_parser("unzip", help="inflate a zlib payload or ccd-zip armor")
    unzipping.add_argument("file")
    unzipping.add_argument("-o", "--output", required=True)
    return parser


def _pack(args: argparse.Namespace) -> int:
    paths = [Path(item) for item in args.inputs]
    if len(paths) == 1 and paths[0].suffix == ".json":
        doc = pack_json(paths[0].read_text(encoding="utf-8"), title_override=args.title)
    else:
        if not args.title:
            print("markdown pack requires --title", file=sys.stderr)
            return 2
        doc = pack_markdown(paths, args.title)
    text = render(doc)
    found = problems(parse(text))
    if found:
        print("\n".join(found), file=sys.stderr)
        return 1
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(text, encoding="utf-8")
    print(f"wrote {output} ({len(doc.nodes)} nodes)")
    return 0


def _outline(args: argparse.Namespace) -> int:
    text = Path(args.file).read_text(encoding="utf-8")
    sys.stdout.write(outline_lines(text, depth=args.depth))
    return 0


def _expand(args: argparse.Namespace) -> int:
    if args.inplace and args.output:
        print("use --inplace or -o, not both", file=sys.stderr)
        return 2
    if args.all and args.id:
        print("pass an id or --all, not both", file=sys.stderr)
        return 2
    path = Path(args.file)
    doc = parse(path.read_text(encoding="utf-8"))
    writing = bool(args.inplace or args.output)
    if writing:
        if not args.all and not args.id:
            print("expand write needs an id or --all", file=sys.stderr)
            return 2
        updated = expand_document(doc, None if args.all else args.id)
        dest = path if args.inplace else Path(args.output)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(render(updated), encoding="utf-8")
        print(f"wrote {dest}")
        return 0
    if not args.id:
        print("expand needs an id", file=sys.stderr)
        return 2
    for node in doc.nodes:
        if node.id == args.id:
            sys.stdout.write(format_expand(node))
            return 0
    print(f"unknown id {args.id}", file=sys.stderr)
    return 1


def _collapse(args: argparse.Namespace) -> int:
    if args.inplace and args.output:
        print("use --inplace or -o, not both", file=sys.stderr)
        return 2
    path = Path(args.file)
    doc = parse(path.read_text(encoding="utf-8"))
    updated = collapse_document(doc, args.id)
    text = render(updated)
    if args.inplace:
        path.write_text(text, encoding="utf-8")
        print(f"wrote {path}")
        return 0
    if args.output:
        dest = Path(args.output)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text, encoding="utf-8")
        print(f"wrote {dest}")
        return 0
    sys.stdout.write(text)
    return 0


def _search(args: argparse.Namespace) -> int:
    doc = parse(Path(args.file).read_text(encoding="utf-8"))
    hits = search_document(doc, args.query)
    if not hits:
        print("no hits", file=sys.stderr)
        return 1
    for hit in hits:
        place = hit.field if hit.line is None else f"{hit.field}:{hit.line}"
        print(f"{hit.node_id} {place} {hit.text}")
    return 0


def _validate(args: argparse.Namespace) -> int:
    failed = False
    for name in args.files:
        text = Path(name).read_text(encoding="utf-8")
        try:
            doc = parse(text)
        except CcdError as exc:
            print(str(exc), file=sys.stderr)
            failed = True
            continue
        found = problems(doc)
        if found:
            for item in found:
                print(f"{name}: {item}", file=sys.stderr)
            failed = True
        else:
            print(f"ok {name} ({len(doc.nodes)} nodes)")
    return 1 if failed else 0


def _unpack(args: argparse.Namespace) -> int:
    doc = parse(Path(args.file).read_text(encoding="utf-8"))
    dest = Path(args.output)
    if args.json:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(unpack_json(doc), encoding="utf-8")
    else:
        unpack_markdown(doc, dest, force=args.force)
    print(f"unpacked {len(doc.nodes)} nodes to {dest}")
    return 0


def _zip(args: argparse.Namespace) -> int:
    text = Path(args.file).read_text(encoding="utf-8")
    payload = zip_text(text, armor=args.armor)
    dest = Path(args.output)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(payload)
    print(f"wrote {dest} ({len(payload)} bytes)")
    return 0


def _unzip(args: argparse.Namespace) -> int:
    text = unzip_bytes(Path(args.file).read_bytes())
    dest = Path(args.output)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(text, encoding="utf-8")
    print(f"wrote {dest}")
    return 0
