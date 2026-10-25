# Testing Seedforge

This folder is complete without the CCD tools. Use a sample seed and check the report against the lists below.

## Step 1. Quickstart

Paste this into the agent before the sample run. It is the same block as the top of `README.md`.

```
You are setting up Seedforge. Repo: https://github.com/alexdepasquale2-jpg/CompactContextDist-.ccd- . Do this setup, then stop and explain. Do not start a design or a build yet.

If you can read files and run commands: clone that URL when the working tree does not already contain agents/system-prompt.md. Load agents/system-prompt.md as your instructions. Read and keep both skills: agents/skills/regliobecky-generation/SKILL.md (Regliobecky Generation: seed to spec) and agents/skills/lincoln-creation/SKILL.md (Lincoln Creation: one batch to a kit). List every file in agents/seed/. That folder is the locked seed. Read all of it before any later phase. Images (png, jpg, webp) are look and sense references. Text (txt, md) is intent, lore, and constraints. Any other file is extra context: note the name and what you can observe, and do not ignore it. If agents/seed/ has no dropped files (only README.md and .gitkeep), say it is empty and ask for the seed.

If you cannot read the repo: say so. Ask the user to paste agents/system-prompt.md and both skill files, and to paste or attach every file that belongs in agents/seed/. Treat those attachments as the locked seed with the same image, text, and other rules. Do not invent a seed.

Then tell the user, in a few lines:
- Regliobecky when they have a seed and no spec. Lincoln when they have a spec and a batch card. If both, Regliobecky first, then stop at the handoff.
- Initialize a run as reports/<YYYY-MM-DD>-<slug>/ with 01-process.md, 02-notes.md, and 03-context.md. Append as you go.
- Regliobecky order: seedinitialization, then seedgermination, then seedexpansion, then sensesprocessing. Lincoln runs after that, one batch at a time.
- Reports are written in that reports folder. The handoff is handoff/<batch>.md with headings Packet, Question, and Next.
- A sample seed and the checklist are in agents/TESTING.md.
```

The agent should answer with how to invoke each mode, how to initialize a run, the phase order, and where reports go. It should not start designing yet.

If it cannot read files, it should ask you to paste `system-prompt.md`, both skills, and the seed. Paste those, then continue with step 2.

## Step 2. Sample seed

This drill is not a recovered world. Drop these into `seed/` (or attach them):

- `pier.txt`, containing exactly: `A fog bell on a pier at dusk. One figure, no crowd.`
- Optional: any png, jpg, or webp of a pier or a bell. If you have no image, skip it and expect the report to say no image was given.
- Optional: `notes.pdf` or any non-image, non-text file, so the "other" rule has something to record. Skip it if you have none.

Tell the agent: run Regliobecky on `seed/` and stop at the handoff. Do not build assets.

## Step 3. Regliobecky checklist

The report is `reports/<date>-fog-bell/` (the slug may differ; the three files must exist).

### seedinitialization

- Process lists every file that was in `seed/`, with type image, text, or other.
- Process quotes `pier.txt` in full and calls that folder the Seed.
- An image is described as a look and sense reference, not as a finished asset.
- A non-image, non-text file is named as extra context, with no invented meaning.
- Notes say what the agent refused to assume.
- Context starts with the same file list.
- The agent stopped when `seed/` was empty, if you tried that first. It did not invent a world.

### seedgermination

- Process has one line for what is visible in each image, or an explicit "no image" line.
- The phrase from `pier.txt` is quoted again, separate from inferences.
- Inferences are marked [INFERRED].
- The inventory is not collapsed to a count.

### seedexpansion

- Notes contain Look, Sound, Feel, Game system, and Opening scene, each filled, each tracing to the pier text or the image.
- A look lock in checkable words is present, and it cites the seed.
- `spec.md` uses the section numbers §1 through §11, including §9 build order, §10 asset list, and §11 delivery.
- Build order starts with one gray-box slice. Stretch is last.
- Asset rows have an id, a budget, a priority, and a seed reference.
- Batch cards exist, or the process says why a card was not cut.
- Anything not in the seed is marked [INFERRED] or left out.

### sensesprocessing

- Process repeats the visible inventory and quotes the text again.
- Look, Sound, Feel, and the look lock are restated in full.
- Material that does not trace to the image, the text, or those headings is cut or marked [INFERRED].
- `handoff/<batch>.md` exists with headings Packet, Question, and Next.
- Next names Lincoln and a build-order step, or says there is no batch yet.
- The agent did not build meshes, textures, or audio.

## Step 4. Lincoln checklist

Give the agent the spec, one batch card, and `common.md` from the Regliobecky run. Tell it to build only that batch and to stop on a spec conflict.

Expect `reports/<date>-<batch>/` to include:

- Process: commands, exit codes, and the verify result. A skipped tool is named.
- Notes: silhouette calls, hand edits refused, and any question for the designer.
- Context: the card, rows built, rows skipped, the seed path, output paths, and whether the kit is finished.
- One regenerate script. A hand edit that is not in the script is a failure.
- `verify.json`. `verify_kit.py` when the card has sockets, markers, or budgets.
- On a conflict, Question in the handoff holds the conflict and the look lock is unchanged.

## Pass

Every box above is either present in the report or explicitly skipped with a reason. A phase reduced to one status line fails seedinitialization's rule that the phase is verbose.
