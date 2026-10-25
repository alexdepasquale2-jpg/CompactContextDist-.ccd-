# Compact Context Distributable (`.ccd`)

`.ccd` is a plain UTF-8 context file for a strong model. A header index lists every node as `id`, depth, and a one-line summary. The model reads that index and stops. It expands a body only when it needs that id. The file is line-oriented so git diffs stay small.

Version 1 is the document. Version 2 is a reversible encoding of a version 1 document, chosen so the file costs fewer tokens for a model to read. A reader accepts 1 and 2. Any other version stops. It does not guess.

## Versioning

The first line is `ccd 1` or `ccd 2`. The integer is the major version.

- Readers reject a missing version, a minor suffix (`ccd 1.1`), or any major other than 1 or 2.
- Parsers reject unknown fields. A new field is a new major version, so an old reader cannot drop data in silence.
- Canonical files contain no timestamp, no hash of themselves, and no trailing whitespace on structural lines. Rewriting an unchanged document does not move unrelated lines.

## Layout

A file is LF, no BOM, and it ends with one newline. Structural lines have no trailing whitespace. Blank lines appear only inside bodies, where they are a single prefixed space.

```
ccd 1
title: <one line>
nodes: <integer>
index:
<id> <depth> <summary>
.
node <id>
parent: <id or ->
summary: <one line>
src: <one line>
see: <- or ids>
inferred: <true or false>
fold: <expanded or collapsed>
body:                 # expanded only
 <body line>
.
store:                # only if some fold is collapsed
node <id>
body:
 <body line>
.
.
```

`nodes:` is the number of index lines and the number of `node` blocks. Depth starts at 1 for a node whose parent is `-`. A child's depth is its parent's depth plus 1. The index is preorder, the same order as the node blocks. Parents appear before their children.

## Grammar

This grammar is version 1. Version 2 decodes to this text before the checks below run.

```
file        = header index node* store?
header      = "ccd 1" NL "title: " text NL "nodes: " int NL
index       = "index:" NL index-line* "." NL
index-line  = id SP depth SP summary NL
node        = "node " id NL
              "parent: " (id / "-") NL
              "summary: " summary NL
              "src: " text NL
              "see: " ("-" / (id (SP id)*)) NL
              "inferred: " ("true" / "false") NL
              fold
fold        = "fold: expanded" NL "body:" NL body-line* "." NL
            / "fold: collapsed" NL "." NL
store       = "store:" NL store-node* "." NL
store-node  = "node " id NL "body:" NL body-line* "." NL
body-line   = SP *text NL
id          = segment ("." segment)*
segment     = [a-z] [a-z0-9-]*
depth       = [1-9] [0-9]*
int         = "0" / [1-9] [0-9]*
```

`text` and `summary` are one line. They contain no characters below U+0020. `summary` and `title` are 1 to 200 characters and have no surrounding space. `src` is 1 to 2000 characters. A body line's first character is always a space, so a line that is only `.` can live in a body as ` .` and cannot end the node. The terminator `.` is column 0.

Field order is fixed. A missing field, an extra field, or a reordered field is a syntax error.

## Index, expand, collapse

The cheap read is the bytes from the start through the `.` that ends the index. `ccd outline` prints that index and does not need the bodies to be valid. `ccd outline -d N` keeps rows whose depth is less than or equal to N.

`fold: expanded` stores the body inline. `fold: collapsed` omits it from the node and keeps it in `store`, in the same order as the collapsed nodes. Collapse does not delete text. `ccd expand FILE ID` prints one node, loading the body from the store when the fold is collapsed. `ccd expand FILE --all -o OUT` and `ccd collapse FILE [ID] -o OUT` rewrite the file. Unpacking always uses the full body.

The canonical pack output is fully expanded and has no `store`. Pack writes version 2 when that encoding's token estimate is lower than version 1, and version 1 otherwise. Collapse is a reading projection.

## Version 2

Version 2 is not a second grammar. Decode it and the result is the exact version 1 text, including every default field.

```
ccd 2
defaults: inferred=false fold=expanded
codebook: inline
¶=<phrase with no newline>
.
ccd 1
...version 1 text, with phrases replaced by their symbols...
```

`defaults:` is present only when lines that were exactly `inferred: false` or `fold: expanded` were removed. A missing `inferred:` line means false. A missing `fold:` line means expanded. `inferred: true` and `fold: collapsed` stay written out.

`codebook:` is one of:

- `inline`, then one `symbol=phrase` line per entry, then a `.` line. The symbol is one code point. The phrase is the rest of the line and may start with a space. Phrases do not contain a symbol from this book.
- `-`, then a `.` line, when the only saving is the omitted defaults.
- `ext:<id>`, then a `.` line. The book is `codebooks/<id>.cb`, one `symbol=phrase` line per entry. `codebooks/relations.cb` maps `because`, `requires`, `derived from`, and `supersedes`. An external book is not in the header, so a model that has only the `.ccd` cannot expand it. Pack does not use an external book. The auto book is inline, so the file decodes from its own header.

The encoder keeps a phrase only when a lower-bound token estimate still falls after paying for the codebook line. The bound is one token per word, one per punctuation run, and one per symbol. Words that are already a single token are not abbreviated. `because` is one of those. Symbols are drawn from a fixed set that cl100k and o200k each encode as one token, skipping any symbol that already occurs in the document.

`outline`, `expand`, `search`, and `validate` decode first. They show plain text. A model that reads the raw file applies the header the same way, then stops at the index.

