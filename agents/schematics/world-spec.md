# World spec layout

Regliobecky writes this set inside one run folder, then stops. Section numbers stay put so a direction line can cite §1–2, §9, and §10. The repo root stays clean. Runs do not share this folder.

```
reports/<YYYY-MM-DD>-<slug>/
  01-process.md
  02-notes.md
  03-context.md
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
  common.md                  delivery spec at the top, then the shared brief
  docs/asset-list.md         one row: id, name, batch, priority, budget, origin, seed, sockets, notes
  docs/prompts/promptN.txt   one scene or system; names ids and child pivots
  docs/batches/<name>.md     one card
  handoff/<batch>.md         Packet, Question, Next
agents/seed/                 locked seed, read in step 0
                             README.md and .gitkeep are folder docs, not seed files
```

`seeds/01` is a label for a seed file in sorted-filename order. No `seeds/` folder is created.

The four phases that fill the spec are seedinitialization, seedgermination, seedexpansion, sensesprocessing. The step numbers are the ones in `protocols/01-regliobecky-generation.md`. Each phase is written in full in `01-process.md` and `02-notes.md`.
