# Handoff flow

The two modes do not share a turn. The packet is `handoff/<batch>.ccd`.

```
seed
  -> Regliobecky
       spec.md, asset list, prompts, batch cards, common.md
  -> Lincoln, one card, P0 rows
       kit that passes the finished checklist
  -> that kit's contact sheet is the bar on the next card
  -> coding agent gets prompt N when every named socket is in a finished kit or marked gray-box
```

When verify fails because the script is wrong, Lincoln fixes the script and regenerates.

When verify fails because the spec is wrong, Lincoln stops. The question goes in `packet.question`. Regliobecky revises the spec, dates the change, and says it overrides the previous brief.

```
packet
  seed, spec path, look lock, delivery, reference kit, row ids, prompt, output, shared props
  src: path of the report .ccd just written
packet.question
  empty, or the conflict and nothing else
packet.next
  regliobecky or lincoln, and the build-order step number
```

The next agent outlines the packet and expands `packet` and `packet.next`.
