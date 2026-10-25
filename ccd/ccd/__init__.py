"""Compact Context Distributable. Reads versions 1, 2, and 3."""

from ccd.codec import parse, read_index, render
from ccd.compact import decode_v2, encode_v2, estimate_tokens, unzip_bytes, zip_text
from ccd.io import pack_json, pack_markdown, unpack_json, unpack_markdown
from ccd.model import CcdError, Document, Hit, Node, problems
from ccd.ops import (
    collapse_document,
    expand_document,
    find_lines,
    focus_text,
    format_expand,
    links_lines,
    map_lines,
    outline_lines,
    rank_ids,
    search_document,
)

__version__ = "3"

__all__ = [
    "CcdError",
    "Document",
    "Hit",
    "Node",
    "collapse_document",
    "decode_v2",
    "encode_v2",
    "estimate_tokens",
    "expand_document",
    "find_lines",
    "focus_text",
    "format_expand",
    "links_lines",
    "map_lines",
    "outline_lines",
    "rank_ids",
    "pack_json",
    "pack_markdown",
    "parse",
    "problems",
    "read_index",
    "render",
    "search_document",
    "unpack_json",
    "unpack_markdown",
    "unzip_bytes",
    "zip_text",
]
