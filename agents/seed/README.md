# Seed

Drop the input seed in this folder before a run. Any file is accepted. Most seeds are photos (`png`, `jpg`, `webp`) and text (`txt`, `md`).

`seedinitialization` reads every file here first and treats the set as the locked seed. It does not skip a file because the type is unfamiliar.

| Kind | Usual extensions | How the phase treats the file |
| --- | --- | --- |
| Image | png, jpg, webp | Look and sense reference. Inventory what is visible. Do not imagine the rest. |
| Text | txt, md | Intent, lore, and constraints. Quote it. |
| Anything else | any | Extra context. Record the filename and what you can observe. Do not ignore it, and do not invent a meaning. |

`jpg` includes a `.jpeg` file: same image rule. An empty folder is not a seed. Stop and ask for one.

This folder is empty in git except this note. Files you drop here are ignored by git so a private seed is not committed.
