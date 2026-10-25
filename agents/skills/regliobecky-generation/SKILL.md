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

## Steps

Same numbers as `protocols/01-regliobecky-generation.md`. Do not renumber.

Run artifacts live in `reports/<YYYY-MM-DD>-<slug>/`: `spec.md`, `common.md`, `docs/asset-list.md`, `docs/prompts/`, `docs/batches/`, `handoff/`, `01-process.md`, `02-notes.md`, `03-context.md`. The repo root stays clean.

`README.md` and `.gitkeep` in `agents/seed/` are folder docs, never part of the seed.

### seedinitialization

0. Read every file in `agents/seed/` except `README.md` and `.gitkeep`. Images (png, jpg, jpeg, webp) are look and sense references. Text (txt, md) is intent, lore, and constraints; quote it. Any other file is extra context. If nothing remains, stop. Open the run folder. If the seed filename is generic (`image`, `img_1234`, `photo`, `untitled`, `screenshot`, `IMG_*`, or numbers only), the slug comes from visible text or a short description of the main subject, recorded as [INFERRED] in `02-notes.md`. Append to `01-process.md` as you go.
1. Ask for the target engine and the dimension (2D, 3D, or other) when no text seed states them. If there is no answer, default to Godot 4 and `.glb` and mark that [INFERRED] in `02-notes.md`.

### seedgermination

2. Inventory the seed. Number images `seeds/01` onward by sorted filename. Those are labels. No `seeds/` folder is created. One line each for what is visible. Separate visible facts from inferences.

### seedexpansion

3. Write Look, Sound, Feel, Game system, Opening scene. With no audio, derive Sound from visual cues and mark the whole heading [INFERRED]. With no text, do the same for Feel. A text-only seed derives both from the quoted text and marks each whole heading [INFERRED]. List each derived heading as an open question in the handoff.
4. Lock the look in checkable constraints. Derive every budget from the seed and justify it. The PS1 lock (vertex-lit, no normal maps, chunky silhouettes, 300–900 tris, 64–128 px) is one example profile, not the default. Use it only when the seed is that kind of 3D, and say so.
5. List the systems the five headings require. For each: name, source heading, what the player does.
6. Study references only when asked, and only as principles, with a lineage row. Otherwise write "no reference pass". No anti-cheat, no DRM bypass, no copied art.
7. Write `spec.md` in the run folder: §1 Look, §2 Look lock, §3 Sound, §4 Feel, §5 Game system, §6 Opening scene, §7 Systems and lineage, §8 UI, §9 Build order, §10 Asset list, §11 Delivery and batches.
8. §9 starts with one vertical slice, then systems, then remaining content, then polish, stretch last. Each step names asset ids and a prompt number.
9. §10 is `docs/asset-list.md`. One row per asset: id, name, batch, priority (P0 first), a justified budget, origin, seed label, sockets, notes.
10. Write `docs/prompts/promptN.txt`. The header names the engine from step 1. Each prompt names every asset id and child pivot it uses.
11. Write the delivery spec in §11 and at the top of `common.md`. Date it and state that it overrides older briefs. If step 1 defaulted, this is Godot 4 and `.glb`, marked [INFERRED]. The recovered FBX / Unity tuple is the example for a Unity engine, not the default.
12. Cut `docs/batches/<name>.md`. Each card has name, row ids (P0 first), prompt N and its pivots, seed label, reference kit or "seed only", scripts to reuse, shared props not to rebuild, output directory, and the required README plus contact sheet and 320×240 layout shot.

### sensesprocessing

13. Restate the visible inventory, the text or its absence, and Look, Sound, Feel, and the look lock in full. Cut material that does not trace to the image, the text, or those headings, or mark it [INFERRED].
14. Check §9 against the batch cards. Every asset a build-order step requires is in the same batch or an earlier one. Fix the order, or log the conflict under Question.
15. Write `handoff/<batch>.md` in the run folder with headings Packet, Question, and Next, and stop. Do not build the assets.

## Report

Each phase is transparent and verbose in `01-process.md`, `02-notes.md`, and `03-context.md`. When packed, those files are the CCD nodes `report.process`, `report.notes`, and `report.context`. [INFERRED] A phase reduced to a status line does not meet the original intent.

The long form is `protocols/01-regliobecky-generation.md`. Facts are in `evidence/`.

## Optional: CCD

Markdown is the source of truth. If `python3 -m ccd` is missing, skip this and do not mention it.

Pack only after step 15's final append. `run.ccd` is the very last file. You may pack `spec.md` to `spec.ccd` immediately before that. The next mode, when those files exist, runs `ccd map`, `ccd find`, and `ccd focus` on `report.context` and `ccd focus spec.ccd spec --section` for each heading the context names. Otherwise it reads `03-context.md` and `handoff/<batch>.md` in the run folder.
