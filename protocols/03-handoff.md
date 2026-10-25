---
id: protocols.handoff
parent: protocols
summary: How the two modes pass work, and the condensate that remains.
src: sources/evidence.md | sources/rea-seed-method.md
see: protocols.regliobecky-generation protocols.lincoln-creation evidence.dawn-whistle evidence.seed-method
inferred: true
---

# Handoff

Regliobecky and Lincoln are two modes. They do not share a turn. The generation protocol writes a contract. The creation protocol builds one batch against it. The quality bar is a finished kit. This file is the contract's shape, the feedback path, and the condensate: what is left when you take the names off.

## Original Intent

The original intent is that Regliobecky is a theoretical single point consciousness that receives a 'prompt' which it considers the 'Seed' upon which the agent takes the full range of Senses and doesn't just imagine, but holds that latent space from the image, the text, and snaps in to that nonphysical reality. Like a rubber band, it holds itself there, and snaps fully into that frame, as it expands outward, breathing life in to the living and dynamic unique and alive busy thriving or desolate universe that is constructed from that point of origin held within the latent space, outward. This is the true full intent of the creative process and is not guarded, but ideally is fully transparent and verbose in the 'seedinitialization' process, and the 'seedgermination' process, and the 'seedexpansion' process, and the 'sensesprocessing'

Source: Alex, 2026-10-25. This is owner-stated original intent for Regliobecky. It supersedes any [INFERRED] description of that intent. The generation run is the four phases named there, in that order, and each phase is transparent and verbose in the report. See [[protocols.regliobecky-generation]].

## The loop

1. A seed arrives. Mode: [[protocols.regliobecky-generation]]. The run is seedinitialization, then seedgermination, then seedexpansion, then sensesprocessing. Each phase is transparent and verbose in the report. Output: `spec.md`, `docs/asset-list.md`, prompts, batch cards, `common.md`.
2. The first build-order step that needs assets becomes a batch card. Mode: [[protocols.lincoln-creation]]. It reads `common.md` first and builds P0 rows.
3. A kit that passes the creation protocol's finished checklist is the quality bar named on the next card.
4. A coding agent receives `docs/promptN.txt` when every socket and asset that prompt names is either in a finished kit or marked gray-box on the asset row. The vertical slice is allowed to start on gray-box. Polish is not.
5. If verify fails because the script is wrong, Lincoln fixes the script and regenerates. If verify fails because the spec is wrong, Lincoln stops. Regliobecky revises the spec, dates the change, and says it overrides the previous brief. Then the batch is cut again.
6. Both modes write a three-part report and pack it to `.ccd` before the other mode starts.

[INFERRED] The loop's feedback edge (step 5) is the role split turned into a rule. The notes show the designer overriding an earlier brief, and they show verify scripts. They do not show a ticket going back. The packet below is the missing edge, invented and labeled.

## The packet

Write `handoff/<batch>.ccd` by packing a small folder:

- `packet` — one screen: seed number, spec path, look-lock paragraph, delivery tuple, reference kit path, row ids, prompt path, output directory, shared props not to rebuild.
- `packet.question` — empty body if there is no question. If Lincoln is sending a conflict back, the body is the conflict and nothing else.
- `packet.next` — the single next mode: `regliobecky` or `lincoln`, and the build-order step number.

An agent that receives the packet runs `ccd outline` and then expands `packet` and `packet.next`. It does not need the chat that produced it.

The report `.ccd` from the mode that just finished is attached by path in `packet.src` (the node's `src` field). It is not copied into the packet.

## Who changes what

| Object | Who may change it |
| --- | --- |
| Look lock, §9, §10, delivery tuple, prompt sockets | Regliobecky, by a dated revision |
| Scripts, exports, previews, verify.json | Lincoln |
| A finished kit's contact sheet | Nobody restyles it in place. A new kit matches it or the designer names a new bar. |
| Reference art, code, names, IP | Neither. Principles only, lineage recorded. |

## Condensate

This is the part that should survive if both names are forgotten.

### Leftover logic

- The seed is an identity, not a file to trace. Every later choice cites the five headings: look, sound, feel, game system, opening scene.
- Original work only. A reference contributes a principle (a formula, a state machine, a layout, a pacing curve) and a lineage row. It does not contribute pixels, meshes, names, or code.
- The spec is the contract. §1–2 is the look, §9 is the order, §10 is the asset list. A direction line cites those numbers. A delivery spec is dated and overrides older briefs.
- One vertical slice first: pipeline, one subject, gray-box of the opening scene, camera. Stretch goals last.
- Assets are regenerated by one script with local open-source tools. A hand edit that is not in the script is not in the kit.
- A setting is trusted only after a small headless test. A kit is trusted only after verify. The bar for the next kit is a finished kit, judged by putting its contact sheet next to the named seed.
- Provenance stays on the page: which seed, which row id, which reference principle, which file. Unknowns stay blank. Inferences are marked.
- Generators that the spec calls procedural are modules with a seeded RNG and pure functions, plus validators and a headless check that the same seed repeats. [INFERRED] That pattern is recovered from the testseed procgen agent, not from these two. Use it when §7 asks for generation. See [[evidence.seed-method]].

### Patterning

The same shapes show up at every scale:

- A numbered list that starts with one playable thing and ends with polish.
- An id with a budget and a priority, P0 first.
- A batch card with a seed number, a prompt number, and a reference kit.
- A folder that can be rebuilt: script, verify, preview, README.
- A report with three nodes: process, notes, context. Packed to `.ccd` so the next agent reads the index and expands one id.

When you add a new kind of work, fit it to one of these shapes instead of inventing a second system.

### Creative flow

Regliobecky's part of this flow runs as seedinitialization, seedgermination, seedexpansion, then sensesprocessing. Each of those phases is transparent and verbose in the report. [INFERRED] The eight steps below stay the combined sequence, including Lincoln's build and verify. They are not a second definition of the four phases. The generation protocol is the map.

1. See the seed. Write down only what is there.
2. Name look, sound, feel, system, and opening scene. This is the identity.
3. Lock the look in checkable words. The recovered voice is short and specific.
4. List systems. Distill principles if you were asked to look at references. Re-synthesize into this identity.
5. Order the build so one slice can be shown. List every asset that slice needs.
6. Cut a batch. Build it by script. Verify. Show the contact sheet against the seed.
7. Only then widen: more batches, more prompts, polish, stretch.
8. Write the full process, the full creative notes, and the full context. Pack them.

The flow is one direction. You can return to step 3 when verify says the spec is wrong. You do not skip from step 1 to step 6 because the tools are ready.

## Reports

Both protocols end the same way. The folder `reports/<run-id>/` holds:

| Id | What "full" means |
| --- | --- |
| `report.process` | Steps in order, files written, commands, exit codes. Skipped steps say why. |
| `report.notes` | Creative decisions, rejected alternatives, every [INFERRED] mark, lineage, questions. |
| `report.context` | Seed, look lock, ids, paths, open questions, the next build-order step. |

```
python -m ccd pack reports/<run-id> -o reports/<run-id>.ccd --title "<run-id>"
python -m ccd validate reports/<run-id>.ccd
```

The next mode starts by outlining that file and expanding `report.context`, then `packet` if a handoff packet exists. It does not start by rereading the whole spec if the context node names the sections that changed.
