# Connect an agent

No install. The instructions are markdown in this folder.

## 1. Load the system prompt

The instructions are `system-prompt.md`.

One mode, instead of the whole bot:

- Regliobecky (seed to spec): `skills/regliobecky-generation/SKILL.md`
- Lincoln (one batch to a kit): `skills/lincoln-creation/SKILL.md`

## 2. Pick a mode

- A seed and no spec: Regliobecky.
- A spec and a batch card: Lincoln.
- Both: Regliobecky first. Stop at the handoff packet.
- If `handoff/<batch>.md` has a Next heading that names a mode, use that.

The seed is every file in `seed/`. seedinitialization reads that folder first. Blank forms are in `templates/`. Layouts are in `schematics/`. A sample run is `TESTING.md`.

## 3. Read the seed

List `seed/`. Images (png, jpg, webp) are look and sense references. Text (txt, md) is intent, lore, and constraints. Any other file is extra context. If the folder is empty, ask for the seed. Do not grow a world from nothing.

## 4. Write a report

Create `reports/<YYYY-MM-DD>-<slug>/` with `01-process.md`, `02-notes.md`, and `03-context.md`. Append as you go. Regliobecky's order is seedinitialization, seedgermination, seedexpansion, sensesprocessing. Lincoln runs after that, one batch at a time.

Leave the folder for the next agent. They read `03-context.md` first.

## Cursor

1. Put this folder on the agent.
2. Add `system-prompt.md` as a project rule, or tell the agent to follow `AGENTS.md`.
3. `@` a skill file when the task is one mode.

## Claude, ChatGPT, Codex, Grok, or any chat

1. Paste `system-prompt.md` into the instructions (or the system slot).
2. Paste `skills/regliobecky-generation/SKILL.md` or `skills/lincoln-creation/SKILL.md` when you want one mode.
3. Attach or paste every file from `seed/`. If you cannot attach files, paste the text files and describe each image.

## Generic CLI agent

Point it at this folder. The first instruction is `system-prompt.md`. The copy-paste block at the top of `README.md` is the same setup.
