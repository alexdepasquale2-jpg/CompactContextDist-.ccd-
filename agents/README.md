## QUICKSTART

Paste this into any CLI or chat agent (Cursor, Claude Code, Codex, ChatGPT, Grok, or another). It sets the agent up, then tells you how to run.

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

# Seedforge

CompactContextDist (`.ccd`). Seedforge is the two modes: Regliobecky writes a spec from a seed, Lincoln builds one batch into a kit.

This folder stands alone. Copy it out of the repo and follow `TESTING.md`. Reports are plain markdown. If you have the CCD tools, a report folder can be packed with them.

## Layout

```
system-prompt.md         both modes
CONNECT.md               how to attach an agent
AGENTS.md                short index
TESTING.md               sample seed and checklist
seed/                    drop the input seed here
protocols/               long form, including the four phases
skills/                  one file per mode
evidence/                recovered facts
sources/                 notes the evidence cites
templates/               blank seed brief, spec, prompt, report
schematics/              layouts
```

A run writes `reports/<YYYY-MM-DD>-<slug>/` (process, notes, context) and, at handoff, `handoff/<batch>.md`.

## License

No license has been chosen. This note is a placeholder, not a grant of rights. Pick a license before distributing the project.
