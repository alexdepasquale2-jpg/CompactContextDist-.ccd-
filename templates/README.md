# Templates

Blank forms. Copy one and fill it. The procedures that define the fields are `protocols/01-regliobecky-generation.md` and `protocols/02-lincoln-creation.md`. Layouts without the blanks filled in are in `schematics/`.

| File | Use |
| --- | --- |
| `seed-brief.md` | The seed handed to Regliobecky |
| `spec.md` | `spec.md`, sections §1–§11 |
| `batch-prompt.md` | One `docs/promptN.txt` |
| `report/` | `report.process`, `report.notes`, `report.context` |
| `starter.ccd` | A two-node `.ccd` you can outline and expand |

Pack a filled report:

```bash
python3 -m ccd pack templates/report -o /tmp/report.ccd --title "run"
python3 -m ccd validate /tmp/report.ccd
```
