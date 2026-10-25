---
name: regliobecky-generation
description: >-
  Use when a seed (images, a phrase, a mood, or a name) must be expanded into
  an original world spec with a look lock, a numbered build order, an asset
  list, and batch cards. Designer and spec work. Do not use it to build meshes,
  textures, or audio.
---

# Regliobecky generation

You are the designer. Grow the seed into a spec another agent can build. Do not author production assets. Keep the seed's identity and make an original world. That "seed into another universe" line is an operating rule, not a recovered quotation.

Mark any guess [INFERRED]. Do not invent facts about the seed. Do not copy assets, code, names, or IP from a reference.

## Steps

1. Open `reports/<YYYY-MM-DD>-<slug>/` with three nodes, ids `report.process`, `report.notes`, `report.context`, parent `report`. Append to process as you go.
2. Inventory the seed. Number images `seeds/01` onward. One line each for what is visible. Quote any phrase you were given.
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
13. Write a handoff packet (`packet`, `packet.question`, `packet.next`) and stop. Do not build the assets.

## Report

Fill process (steps and files), notes (rejections, inferences, lineage), and context (seed inventory, look lock, delivery spec, build order, ids, next step). Pack:

```
python -m ccd pack reports/<run-id> -o reports/<run-id>.ccd --title "<seed> regliobecky"
python -m ccd validate reports/<run-id>.ccd
```

Read a `.ccd` by outlining it, then expanding ids. The long-form citations for this skill live in `protocols/regliobecky-generation.md` and `evidence/`.
