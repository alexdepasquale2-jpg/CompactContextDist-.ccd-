---
name: REA reverse-engineering workflow
description: >-
  Use when a bot needs to understand how an existing app, game, binary, asset
  format or website works (via the REA MCP server + Ghidra) to inform design,
  worldbuilding, or asset pipelines, including seed-driven generative synthesis.
---
# REA reverse-engineering workflow

REA (npm `rea-agents`) is an MCP server with ~170 analysis tools: native binaries (via Ghidra), JS/Electron apps, .NET, APKs, websites, archives. Bots usually can't call it directly; it runs inside a local Cursor client on the user's machine. So bots delegate REA work to a local Cursor agent (`cursor-agent` CLI), which loads REA from `~/.cursor/mcp.json`.

## Hard rules
- Only analyze targets the user is allowed to analyze and that are in the active job's scope.
- Never target anti-cheat software (EasyAntiCheat, BattlEye, Vanguard/vgk, XIGNCODE, nProtect, Ricochet, PunkBuster, etc.) or try to bypass protections, DRM or licensing.
- Static analysis first; runtime capture only if the scope allows it.
- Rebuild mechanics as ORIGINAL designs and code. Never copy assets, code, names or IP.
- Respect the host's limits on local agent sessions and run heavy work at low priority.

## Steps
1. **Read the job.** Read the active job file from the REA dashboard workspace (e.g. `rea-workspace/jobs/ACTIVE.json`): target path or URL, goal, in- and out-of-scope notes, allowed actions, output folder. If there's no job, ask the coordinator or user to set one.
2. **Write a question checklist.** Turn the goal into 3-8 concrete questions (e.g. "how is the score multiplier computed?", "what fields does this model format store?").
3. **Delegate to a local Cursor agent.** Prompt it with the target, the checklist, the scope rules above and the output folder. Tell it to route the target per REA's own skill (`reverse-engineer-anything`): `open_binary` plus Ghidra for native code, `analyze_javascript_application` for JS/Electron, `inspect_managed_artifact` for .NET, `inspect_android_package` for APKs. It should work summary-first, cite Evidence IDs, separate observations from inferences and unknowns, save evidence JSON to the output folder, and call `close_binary` when done.
4. **Log progress.** Append each step to the dashboard activity log (e.g. `python dashboard/log_action.py <actor> <job-id> "<action>"`).
5. **Synthesize.** Read the findings and answer each checklist item as answered, partial or unresolved. Then produce the deliverable in your own domain: a design doc, an original system, a converter or a pipeline.

## Seed-mode variant (generative synthesis of worlds and games)
For a worldbuilding bot that works from seeds:
1. Expand the seed with the normal seed method: look, sound, feel, game system, opening scene.
2. From that expansion, list the mechanics and systems the world needs (e.g. a deck-building scoring loop, tower defense pathing, procedural terrain, a crafting economy).
3. For each one, pick real, legally analyzable reference targets that implement something similar (open-source games, demos, the user's own builds, web games), and make each a scoped REA job with steps 1-4 above.
4. Distill the findings into abstract principles (formulas, state machines, data layouts, pacing curves), not copies.
5. Re-synthesize: fuse those principles with the seed's own identity into original systems, then feed them back into the world spec and hand off implementation to coding agents.
6. Record which reference informed which system, so the lineage stays clear and nothing is copied.

## Art, UI and sound variant (asset and experience bot)
For an asset bot, REA covers anything to do with art, functionality, HUD, UI/UX and sound in reference apps and games:
1. **Art:** how sprites, atlases, models, shaders, palettes, animation rigs and VFX are stored and loaded (formats, layouts, resolutions, naming, LOD).
2. **Functionality:** how features behave in the UI layer: input handling, state flows, feedback timing, juice (tweens, easing, screen shake), how each feature is wired up.
3. **HUD and UI/UX:** layout systems, anchoring and scaling across screen sizes, menu flows, iconography, typography, readability, accessibility, mobile touch targets. For web and Electron apps, trace the UI components and CSS. For native apps, inspect resources and UI code.
4. **Sound:** audio formats, banks and middleware layout, how SFX and music are triggered (events, layering, ducking, randomization, loops), mixing levels.
Distill each into specs and principles (style guides, timing tables, layout rules, audio event maps), then generate ORIGINAL assets with local tools only and build better local generation, conversion and optimization pipelines. Never extract or reuse the reference's actual art or audio.
