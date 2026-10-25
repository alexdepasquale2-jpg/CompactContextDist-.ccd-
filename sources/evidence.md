# Evidence: Regliobecky & Lincolnlogious (recovered 2026-10-25)

## Regliobecky (very thin)
- /home/box/.cursor/projects/workspace/terminals/740134.txt (Bot World collector docstring, Oct 17):
  "Sources: agent profiles + file heartbeats, dashboard cards (+ bundle + PC mirrors), Regliobecky's
  cursor-agent output mirrored on the box, agent transcripts ..."
  -> Regliobecky ran as a cursor-agent CLI agent (likely on Alex's PC), output mirrored to the box.
- 740137.txt lists Regliobecky as a Bot World bot (with OptimizePrime, OpenWorldeous). No instructions survive.
- /workspace/openworld (the mirror) is deleted. No hits on Alex's PC (~/.cursor, %APPDATA%\Cursor\User, Desktop; files <50MB).

## "Lincoln" (almost certainly Lincolnlogious) — asset builder, local tools only
- Workspace was /workspace/lincoln (now deleted): README.md, bin, blender (5.2.2 portable), dawn-whistle, img, python, sfx, smoke, venv (terminal 800941.txt, Oct 4).
- 652231.txt (Oct 3): built its own toolchain in /workspace/lincoln: uv Python 3.11 venv + CPU torch/torchvision/torchaudio.
- 800941.txt: /workspace/seeds-beast-arena/dawn-whistle-spec.md
  "## 10. Asset list (Lincoln, local tools only)
   - Low-poly models (300–900 triangles each): 4 beasts, each with 3 armor plate sets that can detach; 4 riders; 4 tools.
   - Arena kits: car bodies, a magnet crane, ... houses at 3 burn stages ...
   - Textures: 64–128 px, matching the seed screenshots.
   - Audio: ... radio barks (local text-to-speech only)."
  "## 9. Build order: 1. The PSX render pipeline, one rig (Cinderstride) in a gray-box Scrapdune Yard ... 7. Polish, then split screen (stretch)."
- 766498/766499.txt: `./make_scrapdune.sh` end-to-end script: "== textures (TEX-04 tiling, TEX-08 sky, VFX-04 flipbook)", writes PNGs straight into
  /workspace/seeds-beast-arena/assets/arenas/ScrapduneYard/..., then builds mesh groups via build_group.py (logs/1000_build.log).
- 766500.txt: arenas/frostbite/verify_kit.py checks marker colours / sockets (validation step per kit).
- 737665.txt "Test FBX export settings round-trip"; 766501.txt "Test bf2 on double layers and Eevee headless" -> small headless Blender tests in beasts/_tests before committing to a setting.

## The "seed method" (Alex's own skill)
- /home/box/agent-data/workflows/rea-reverse-engineering-workflow/SKILL.md lines 26-33, "Seed-mode variant":
  1. Expand the seed with the normal seed method: look, sound, feel, game system, opening scene.
  2. List the mechanics and systems the world needs.
  3. Pick legally analyzable reference targets for each; scoped REA job.
  4. Distill into abstract principles (formulas, state machines, data layouts, pacing curves), not copies.
  5. Re-synthesize with the seed's own identity into original systems; feed back into the world spec; hand implementation to coding agents.
  6. Record which reference informed which system.
- Hard rules (same file): rebuild as ORIGINAL designs; never copy assets, code, names or IP.

## Related cloud agent
- bc-750a35a2-7551-5ab7-a48c-2ab59ecdb581 "testseed procgen library (Godot 4.8)": no mention of either name; shows the seed engineering pattern:
  "Modules, each a class with seeded RNG (reproducible from an int seed) and pure functions", validators (connectivity, reachability, slope, spacing),
  demo scene "with a seed field and a regenerate button", headless tests "covering determinism by seed".

## Searched with no hits
Box (/workspace, /home/box, /cursor/stores, /tmp), Alex's PC (.cursor, AppData Cursor User, Desktop). Drive/GitHub were not re-searched here (parent reported none earlier).

## Update (follow-up): Dawn Whistle cloud agent transcripts
- bc-ce93cafa-fa53-5c05-85a7-dc32b3c746a3 (HUD+UI), inside the shared asset brief (also seen in the other three):
  "Sources read: dawn-whistle-spec.md (all 11 sections, including the Prompt 1–22 build prompts) and seeds 01–04.
   **Designer direction (Regliobecky, 2026-10-04):** align with spec §10 (asset list) and §1–2 (look). PS1-faithful: vertex-lit, **no normal maps**, chunky silhouettes that match the seeds."
  Same brief, "0.1 Delivery format (designer spec, overrides the earlier brief)": FBX only, Y-up, 1 unit = 1 m, pivot at feet, scale 1.0, forward = Unity +Z (model facing Blender −Y), export axis_forward='-Z', axis_up='Y', bake_space_transform=True, add_leaf_bones=False, mesh_smooth_type='FACE', colors_type='SRGB'.
  -> Regliobecky was the DESIGNER/spec owner; Lincoln built assets from the spec.
- "Seeds" = numbered seed screenshots 01–04 (seeds/ folder) used as the look reference; e.g. "The attached seed 03 is the look reference" (Cinder Court, bc-21289031), "seed 04" (Pier 9, bc-cd4b2f50), the seed HUD drawn by scripts/hud_post_reference.py (UI).
- Batch prompt pattern (all four): "Batch name: X. Read uploads/common.md first (shared brief: tools, style, export, delivery). Build rows <IDs> from docs/asset-list.md ... Build prompt N (docs/promptN.txt) is the scene that will use the kit, so give it every child pivot and socket it mentions. Seed NN is the look reference. The attached Scrapdune contact sheet is a finished kit from the same pipeline: match its style and quality bar; reuse scripts/scrapdune/. Don't rebuild shared props. Output to assets/... with a README and previews/ (contact sheet + 320×240 layout shot)." Also "Tools: open-source and installed locally only." and P0 rows first.
- Lincoln artifacts referenced: /workspace/lincoln/dawn-whistle/{arenas/scrapdune/make_scrapdune.sh, beasts/beastlib.py export_fbx with two FBX exporter patches for nested children, weapons/make_weapons.sh}, /workspace/lincoln/sfx/*/make_sfx.py (numpy/scipy synthesis + ffmpeg; Freesound alts verified CC0). Each kit writes verify.json re-import data (objects, parent path, tris, Unity-space pivots, sizes, textures).
- Spec includes 22 numbered Unity build prompts (e.g. "Prompt 15: HUD (match the seed screenshots)", project DawnWhistle Unity 6 URP, "Use Unity MCP").
- No "universe" wording found. No "lincolnlogious" spelling found (only "Lincoln").

## PC state.vscdb
- %APPDATA%\Cursor\User\globalStorage\state.vscdb = 713,830,400 bytes (~681 MB), over CopyToBox's 100 MiB limit; not queried.
