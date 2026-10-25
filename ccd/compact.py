"""Version 2 encoding: a reversible codebook over a version 1 document.

Writers emit version 2 only when the encoded file is shorter by the token
estimate below. The estimate is a lower bound (one token per word, one per
punctuation run, one per codebook symbol) so an entry is kept only when it
would still save tokens if the phrase were as cheap as that bound. Symbols are
single code points that cl100k and o200k both encode as one token. Relations
that are already one token, such as "because", are not abbreviated.
"""

from __future__ import annotations

import base64
import re
import zlib
from collections import Counter
from pathlib import Path

from ccd.model import CcdError

# One token in both cl100k_base and o200k_base, measured when this encoder
# was tuned. A symbol that occurs in the document is not used.
_SYMBOLS = (
    "¶†¤→•αβλ★☆µ±¿¡£¥©®°¯¬¦¨ªº›«»■●♪♥♀✔"
)
_DEFAULTS_LINE = "defaults: inferred=false fold=expanded"
_EXT_ID = re.compile(r"^[a-z][a-z0-9-]*$")
_TOKEN = re.compile(r"[A-Za-z0-9]+|[^A-Za-z0-9\s]+")


def estimate_tokens(text: str) -> int:
    """Lower-bound token estimate. No third-party tokenizer required."""
    if text == "":
        return 0
    count = 0
    for part in _TOKEN.findall(text):
        if part.isalnum() and len(part) > 24:
            count += 1 + (len(part) - 24) // 8
        else:
            count += 1
    return count


def encode_v2(v1: str) -> str:
    """Return a version 2 file, or the original text when version 2 does not win."""
    if not v1.startswith("ccd 1\n"):
        raise CcdError("version 2 encoding expects a version 1 document")
    stripped = _strip_defaults(v1)
    mapping, body = _select(stripped, v1)
    use_defaults = stripped != v1
    if not mapping and not use_defaults:
        return v1
    encoded = _format(mapping, body, defaults=use_defaults)
    if estimate_tokens(encoded) >= estimate_tokens(v1):
        return v1
    if decode_v2(encoded) != v1:
        return v1
    return encoded


def decode_v2(text: str, *, root: Path | None = None) -> str:
    """Expand a version 2 file to the exact version 1 text."""
    if not text.endswith("\n"):
        raise CcdError("file must end with a newline")
    lines = text.split("\n")
    if not lines or lines[0] != "ccd 2":
        raise CcdError("not a version 2 file")
    index = 1
    defaults = False
    if index < len(lines) and lines[index] == _DEFAULTS_LINE:
        defaults = True
        index += 1
    if index >= len(lines):
        raise CcdError("missing codebook")
    kind = lines[index]
    index += 1
    if kind == "codebook: inline":
        mapping, index = _read_inline(lines, index)
    elif kind == "codebook: -":
        mapping = []
        index = _expect_dot(lines, index)
    elif kind.startswith("codebook: ext:"):
        ident = kind[len("codebook: ext:") :]
        mapping = _load_external(ident, root)
        index = _expect_dot(lines, index)
    else:
        raise CcdError("expected codebook")
    body = "\n".join(lines[index:])
    symbols = [sym for sym, _phrase in mapping]
    for sym, phrase in mapping:
        if sym in phrase or any(other in phrase for other in symbols):
            raise CcdError("codebook phrase contains a symbol")
        body = body.replace(sym, phrase)
    if defaults:
        body = _restore_defaults(body)
    return body


def zip_text(text: str, *, armor: bool = False) -> bytes:
    """Compress UTF-8 text with zlib (RFC 1950 deflate)."""
    raw = zlib.compress(text.encode("utf-8"), level=9)
    if not armor:
        return raw
    wrapped = base64.encodebytes(raw).decode("ascii")
    return f"ccd-zip 1\n{wrapped}".encode("ascii")


def unzip_bytes(data: bytes) -> str:
    """Inflate a zlib payload or a `ccd-zip 1` ASCII armor."""
    try:
        if data.startswith(b"ccd-zip 1\n"):
            payload = b"".join(data[len(b"ccd-zip 1\n") :].split())
            raw = base64.b64decode(payload, validate=True)
        else:
            raw = data
        return zlib.decompress(raw).decode("utf-8")
    except (zlib.error, ValueError, UnicodeDecodeError) as exc:
        raise CcdError(f"zip payload is not valid: {exc}") from exc


