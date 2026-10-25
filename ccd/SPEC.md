# Compact Context Distributable (`.ccd`)

`.ccd` is a plain UTF-8 context file for a strong model. The goal is attention, not file size: how many tokens a model must load, and how much irrelevant text sits in that load, before it is looking at the node a task needs. A header index lists every node. The model does not load that whole index when a tool can do it. The cheap loop is `ccd map`, then `ccd find`, then `ccd focus`, then write back. The file is line-oriented so git diffs stay small.

Version 1 is the document. Version 3 is the same document plus a token estimate on each index line and typed cross-references, and it is what `ccd pack` writes. Version 2 is a reversible encoding of a version 1 document. It can be shorter, and it is not the default: substituting short words makes the index harder to scan. A reader accepts 1, 2, and 3. Any other version stops. It does not guess.

## Versioning

The first line is `ccd 1`, `ccd 2`, or `ccd 3`. The integer is the major version.

- Readers reject a missing version, a minor suffix (`ccd 1.1`), or any major other than 1, 2, or 3.
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

The bytes from the start through the `.` that ends the index are enough to rank ids. `ccd outline` prints that index and does not need the bodies to be valid. `ccd outline -d N` keeps rows whose depth is less than or equal to N. Outline is the whole index. Prefer `ccd map` when the model itself must see a header: it prints depth-1 rows (own tokens and subtree tokens) inside a budget, and it tells the model to call `ccd find` if the map was cut.

`fold: expanded` stores the body inline. `fold: collapsed` omits it from the node and keeps it in `store`, in the same order as the collapsed nodes. Collapse does not delete text. `ccd expand FILE ID` prints one node, loading the body from the store when the fold is collapsed. `--section` keeps one markdown heading and its body, through the next heading of the same or higher level. `--budget N` stops the printed body after about N estimated tokens and marks the cut. Those two flags print; they do not rewrite the file. `ccd expand FILE --all -o OUT` and `ccd collapse FILE [ID] -o OUT` rewrite the file. Unpacking always uses the full body.

The canonical pack output is fully expanded version 3 and has no `store`. Version 2 remains available as `render(..., version=2)` for a lossless encoding of the version 1 text. Pack does not apply it. Collapse is a reading projection.

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

`outline`, `map`, `expand`, `search`, and `validate` decode version 2 first. They show plain text. A model that reads a raw version 2 file applies the header the same way, then stops at the index. Do not paste a version 2 codebook into a prompt when you can call `ccd map` on a version 3 file instead. The codebook stays available. It is the wrong tool when the index has to stay readable.

Version 2 is UTF-8. It is not an ASCII-only encoding. The symbol set is whatever measured shorter on real tokenizers.

`ccd zip` wraps the file bytes with zlib (deflate, RFC 1950). `ccd unzip` inflates them. `--armor` writes `ccd-zip 1` plus base64. Armor is for a text channel. It is larger in tokens than the plain `.ccd`. Zip wins bytes. It is not the form to paste into a prompt.

## Version 3

Version 3 is the attention form. The grammar of version 1 still holds, with two additions. An index line is `id depth tokens summary`. `tokens` is `estimate_tokens` of that node's body (one token per word, one per punctuation run). It is a stable lower bound, not a vendor tokenizer count. The benchmark that compares loops uses tiktoken o200k on the strings the model would actually see. The number in the file does not depend on tiktoken, so a repack does not churn when the tokenizer is absent.

The summary is the line the ranker sees. Write it as the point of the node, the terms a question would use, and an `answers:` clause naming what the body settles. Cap remains 200 characters. A vague summary forces a body load.

After `see:` a version 3 node has three typed lists, each `-` or single-spaced ids:

```
requires: -
supersedes: -
derived-from: -
```

`requires` is what you need before this node. `supersedes` is what this node replaces. `derived-from` is where it was drawn. The same checks as `see:` apply: the id exists, it is not this node, it is not repeated in that field. `ccd links` prints these lists and does not print bodies. `ccd find` appends a non-empty list to its one-liner so a follow-up id is visible without a second load.

`ccd find QUERY` scores the query against id and summary only. Bodies are not in the score. It prints ranked one-liners. `ccd focus ID` prints ancestor one-liners (id, depth, tokens, summary) and then the target body. Ancestor bodies stay unloaded. `--budget` and `--section` apply to that body the same way as `ccd expand`.

