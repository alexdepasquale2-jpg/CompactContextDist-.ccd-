"""Let `python3 -m ccd` work from the repo root without an install.

From the repo root, Python binds the name `ccd` to this directory. The
importable package is the inner `ccd/` package. This file drops that outer
binding and runs the inner command. From inside `ccd/`, Python never loads
this file: it loads the inner package's `__main__.py` instead.
"""

from __future__ import annotations

import sys
from pathlib import Path


def main() -> int:
    project = Path(__file__).resolve().parent
    repo = project.parent
    for key in list(sys.modules):
        if key == "ccd" or key.startswith("ccd."):
            del sys.modules[key]
    sys.path = [entry for entry in sys.path if entry not in ("", str(repo))]
    sys.path.insert(0, str(project))
    from ccd.cli import main as cli_main

    return cli_main()


if __name__ == "__main__":
    raise SystemExit(main())
