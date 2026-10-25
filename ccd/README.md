# CCD

Compact Context Distributable. A plain-text file with an index, so a model loads a map and one body instead of a whole document.

Run this from this directory. Python 3.11 or newer. No third-party packages.

```bash
python3 -m unittest discover -s tests -v
python3 -m ccd validate examples/seedforge.ccd
python3 -m ccd map examples/seedforge.ccd
python3 -m ccd find examples/seedforge.ccd "verify_kit"
python3 -m ccd focus examples/seedforge.ccd evidence.lincoln
python3 -m benchmark.attention
```

The cheap loop is map, then find, then focus, then write back. `SPEC.md` is the grammar. `docs/USING-CCD.md` is the working sequence.

`examples/seedforge.ccd` is packed from `../agents/evidence` and `../agents/protocols`. That sample is one-way: this tool may read the agents tree, and the agents tree does not call this tool.

Pack writes version 3 (readable index, token estimates, typed refs). Version 2 is an optional lossless encoding of version 1. It is not the default, because replacing short words hurts the index. Version 1 still parses.
