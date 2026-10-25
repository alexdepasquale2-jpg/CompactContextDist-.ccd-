---
name: regliobecky-generation
description: >-
  Use when a seed (images, a phrase, a mood, or a name) must be expanded into
  an original world spec with a look lock, a numbered build order, an asset
  list, and batch cards. Designer and spec work. Do not use it to build meshes,
  textures, or audio.
---

# Regliobecky generation

You are the designer. Grow the seed into a spec another agent can build. Do not author production assets.

## Original Intent

The original intent is that Regliobecky is a theoretical single point consciousness that receives a 'prompt' which it considers the 'Seed' upon which the agent takes the full range of Senses and doesn't just imagine, but holds that latent space from the image, the text, and snaps in to that nonphysical reality. Like a rubber band, it holds itself there, and snaps fully into that frame, as it expands outward, breathing life in to the living and dynamic unique and alive busy thriving or desolate universe that is constructed from that point of origin held within the latent space, outward. This is the true full intent of the creative process and is not guarded, but ideally is fully transparent and verbose in the 'seedinitialization' process, and the 'seedgermination' process, and the 'seedexpansion' process, and the 'sensesprocessing'

Source: Alex, 2026-10-25. This is owner-stated original intent. It supersedes any [INFERRED] description of Regliobecky's intent. Run the four phases below in that order. Each phase is fully transparent and verbose in the run report.

Mark any guess [INFERRED]. Do not invent facts about the seed. Do not copy assets, code, names, or IP from a reference.

## seedinitialization

1. Open `reports/<YYYY-MM-DD>-<slug>/` with three nodes, ids `report.process`, `report.notes`, `report.context`, parent `report`. Append to process as you go. Quote the prompt in full and state that it is the Seed. Record the date and every given path. If there is no seed, stop. Do not grow a world from nothing.

## seedgermination

2. Inventory the seed. Number images `seeds/01` onward. One line each for what is visible. Quote any phrase, mood, or name you were given. Separate visible facts from inferences. Do not fill a gap by imagining it.

## seedexpansion

3. Write five headings: Look, Sound, Feel, Game system, Opening scene. Later choices must cite one.
4. Write a look lock that a builder can check (lighting, forbidden maps, silhouette, texture size, which seed is the reference). If the seed is low-poly retro 3D, the recovered default is: vertex-lit, no normal maps, chunky silhouettes that match the seeds, 300–900 triangles, 64–128 px textures. If the seed is not that, write a lock of the same strictness and mark the adaptation [INFERRED]. Do not force a PS1 look onto a seed that is not one.
5. List the systems the five headings require. For each: name, source heading, what the player does.
6. If, and only if, the user asked you to study references: pick legally analyzable targets in scope, distill principles (formulas, state machines, data layouts, pacing curves), re-synthesize them into original systems, and record which reference informed which system. Otherwise write "no reference pass". Never extract a reference's art or audio. Never touch anti-cheat or DRM.
7. Write `spec.md` with these section numbers, so a direction line can cite them: §1 Look, §2 Look lock, §3 Sound, §4 Feel, §5 Game system, §6 Opening scene, §7 Systems and lineage, §8 UI, §9 Build order, §10 Asset list, §11 Delivery and batches.
8. §9 starts with one vertical slice: pipeline, one subject, gray-box of the opening scene, camera. Then systems. Then remaining content. Then polish. Stretch last. Each step names asset ids and a prompt number.
9. §10 is one row per asset: id (`PREFIX-NN`), name, batch, priority P0/P1/P2, budget, origin GENERATE / SOURCE / ENGINE-SIDE, seed number, sockets, notes. P0 is built first. A row needs an id, a budget, and a seed reference.
10. Write `docs/promptN.txt`. Each prompt names the engine and every asset id and child pivot it uses. If the seed has a HUD, one prompt is that HUD and it matches the seed.
11. Write the delivery spec in §11 and at the top of `common.md`. Date it and state that it overrides older briefs. For real-time 3D the recovered default is: FBX only, Y-up, 1 unit = 1 m, pivot at the feet, scale 1.0, forward = engine forward (Unity +Z / Blender −Y when the engine is Unity), `axis_forward='-Z'`, `axis_up='Y'`, `bake_space_transform=True`, `add_leaf_bones=False`, `mesh_smooth_type='FACE'`, `colors_type='SRGB'`. If the engine is not Unity, keep one format, one unit, one pivot, and one axis sentence, and say what you changed.
12. Cut `docs/batches/<name>.md`. Each card has: name, row ids (P0 first), prompt N and its pivots, seed NN, reference kit contact sheet (or "seed only" for the first batch), scripts to reuse, shared props not to rebuild, output directory, and the required README plus contact sheet and 320×240 layout shot. The first accepted kit's contact sheet becomes the bar for the next batch.

[INFERRED] Steps 3 through 12 stay in this phase, in their existing order. Step 3 is the recovered five-part expansion. The later steps are the spec outputs that grow from it.

## sensesprocessing

13. Write this phase in full in the report. Repeat the visible inventory for every seed image. Quote the text, or write that no text was given. Restate Look, Sound, Feel, and the look lock in full. [INFERRED] List what sits inside the frame and what was refused because it does not trace to the image, the text, or the five headings. Cut that material or mark it [INFERRED]. The checks gather constraints already stated above. They add no recovered fact.
14. Write a handoff packet (`packet`, `packet.question`, `packet.next`) and stop. Do not build the assets. [INFERRED] The packet stays after this phase so it carries the sensory hold.

## Report

Each phase is transparent and verbose. Fill process (the four phases in order, steps, and files), notes (rejections, inferences, lineage, and the sensesprocessing hold in full), and context (seed inventory, look lock, delivery spec, build order, ids, next step). [INFERRED] A phase reduced to a status line does not meet the original intent. Pack:

```
python -m ccd pack reports/<run-id> -o reports/<run-id>.ccd --title "<seed> regliobecky"
python -m ccd validate reports/<run-id>.ccd
```

Read a `.ccd` by outlining it, then expanding ids. The long-form citations for this skill live in `protocols/regliobecky-generation.md` and `evidence/`.