def _select(body: str, original: str) -> tuple[list[tuple[str, str]], str]:
    pool = [sym for sym in _SYMBOLS if sym not in original]
    current = body
    chosen: list[tuple[str, str]] = []
    for gram in _candidates(body):
        if not pool:
            break
        found = current.count(gram)
        if found < 2:
            continue
        if any(sym in gram for sym, _phrase in chosen):
            continue
        weight = estimate_tokens(gram)
        if weight < 2:
            continue
        if found * (weight - 1) - (weight + 4) < 8:
            continue
        sym = pool.pop(0)
        current = current.replace(gram, sym)
        chosen.append((sym, gram))
    return chosen, current


def _candidates(text: str) -> list[str]:
    counts: Counter[str] = Counter()
    words = text.split()
    limit = len(words)
    for start in range(limit):
        for size in range(1, 13):
            end = start + size
            if end > limit:
                break
            gram = " ".join(words[start:end])
            if len(gram) < 6:
                continue
            counts[gram] += 1
    for line in text.split("\n"):
        if len(line) >= 24:
            counts[line] += 1
    ranked: list[tuple[int, int, str]] = []
    for gram, found in counts.items():
        if found < 2 or "\n" in gram:
            continue
        weight = estimate_tokens(gram)
        if weight < 2:
            continue
        save = found * (weight - 1) - (weight + 4)
        if save >= 8:
            ranked.append((save, len(gram), gram))
    ranked.sort(reverse=True)
    return [gram for _save, _length, gram in ranked]


def _format(mapping: list[tuple[str, str]], body: str, *, defaults: bool) -> str:
    lines = ["ccd 2"]
    if defaults:
        lines.append(_DEFAULTS_LINE)
    if mapping:
        lines.append("codebook: inline")
        lines.extend(f"{sym}={phrase}" for sym, phrase in mapping)
    else:
        lines.append("codebook: -")
    lines.append(".")
    return "\n".join(lines) + "\n" + body


def _strip_defaults(text: str) -> str:
    kept = [
        line
        for line in text.split("\n")
        if line not in ("inferred: false", "fold: expanded")
    ]
    return "\n".join(kept)


def _restore_defaults(text: str) -> str:
    lines = text.split("\n")
    out: list[str] = []
    index = 0
    last = len(lines)
    while index < last:
        line = lines[index]
        out.append(line)
        if line.startswith("see: "):
            nxt = lines[index + 1] if index + 1 < last else ""
            if nxt.startswith("inferred:"):
                index += 1
                out.append(lines[index])
                nxt = lines[index + 1] if index + 1 < last else ""
            else:
                out.append("inferred: false")
            if nxt.startswith("fold:"):
                index += 1
                out.append(lines[index])
            else:
                out.append("fold: expanded")
        index += 1
    return "\n".join(out)


def _read_inline(lines: list[str], index: int) -> tuple[list[tuple[str, str]], int]:
    mapping: list[tuple[str, str]] = []
    seen: set[str] = set()
    while index < len(lines) and lines[index] != ".":
        sym, phrase = _map_line(lines[index])
        if sym in seen:
            raise CcdError(f"duplicate codebook symbol {sym}")
        seen.add(sym)
        mapping.append((sym, phrase))
        index += 1
    if index >= len(lines) or lines[index] != ".":
        raise CcdError("codebook is not terminated")
    return mapping, index + 1


def _expect_dot(lines: list[str], index: int) -> int:
    if index >= len(lines) or lines[index] != ".":
        raise CcdError("expected '.'")
    return index + 1


def _map_line(line: str) -> tuple[str, str]:
    if len(line) < 3 or line[1] != "=":
        raise CcdError("invalid codebook line")
    sym = line[0]
    phrase = line[2:]
    if phrase == "" or sym in phrase or sym in ".=\n":
        raise CcdError("invalid codebook entry")
    return sym, phrase


def _load_external(ident: str, root: Path | None) -> list[tuple[str, str]]:
    if not _EXT_ID.match(ident):
        raise CcdError(f"invalid codebook id {ident}")
    name = f"{ident}.cb"
    roots = []
    if root is not None:
        roots.append(root)
    roots.append(Path.cwd())
    roots.append(Path(__file__).resolve().parents[1])
    for base in roots:
        path = base / "codebooks" / name
        if path.is_file():
            return _read_book(path.read_text(encoding="utf-8"))
    raise CcdError(f"codebook not found: {ident}")


def _read_book(text: str) -> list[tuple[str, str]]:
    mapping: list[tuple[str, str]] = []
    seen: set[str] = set()
    for line in text.split("\n"):
        if line == "":
            continue
        sym, phrase = _map_line(line)
        if sym in seen:
            raise CcdError(f"duplicate codebook symbol {sym}")
        seen.add(sym)
        mapping.append((sym, phrase))
    if not mapping:
        raise CcdError("external codebook is empty")
    return mapping
