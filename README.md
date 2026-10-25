# Seedforge

CompactContextDist (`.ccd`). Two former agents, one system, and a context file format.

**Regliobecky** turns a seed into a spec: a look lock, a build order, and an asset list. **Lincoln** builds one batch against that spec with local open-source tools, a regenerate script, and a verify gate. A finished kit is the quality bar for the next batch. The facts this is built from are in `evidence/`. Inferences are marked in the protocols.

`.ccd` (Compact Context Distributable) is a plain-text file an agent can skim. The top of the file is an index of ids and one-line summaries. Bodies stay folded until something asks for that id.

## Quickstart

Python 3.11 or newer. No packages to install.

```bash
python3 -m ccd validate examples/seedforge.ccd
python3 -m ccd outline examples/seedforge.ccd -d 1
python3 -m ccd expand examples/seedforge.ccd protocols.handoff
python3 -m ccd search examples/seedforge.ccd "verify_kit"
python3 -m ccd unpack examples/seedforge.ccd -o /tmp/seedforge-docs
python3 -m unittest discover -s tests -v
```

Pack a folder of markdown back into a `.ccd`:

```bash
python3 -m ccd pack evidence protocols -o examples/seedforge.ccd --title "Seedforge"
python3 -m ccd validate examples/seedforge.ccd
```

`SPEC.md` is the format. `system-prompt.md` is the bot: two modes, plus how any agent should pull and push docs as `.ccd`. The procedures are `protocols/regliobecky-generation.md`, `protocols/lincoln-creation.md`, and `protocols/handoff.md`. The same procedures, trimmed to skill files, are under `skills/`.

## Layout

```
SPEC.md                  .ccd grammar, commands, versioning
system-prompt.md         one bot, two modes
ccd/                     dependency-free library and CLI
evidence/                recovered facts, inferences marked
protocols/               generation, creation, handoff
skills/                  self-contained skill files
sources/                 the notes the evidence was drawn from
examples/seedforge.ccd   evidence + protocols, packed
tests/                   pack/unpack round trip and validation
```

A run of either mode writes `reports/<run-id>/` (process, creative notes, context) and packs `reports/<run-id>.ccd`.

## License

No license has been chosen. This note is a placeholder, not a grant of rights. Pick a license before distributing the project.
