# World spec layout

Regliobecky writes this set, then stops. Section numbers stay put so a direction line can cite §1–2, §9, and §10.

```
spec.md
  §1  Look
  §2  Look lock
  §3  Sound
  §4  Feel
  §5  Game system
  §6  Opening scene
  §7  Systems and reference lineage
  §8  UI
  §9  Build order          vertical slice first, polish, stretch last
  §10 Asset list           rows also copied to docs/asset-list.md
  §11 Delivery and batches
docs/asset-list.md         one row: id, name, batch, priority, budget, origin, seed, sockets, notes
docs/promptN.txt           one scene or system; names ids and child pivots
docs/batches/<name>.md     one card
common.md                  delivery spec at the top, then the shared brief
reports/<run-id>/          process, notes, context
agents/seed/               locked seed read in seedinitialization
```

The four phases that fill the spec are seedinitialization, seedgermination, seedexpansion, sensesprocessing. Each one is written in full in the report.
