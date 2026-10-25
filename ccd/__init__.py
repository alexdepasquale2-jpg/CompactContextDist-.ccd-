"""Compact Context Distributable, version 1."""

from ccd.codec import parse, read_index, render
from ccd.io import pack_json, pack_markdown, unpack_json, unpack_markdown
from ccd.model import CcdError, Document, Hit, Node, problems
from ccd.ops import (
    collapse_document,
    expand_document,
    format_expand,
    outline_lines,
    search_document,
)

__version__ = "1"

__all__ = [
    "CcdError",
    "Document",
    "Hit",
    "Node",
    "collapse_document",
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
]
