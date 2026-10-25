---
id: evidence.lincoln
parent: evidence
summary: Lincoln built kits with local tools, one regenerate script, and verify checks.
src: sources/evidence.md | terminals/652231.txt | terminals/766498.txt
see: evidence.dawn-whistle protocols.lincoln-creation
inferred: false
---

Lincoln is the asset builder. The workspace `/workspace/lincoln` is deleted. Terminal `800941.txt` (4 Oct 2026) still lists what was in it: `README.md`, `bin`, portable Blender 5.2.2, `dawn-whistle`, `img`, `python`, `sfx`, `smoke`, and a venv. Terminal `652231.txt` (3 Oct 2026) records the toolchain it built there: a uv Python 3.11 venv and CPU torch, torchvision, and torchaudio.

No recovered kit script in these notes imports torch. [INFERRED] Torch was installed and available. Do not describe it as part of the Dawn Whistle asset path.

What the notes do show Lincoln running:

- `./make_scrapdune.sh` as an end-to-end script. It builds textures (the log names TEX-04 tiling, TEX-08 sky, VFX-04 flipbook), writes PNGs straight into `/workspace/seeds-beast-arena/assets/arenas/ScrapduneYard/...`, then builds mesh groups with `build_group.py`. The group log is `logs/1000_build.log`. Terminals `766498.txt` and `766499.txt`.
- `arenas/frostbite/verify_kit.py` checks marker colours and sockets. Terminal `766500.txt`.
- Small headless Blender tests in `beasts/_tests` before a setting was kept: "Test FBX export settings round-trip" (`737665.txt`) and "Test bf2 on double layers and Eevee headless" (`766501.txt`).
- `beasts/beastlib.py` exports FBX and carries two exporter patches for nested children.
- `weapons/make_weapons.sh` for the weapon kit.
- `sfx/*/make_sfx.py` synthesizes audio with numpy and scipy, then ffmpeg. Freesound alternatives were verified CC0. Voices in the asset list are local text-to-speech only.

Each kit writes `verify.json` with re-import data: objects, parent path, triangle counts, Unity-space pivots, sizes, and textures. Batch output includes a README and `previews/` (a contact sheet and a 320×240 layout shot). The batch prompt says to read `uploads/common.md` first, build the listed row ids, do P0 rows first, supply every child pivot and socket the matching build prompt names, match the named seed and the reference kit, reuse `scripts/scrapdune/`, and not rebuild shared props. Tools are open-source and installed locally only.

The PNG library is not named. [INFERRED] Pillow is the likely writer. ImageMagick is named only in the later draft prompt, not in the terminal notes. Point-sampled filtering is also only in that draft. A "~1 min" regenerate budget is only in that draft; no duration was measured in the notes.
