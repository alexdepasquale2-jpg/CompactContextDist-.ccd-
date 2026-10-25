---
name: lincoln-creation
description: >-
  Use when a finished spec, asset list, and batch card must be built into
  original assets with local open-source tools, one regenerate script per kit,
  and verify checks. Do not use it to invent the world spec or change the look
  lock.
---

# Lincoln creation

You build one batch from a spec. You do not redesign the world. Tools are open-source and installed locally only. If the look lock and a row disagree, stop and send the question back. Do not pick a winner yourself.

Mark tool guesses [INFERRED]. Do not copy a reference's art or audio. A SOURCE row must be a license you can check, such as CC0.

## You need

The spec sections for look (§1–2), build order (§9), asset list (§10), and delivery (§11). The batch card. The named seed image. `common.md`, which you read first. The reference kit contact sheet, once one exists. If one of these is missing, stop and name it.

## Steps

1. Open `reports/<YYYY-MM-DD>-<batch>/` with `report.process`, `report.notes`, and `report.context`. Copy the card, the look lock, and the delivery tuple into context before you build.
2. Check every row id against §10: priority, budget, seed, sockets the build prompt names. Build P0 rows first. List shared props you must not rebuild. Reuse the scripts the card names.
3. Before you keep an export or render setting, add a tiny headless test under `<kit>/_tests` and run it. The recovered pattern is an FBX round-trip, and a headless render test, before the setting is trusted.
4. Write one regenerate script, `make_<kit>.sh` (or `make_<kit>.py` for audio). It rebuilds textures, meshes, export, previews, `verify.json`, and the README from a clean start, and it writes assets straight into the output directory. Log each group. Do not hand-edit the art. A hand edit that is not in the script is not in the kit.
5. Hit the budgets and the look lock from the spec. Under the recovered PS1 lock that is 300–900 triangles, 64–128 px, vertex-lit, no normal maps, chunky silhouettes matching the named seed. Do not quietly exceed a budget.
6. Export with the delivery tuple from §11. Recovered 3D default: FBX only, Y-up, 1 unit = 1 m, pivot at the feet, scale 1.0, forward Unity +Z (Blender −Y), `axis_forward='-Z'`, `axis_up='Y'`, `bake_space_transform=True`, `add_leaf_bones=False`, `mesh_smooth_type='FACE'`, `colors_type='SRGB'`. If nested children break, patch the exporter inside the script, restore the scene afterward, and prove it with the headless round-trip. Every prompted pivot is in the file.
7. Write `verify.json` (objects, parent path, triangle counts, engine-space pivots, sizes, textures) and `verify_kit.py` (markers, sockets, budgets, prompted pivots). A miss exits non-zero.
8. For a visual kit, write `previews/` with a contact sheet and a 320×240 layout shot of the prompt's arrangement. Write a README that states seed, rows, prompt, regenerate command, budgets, delivery line, verify command, reference kit, and shared props you did not rebuild.
9. Audio rows: numpy/scipy plus ffmpeg, or a source you verified is CC0. Voice is local text-to-speech only. Record duration, sample rate, channels, peak, and the source in `verify.json`.
10. The kit is finished only when the script regenerates it, budgets hold, verify exits 0, the README and the required previews exist, new settings have a passing headless test, the contact sheet matches the named seed's silhouette and palette, and shared props were reused.
11. On a spec conflict, stop. Put the question in the notes. Do not change the look lock or a prompt's sockets.

Toolchain to install in the workspace when you are on a fresh machine: a portable Blender, a uv Python 3.11 venv, numpy, scipy, ffmpeg. The recovered machine also had CPU torch installed; do not use it unless the spec asks for a local model. [INFERRED] Pillow is a reasonable PNG writer. The notes do not name one.

## Report

Process is commands and exit codes. Notes are the hard silhouette calls, hand edits you refused, inferences, and any question for the designer. Context is the card, the rows built, the rows skipped, the seed, the reference kit, the output paths, and whether the kit is finished.

```
python -m ccd pack reports/<run-id> -o reports/<run-id>.ccd --title "<batch> lincoln"
python -m ccd validate reports/<run-id>.ccd
```

Read incoming context with `python -m ccd outline <file>.ccd` and `python -m ccd expand <file>.ccd <id>`. The citation-heavy version of this skill is `protocols/lincoln-creation.md`.
