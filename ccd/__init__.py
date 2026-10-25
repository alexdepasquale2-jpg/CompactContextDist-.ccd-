"""Compact Context Distributable. Reads version 1 and version 2."""

from ccd.codec import parse, read_index, render
from ccd.compact import decode_v2, encode_v2, estimate_tokens, unzip_bytes, zip_text
from ccd.io import pack_json, pack_markdown, unpack_json, unpack_markdown
from ccd.model import CcdError, Document, Hit, Node, problems
from ccd.ops import (
    collapse_document,
    expand_document,
    format_expand,
    outline_lines,
    search_document,
)

__version__ = "2"

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
    "format_expand",
    "outline_lines",
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
