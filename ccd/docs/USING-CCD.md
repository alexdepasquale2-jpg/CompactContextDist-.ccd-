# Using .ccd

Python 3.11 or newer, from this directory (`ccd/`). `python3 -m ccd` needs no packages. The grammar is `SPEC.md`.

`examples/seedforge.ccd` is `../agents/evidence` and `../agents/protocols` packed as version 3.

The loop is map, find, focus, write back. The tool reads the file. The model loads only what the tool prints.

## Map

Depth 1, with each root's own token estimate and the subtree total. The default budget is 400 estimated tokens. A cut map says to use find.

```bash
python3 -m ccd map examples/seedforge.ccd
python3 -m ccd map examples/seedforge.ccd --budget 120 --depth 1
```

## Find

Ranked one-liners from the index only. The body is not scored and not printed. A non-empty typed ref is appended so you can follow it without opening the other node.

```bash
python3 -m ccd find examples/seedforge.ccd "verify_kit" -n 3
python3 -m ccd links examples/seedforge.ccd protocols.lincoln-creation
```

## Focus

Ancestor one-liners, then the bodies you named. Ancestor bodies stay out.

```bash
python3 -m ccd focus examples/seedforge.ccd evidence.lincoln
python3 -m ccd focus examples/seedforge.ccd protocols.regliobecky-generation --section seedinitialization
python3 -m ccd expand examples/seedforge.ccd protocols.handoff --budget 80
```

`--section` is a markdown heading. `--budget` trims the printed body. Neither rewrites the file.

## Outline, search, collapse

`outline` prints the whole index, including the token estimate on version 3. Use it when you want every id. `search` is a substring over summary, src, and body, for when you already know a string. `collapse` moves bodies into `store:`. The file to commit is the expanded pack.

```bash
python3 -m ccd outline examples/seedforge.ccd -d 1
python3 -m ccd search examples/seedforge.ccd "verify_kit"
python3 -m ccd collapse examples/seedforge.ccd -o /tmp/collapsed.ccd
```

## Pack

```bash
python3 -m ccd pack ../agents/evidence ../agents/protocols -o examples/seedforge.ccd --title "Seedforge"
python3 -m ccd validate examples/seedforge.ccd
```

Pack writes version 3: readable summaries, a body-token estimate on each index line, and `requires`, `supersedes`, `derived-from`. Version 2 still decodes, and it is not what pack writes. Replacing short words made the index worse to scan.

Frontmatter keys are `id`, `parent`, `summary`, `src`, `see`, `inferred`, `requires`, `supersedes`, `derived-from`. A `---` block without `id:` is body (skill files stay intact). Path segments are lowercased. `parent: -` means a root.

Write the summary so find can choose the node: the point, the terms, and `answers:` what the body settles. Stay inside 200 characters.

## Unpack

```bash
python3 -m ccd unpack examples/seedforge.ccd -o /tmp/seedforge-docs
python3 -m ccd unpack examples/seedforge.ccd -o /tmp/seedforge.json --json
```

Unpack fails on a non-empty directory unless `--force` is set.

## Zip

```bash
python3 -m ccd zip examples/seedforge.ccd -o /tmp/seedforge.ccd.zip
python3 -m ccd unzip /tmp/seedforge.ccd.zip -o /tmp/seedforge.ccd
```

Zip is zlib, for bytes. Do not paste a zip or a codebook into a prompt. Call map, then find, then focus.

## Attention check

```bash
python3 -m benchmark.attention
```

The script asks about twenty questions against this example and against a larger pack of the repo's docs. It reports tokens loaded, how often the index pick is the right node, and tokens loaded that are not the target body. The comparison is the old loop (full index, then one body) against map + find + focus, and against loading the markdown whole.
