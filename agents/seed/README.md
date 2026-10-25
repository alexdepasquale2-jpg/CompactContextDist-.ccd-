# Seed

Drop the input seed in this folder before a run. Any file is accepted. Most seeds are photos (`png`, `jpg`, `webp`) and text (`txt`, `md`).

`README.md` and `.gitkeep` are folder docs. They are never part of the seed. Every protocol that reads `agents/seed/` skips those two names. Do not put intent, lore, or a brief in this README.

`seedinitialization` reads every other file here first and treats that set as the locked seed. It does not skip a file because the type is unfamiliar.

| Kind | Usual extensions | How the phase treats the file |
| --- | --- | --- |
| Image | png, jpg, jpeg, webp | Look and sense reference. Inventory what is visible. Do not imagine the rest. |
| Text | txt, md | Intent, lore, and constraints. Quote it. |
| Anything else | any | Extra context. Record the filename and what you can observe. Do not ignore it, and do not invent a meaning. |

`jpg` includes a `.jpeg` file: same image rule. A folder that contains only this README and `.gitkeep` is not a seed. Stop and ask for one.

Images are labeled `seeds/01`, `seeds/02`, and so on, by sorted filename. Those are labels. No `seeds/` folder is created.

A generic filename does not become the run slug. Generic names are `image`, `img_1234`, `photo`, `untitled`, `screenshot`, `IMG_*`, and a name that is only numbers. The slug then comes from visible text or a short description of the main subject, and `02-notes.md` records that choice as [INFERRED].

This folder is empty in git except this note and `.gitkeep`. Files you drop here are ignored by git so a private seed is not committed.
