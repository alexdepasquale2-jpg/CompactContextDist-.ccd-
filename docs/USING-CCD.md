# Using .ccd

Python 3.11 or newer, from the repo root. `python3 -m ccd` needs no packages. The grammar is `SPEC.md`. This file is the working sequence.

`examples/seedforge.ccd` is `evidence/` and `protocols/` packed.

## Read

The top of the file is an index: id, depth, one-line summary. Read that far and stop.

```bash
python3 -m ccd outline examples/seedforge.ccd -d 1
python3 -m ccd outline examples/seedforge.ccd -d 2
```

`-d 1` is the roots. Depth 2 includes their children. `outline` does not print bodies.

## Expand

```bash
python3 -m ccd expand examples/seedforge.ccd protocols.handoff
```

One node. A collapsed body is loaded from the store trailer. To put bodies back inline:

```bash
python3 -m ccd expand examples/seedforge.ccd --all -o /tmp/expanded.ccd
```

## Collapse

```bash
python3 -m ccd collapse examples/seedforge.ccd -o /tmp/collapsed.ccd
python3 -m ccd collapse examples/seedforge.ccd protocols.handoff -o /tmp/one.ccd
```

Collapse moves bodies into `store:`. It does not delete them. The file to commit is the expanded pack.

## Search

```bash
python3 -m ccd search examples/seedforge.ccd "verify_kit"
```

Case-insensitive substring over summary, `src`, and body, including stored bodies. Exit 0 is a hit. Exit 1 is no hit.

## Pack

```bash
python3 -m ccd pack evidence protocols -o examples/seedforge.ccd --title "Seedforge"
```

Directories of markdown, or one JSON tree. Frontmatter keys are `id`, `parent`, `summary`, `src`, `see`, `inferred`. `parent: -` and `see: -` mean none. A file with no frontmatter takes its id from the path.

Pack writes version 2 when that form estimates fewer tokens than version 1. Otherwise it writes version 1. Both validate.

## Unpack

```bash
python3 -m ccd unpack examples/seedforge.ccd -o /tmp/seedforge-docs
python3 -m ccd unpack examples/seedforge.ccd -o /tmp/seedforge.json --json
```

Unpack fails on a non-empty directory unless `--force` is set.

## Validate

```bash
python3 -m ccd validate examples/seedforge.ccd
```

Grammar, ids, parents, `see:` targets, and `[[wikilinks]]` outside fenced code. `ok <file> (N nodes)` is success.

## Write a good node

```yaml
---
id: report.context
parent: report
summary: Seed, look lock, ids, and the next build step.
src: spec.md
see: report.notes
inferred: false
---
```

- `summary` is one line, 200 characters or fewer, no surrounding space. It is the line in the index. Write it so a reader can skip the body.
- `src` is where the claim came from. Use `-` when there is none.
- `see:` is the cross-reference list the index should expose. `[[id]]` in the body is checked too.
- `inferred: true` means the node is a synthesis. Inside a recovered node, mark a local guess `[INFERRED]`.
- A directory's node is `_index.md`. Number siblings (`01-process.md`) so order survives the pack.
- One trailing newline ends the markdown file. It is not part of the body.

The report trio is `report`, `report.process`, `report.notes`, `report.context`. A blank set is `templates/report/`.

## Version 2

A version 2 file starts with `ccd 2`. Under that is an optional defaults line and a codebook, then a version 1 document whose repeated phrases have been replaced by single symbols.

```bash
python3 -m ccd outline examples/seedforge.ccd -d 1
```

The command decodes first. You do not apply the codebook by hand.

The codebook is in the header (`codebook: inline`) so a model that reads the raw file can expand it before the index. Decode is exact: the version 1 text comes back unchanged, including default `inferred: false` and `fold: expanded` lines that version 2 omits.

An entry is kept only when a lower-bound token estimate still drops after paying for the codebook line. A word that is already one token is left alone. `because` is one of those. `codebooks/relations.cb` still lists `because`, `requires`, `derived from`, and `supersedes` for an external book (`codebook: ext:relations`). Pack does not attach that book. The shipped example decodes from its own header.

Version 2 is UTF-8. Symbols were picked because they are one token on cl100k and o200k, which is shorter than the phrases they replace.

## Zip

```bash
python3 -m ccd zip examples/seedforge.ccd -o /tmp/seedforge.ccd.zip
python3 -m ccd zip examples/seedforge.ccd -o /tmp/seedforge.ccd.zz --armor
python3 -m ccd unzip /tmp/seedforge.ccd.zip -o /tmp/seedforge.ccd
```

`zip` is zlib deflate (RFC 1950). `--armor` is `ccd-zip 1` and base64, for a text channel. Zip is the small byte form. The armored form costs more tokens than the plain `.ccd`. Do not paste a zip into a prompt. Paste an outline, then expand ids.

## Examples

```bash
python3 -m ccd validate examples/seedforge.ccd templates/starter.ccd
python3 -m ccd expand examples/seedforge.ccd evidence.regliobecky
python3 -m ccd pack templates/report -o /tmp/report.ccd --title "run"
```