Version 2 is UTF-8. It is not an ASCII-only encoding. The symbol set is whatever measured shorter on real tokenizers.

`ccd zip` wraps the file bytes with zlib (deflate, RFC 1950). `ccd unzip` inflates them. `--armor` writes `ccd-zip 1` plus base64. Armor is for a text channel. It is larger in tokens than the plain `.ccd`. Zip wins bytes. It is not the form to paste into a prompt.

## Cross-references and provenance

`see:` lists other ids in this file, single-spaced, or `-` when there are none. Duplicates, self-references, and missing ids are validation errors.

A body may also name a node as `[[id]]`. Validation resolves those wikilinks. Links inside a fenced code block (a line whose first characters are three backticks) are not resolved. Prefer `see:` for links the index should expose without opening the body.

`src:` is a provenance pointer. Use `-` when there is none. Recommended shapes, joined by ` | ` when there are several:

- `path/file.md`
- `path/file.md:12-40`
- `sources/evidence.md | bc-ce93cafa-fa53-5c05-85a7-dc32b3c746a3`

The pointer is not fetched. It tells the next reader where the claim came from. `inferred: true` means the node is a synthesis, not a recovered extract. Recovered extracts stay `inferred: false` and mark local guesses inline as `[INFERRED]`.

## Pack and unpack

`ccd pack` accepts one JSON tree, or one or more markdown files and directories.

JSON:

```json
{
  "title": "Min",
  "nodes": [
    {
      "id": "kit",
      "parent": null,
      "summary": "A finished kit is the quality bar.",
      "src": "-",
      "see": [],
      "inferred": false,
      "body": "text"
    }
  ]
}
```

Unknown JSON keys are errors. Parents may be listed after their children; pack rewrites the file into preorder. Sibling order follows input order.

Markdown uses this frontmatter, or omits it:

```yaml
---
id: kit.socket
parent: kit
summary: Child pivots named by the build prompt.
src: -
see: -
inferred: false
---
```

Keys are only `id`, `parent`, `summary`, `src`, `see`, `inferred`. Values are not quoted. `parent: -` and `see: -` mean none. A file that starts without `---` is all body. Then the id comes from the path (a leading `NN-` on a filename is an order prefix, not part of the id; `_index.md` is the directory's node), the summary comes from the first heading or the first non-empty line (cut to 200 characters), `src` is the file path, and `inferred` is false. A listed parent that has no node is an error. Add an `_index.md` for that directory.

Unpack writes the forest back to markdown. A node with children becomes a directory whose `_index.md` is the node. Leaves are files. Siblings are numbered so path order matches pack order. `ccd unpack --json` writes the JSON tree instead. Unpacking a non-empty directory fails unless `--force` is set.

Round-trip means `pack(unpack(document))` renders the same `.ccd`, and JSON unpacks to the same node fields. It does not mean a hand-written note with no frontmatter is byte-identical after a trip. Bodies are. One trailing newline at the end of a markdown file is the file terminator, not part of the body. A body that itself ends in a newline unpacks with a blank line before the end of the file.

## Commands

```
python -m ccd pack <path>... -o <file.ccd> --title <title>
python -m ccd outline <file.ccd> [-d N]
python -m ccd expand <file.ccd> <id>
python -m ccd expand <file.ccd> (--all | <id>) (--inplace | -o <file>)
python -m ccd collapse <file.ccd> [id] [--inplace | -o <file>]
python -m ccd search <file.ccd> <query>
python -m ccd validate <file.ccd>...
python -m ccd unpack <file.ccd> -o <dir>
python -m ccd unpack <file.ccd> -o <file.json> --json
python -m ccd zip <file.ccd> -o <file.ccd.zip>
python -m ccd zip <file.ccd> -o <file.ccd.zz> --armor
python -m ccd unzip <file.ccd.zip> -o <file.ccd>
```

Search is a case-insensitive substring over id text in the hits, plus summary, `src`, and body, including bodies that live in the store. Exit 0 is a hit. Exit 1 is no hit, a validation failure, or an unknown id. Exit 2 is bad usage. There are no third-party dependencies. The library surface is `ccd.parse`, `ccd.render`, `ccd.read_index`, `ccd.pack_markdown`, `ccd.pack_json`, `ccd.unpack_markdown`, `ccd.unpack_json`, `ccd.problems`, `ccd.outline_lines`, `ccd.search_document`, `ccd.collapse_document`, `ccd.expand_document`, `ccd.encode_v2`, `ccd.decode_v2`, `ccd.estimate_tokens`, `ccd.zip_text`, and `ccd.unzip_bytes`. Token counts in the comparison notes use tiktoken when it is installed. The encoder itself does not import it.

## Example

```ccd
ccd 1
title: Min
nodes: 2
index:
kit 1 A finished kit is the quality bar.
kit.socket 2 Child pivots named by the build prompt.
.
node kit
parent: -
summary: A finished kit is the quality bar.
src: sources/evidence.md
see: kit.socket
inferred: false
fold: expanded
body:
 The contact sheet is the bar for the next batch.
 [[kit.socket]]
.
node kit.socket
parent: kit
summary: Child pivots named by the build prompt.
src: -
see: -
inferred: true
fold: expanded
body:
 Pivot at the grip, parented to the prop.
.
```

A collapsed `kit` keeps its index line and moves the two body lines under `store:`. `ccd expand file.ccd kit` prints them either way. `examples/seedforge.ccd` is this format packed from `evidence/` and `protocols/`.
