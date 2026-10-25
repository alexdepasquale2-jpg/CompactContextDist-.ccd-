## QUICKSTART

Paste this into any CLI or chat agent (Cursor, Claude Code, Codex, ChatGPT, Grok, or another). It sets the agent up, then tells you how to run.

```
You are setting up Seedforge. Repo: https://github.com/alexdepasquale2-jpg/CompactContextDist-.ccd- . Do this setup, then stop and explain. Do not start a design or a build yet.

If you can read files and run commands: clone that URL when the working tree does not already contain agents/system-prompt.md. Load agents/system-prompt.md as your instructions. Read and keep both skills: agents/skills/regliobecky-generation/SKILL.md (Regliobecky Generation: seed to spec) and agents/skills/lincoln-creation/SKILL.md (Lincoln Creation: one batch to a kit). List every file in agents/seed/ except README.md and .gitkeep. Those two are folder docs, never part of the seed. Every other file is the locked seed. Read all of them before any later phase. Images (png, jpg, webp) are look and sense references. Text (txt, md) is intent, lore, and constraints. Any other file is extra context: note the name and what you can observe, and do not ignore it. If agents/seed/ has no dropped files (only README.md and .gitkeep), say it is empty and ask for the seed.

If you cannot read the repo: say so. Ask the user to paste agents/system-prompt.md and both skill files, and to paste or attach every file that belongs in agents/seed/. Treat those attachments as the locked seed with the same image, text, and other rules. Do not invent a seed.

Then tell the user, in a few lines:
- Regliobecky when they have a seed and no spec. Lincoln when they have a spec and a batch card. If both, Regliobecky first, then stop at the handoff.
- Initialize a run as reports/<YYYY-MM-DD>-<slug>/ with 01-process.md, 02-notes.md, and 03-context.md. Append as you go. Run artifacts stay in that folder: spec.md, common.md, docs/asset-list.md, docs/prompts/, docs/batches/, and handoff/<batch>.md. The repo root stays clean.
- Regliobecky order: seedinitialization, then seedgermination, then seedexpansion, then sensesprocessing. Lincoln runs after that, one batch at a time. Step numbers are the ones in protocols/01 and protocols/02.
- The handoff is reports/<run>/handoff/<batch>.md with headings Packet, Question, and Next.
- A sample seed and the checklist are in agents/TESTING.md.
If ccd/ is present, check it with python3 -m ccd validate ccd/examples/seedforge.ccd and use it for handoffs; otherwise skip.
```

# CompactContextDist

Two trees in one repo.

`agents/` is Seedforge. It is the system prompt, both skills, the protocols, and the seed drop folder. Copy that directory out on its own. `agents/TESTING.md` is how you test it. Reports are markdown. Nothing in `agents/` imports or requires the format tools.

`ccd/` is the Compact Context Distributable format and its command-line tool. It may read `agents/` as example content (`ccd/examples/seedforge.ccd` is `agents/evidence` and `agents/protocols` packed). The cheap read is map, then find, then focus. From the repo root, `python3 -m ccd` needs no install. See `ccd/README.md`.

The link is one way. The format can use the agents as a sample. The agents do not import the format. A handoff may use it when the tool is present, and stays markdown when it is not.
