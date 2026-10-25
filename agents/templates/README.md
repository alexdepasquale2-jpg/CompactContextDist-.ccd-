# Templates

Blank forms. Copy one and fill it. The procedures that define the fields are `protocols/01-regliobecky-generation.md` and `protocols/02-lincoln-creation.md`. Layouts without the blanks filled in are in `schematics/`.

| File | Use |
| --- | --- |
| `seed-brief.md` | Notes you can also drop into `seed/` as text. Not `README.md`. |
| `spec.md` | Copy to `reports/<run>/spec.md`, sections §1–§11 |
| `batch-prompt.md` | One `reports/<run>/docs/prompts/promptN.txt` |
| `report/` | `01-process.md`, `02-notes.md`, `03-context.md` |

Copy `report/` to `reports/<YYYY-MM-DD>-<slug>/` at the start of a run and fill it as you go. The spec, `common.md`, `docs/`, and `handoff/` are written in that same folder. The repo root stays clean. When a report is packed, `01-process.md` is the CCD node `report.process`, `02-notes.md` is `report.notes`, and `03-context.md` is `report.context`.
