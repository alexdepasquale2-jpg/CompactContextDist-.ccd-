# Handoff flow

The two modes do not share a turn. The packet is `reports/<run>/handoff/<batch>.md`. The seed those modes start from is every file in `agents/seed/` except `README.md` and `.gitkeep`. Those two are folder docs, never part of the seed. Run artifacts stay inside the run folder.

```
seed
  -> Regliobecky
       reports/<run>/spec.md, docs/asset-list.md, docs/prompts/, docs/batches/, common.md
  -> Lincoln, one card, P0 rows
       kit that passes the finished checklist
  -> that kit's contact sheet is the bar on the next card
  -> coding agent gets prompt N when every named socket is in a finished kit or marked gray-box
       and that asset is in the same batch or an earlier one
```

When verify fails because the script is wrong, Lincoln fixes the script and regenerates.

When verify fails because the spec is wrong, Lincoln stops. The question goes under `Question`. Regliobecky revises the spec, dates the change, and says it overrides the previous brief.

```
# Packet
seed, spec path, look lock, delivery, reference kit, row ids, prompt, output, shared props
path of the report folder just written

# Question
empty, or the conflict and nothing else

# Next
regliobecky or lincoln, and the build-order step number
```

The next agent reads those three headings.