```
ccd 3
title: Min
nodes: 2
index:
kit 1 9 A finished kit is the quality bar. answers: contact sheet
kit.socket 2 6 Child pivots named by the build prompt. answers: grip
.
node kit
parent: -
summary: A finished kit is the quality bar. answers: contact sheet
src: sources/evidence.md
see: kit.socket
requires: -
supersedes: -
derived-from: -
inferred: false
fold: expanded
body:
 The contact sheet is the bar for the next batch.
 [[kit.socket]]
.
node kit.socket
parent: kit
summary: Child pivots named by the build prompt. answers: grip
src: -
see: -
requires: kit
supersedes: -
derived-from: -
inferred: true
fold: expanded
body:
 Pivot at the grip, parented to the prop.
.
```

That fence is an illustration. The first `ccd` example in this file is still version 1, and a version 1 reader rejects version 3 instead of dropping the new fields.

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

Keys are `id`, `parent`, `summary`, `src`, `see`, `inferred`, `requires`, `supersedes`, and `derived-from`. Values are not quoted. `parent: -` and a ref field of `-` mean none. The three typed ref keys may be omitted; omitted means none. A `---` block is frontmatter only when it contains an `id:` line. A skill file that opens with `name:` is body, fence included. A file that starts without CCD frontmatter is all body. Then the id comes from the path (a leading `NN-` on a filename is an order prefix, not part of the id; a path segment is lowercased; `_index.md` is the directory's node), the summary comes from the first heading or the first non-empty line (cut to 200 characters), `src` is the file path, and `inferred` is false. A listed parent that has no node is an error. Add an `_index.md` for that directory.

Unpack writes the forest back to markdown. A node with children becomes a directory whose `_index.md` is the node. Leaves are files. Siblings are numbered so path order matches pack order. `ccd unpack --json` writes the JSON tree instead. Unpacking a non-empty directory fails unless `--force` is set.

Round-trip means `pack(unpack(document))` renders the same `.ccd`, and JSON unpacks to the same node fields. It does not mean a hand-written note with no frontmatter is byte-identical after a trip. Bodies are. One trailing newline at the end of a markdown file is the file terminator, not part of the body. A body that itself ends in a newline unpacks with a blank line before the end of the file.

## Commands

```
python -m ccd map <file.ccd> [--budget N] [--depth N]
python -m ccd find <file.ccd> <query> [-n N]
python -m ccd focus <file.ccd> <id>... [--budget N] [--section HEADING]
python -m ccd links <file.ccd> [id]
python -m ccd pack <path>... -o <file.ccd> --title <title>
python -m ccd outline <file.ccd> [-d N]
python -m ccd expand <file.ccd> <id> [--budget N] [--section HEADING]
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

Run these from the `ccd/` directory. `map` defaults to depth 1 and a budget of 400 estimated tokens. `find` defaults to 8 one-liners and does not open bodies. `focus` is the body load.

Search is a case-insensitive substring over summary, `src`, and body, including bodies that live in the store. It is for a known string, not for choosing a node. Exit 0 is a hit. Exit 1 is no hit, a validation failure, or an unknown id. Exit 2 is bad usage. There are no third-party dependencies. The library surface is `ccd.parse`, `ccd.render`, `ccd.read_index`, `ccd.pack_markdown`, `ccd.pack_json`, `ccd.unpack_markdown`, `ccd.unpack_json`, `ccd.problems`, `ccd.outline_lines`, `ccd.map_lines`, `ccd.find_lines`, `ccd.focus_text`, `ccd.rank_ids`, `ccd.links_lines`, `ccd.search_document`, `ccd.collapse_document`, `ccd.expand_document`, `ccd.encode_v2`, `ccd.decode_v2`, `ccd.estimate_tokens`, `ccd.zip_text`, and `ccd.unzip_bytes`. Comparison notes may use tiktoken when it is installed. The encoder and the index estimate do not import it.

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

A collapsed `kit` keeps its index line and moves the two body lines under `store:`. `ccd expand file.ccd kit` prints them either way. `examples/seedforge.ccd` is version 3 packed from `../agents/evidence` and `../agents/protocols`.
