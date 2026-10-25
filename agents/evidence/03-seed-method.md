---
id: evidence.seed-method
parent: evidence
summary: Alex's seed method expands a seed, distills principles, and resynthesizes. answers: REA hard rules, no DRM
src: sources/rea-seed-method.md
see: protocols.regliobecky-generation
inferred: false
---

`sources/rea-seed-method.md` is Alex's REA skill. The seed-mode variant is the recovered method for growing a world from a seed:

1. Expand the seed: look, sound, feel, game system, opening scene.
2. List the mechanics and systems the world needs.
3. Pick legally analyzable reference targets for each. Each target is a scoped REA job.
4. Distill abstract principles (formulas, state machines, data layouts, pacing curves). Do not copy.
5. Re-synthesize those principles with the seed's own identity into original systems. Feed them back into the world spec. Hand implementation to coding agents.
6. Record which reference informed which system.

Hard rules from the same file: only analyze targets the user may analyze and that are in the job's scope; never target anti-cheat or try to bypass DRM or licensing; static analysis first; rebuild as original designs and code; never copy assets, code, names, or IP.

The art, UI, and sound variant in that skill tells an asset bot to distill how reference games store sprites, models, HUD layout, juice, and audio events, then generate original assets with local tools only. It forbids extracting the reference's actual art or audio. That is the recovered permission boundary for Lincoln's side of a reference pass. The REA server itself runs in a local Cursor client; these notes do not show Regliobecky or Lincoln calling it directly.

A related cloud agent, `bc-750a35a2-7551-5ab7-a48c-2ab59ecdb581` ("testseed procgen library", Godot 4.8), does not mention either name. It shows the seed-engineering pattern beside them: modules with a seeded RNG (reproducible from an int) and pure functions, validators for connectivity, reachability, slope, and spacing, a demo scene with a seed field and a regenerate button, and headless tests that the same seed gives the same output. [INFERRED] Folding that pattern into these two agents is a synthesis. The pattern itself is recovered from that agent.
