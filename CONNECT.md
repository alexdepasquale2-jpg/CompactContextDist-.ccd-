# Connect an agent

Python 3.11 or newer. From the repo root. Nothing is installed.

## 1. Load the system prompt

The instructions are `system-prompt.md`.

One mode, instead of the whole bot:

- Regliobecky (seed to spec): `skills/regliobecky-generation/SKILL.md`
- Lincoln (one batch to a kit): `skills/lincoln-creation/SKILL.md`

## 2. Pick a mode

- A seed and no spec: Regliobecky.
- A spec and a batch card: Lincoln.
- Both: Regliobecky first. Stop at the handoff packet.
- If `packet.next` names a mode, use that.

Blank forms are in `templates/`. Layouts are in `schematics/`.

## 3. Pull context

Read the index, then one id. Do not paste the whole file.

```bash
python3 -m ccd outline examples/seedforge.ccd -d 1
python3 -m ccd expand examples/seedforge.ccd protocols.handoff
```

`outline` and `expand` decode a version 2 file. You get plain text.

## 4. Push a report

```bash
python3 -m ccd pack reports/<run-id> -o reports/<run-id>.ccd --title "<run-id>"
python3 -m ccd validate reports/<run-id>.ccd
```

Leave that `.ccd` for the next agent. They outline it and expand `report.context`.

## Cursor

1. Put this repo on the agent.
2. Add `system-prompt.md` as a project rule, or tell the agent to follow `AGENTS.md`.
3. Use the pull and push commands above. `@` a skill file when the task is one mode.

## Claude or ChatGPT custom instructions

1. Paste `system-prompt.md` into custom instructions (or the system slot).
2. Paste `skills/regliobecky-generation/SKILL.md` or `skills/lincoln-creation/SKILL.md` when you want one mode.
3. If the chat can run commands, use the pull and push block.
4. If it cannot, paste the `outline` output, then paste one `expand` at a time. Do not paste `examples/seedforge.ccd` whole.

## Generic CLI agent

```bash
python3 -m ccd outline examples/seedforge.ccd -d 2
python3 -m ccd expand examples/seedforge.ccd <id>
python3 -m ccd pack reports/<run-id> -o reports/<run-id>.ccd --title "<run-id>"
python3 -m ccd validate reports/<run-id>.ccd
```

Send `system-prompt.md` as the first instruction. The format guide is `docs/USING-CCD.md`. The grammar is `SPEC.md`.
