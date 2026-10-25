---
id: evidence.dawn-whistle
parent: evidence
summary: Dawn Whistle is the recovered instance of spec, batches, seeds, and export.
src: sources/evidence.md | terminals/800941.txt
see: evidence.regliobecky evidence.lincoln
inferred: false
---

Dawn Whistle is the job these notes actually describe. It is one instance of the protocol, not a rule that every future seed is a PS1 arena game.

The spec file `dawn-whistle-spec.md` was read from terminal `800941.txt`:

- Section 9, build order, starts at the PSX render pipeline and one rig (Cinderstride) in a gray-box Scrapdune Yard, and ends at step 7: polish, then split screen as a stretch goal. The middle steps are not in the snippet.
- Section 10, asset list, marked "Lincoln, local tools only": low-poly models at 300–900 triangles (4 beasts, each with 3 detachable armor plate sets; 4 riders; 4 tools); arena kits (car bodies, a magnet crane, houses at 3 burn stages); textures at 64–128 px matching the seed screenshots; audio including radio barks by local text-to-speech only.

The spec has 11 sections. Prompts 1–22 are separate build prompts. Prompt 15 is the HUD and must match the seed screenshots. The project named in the brief is Dawn Whistle, Unity 6 URP, "Use Unity MCP". The titles of the 11 sections other than the look sections, §9, and §10 were not recovered.

The batch prompt pattern, shared by the four transcripts `bc-ce93cafa`, `bc-21289031`, `bc-cd4b2f50`, and `bc-c3ebd088`, is:

> Batch name: X. Read uploads/common.md first (shared brief: tools, style, export, delivery). Build rows <IDs> from docs/asset-list.md. Build prompt N (docs/promptN.txt) is the scene that will use the kit, so give it every child pivot and socket it mentions. Seed NN is the look reference. The attached Scrapdune contact sheet is a finished kit from the same pipeline: match its style and quality bar; reuse scripts/scrapdune/. Don't rebuild shared props. Output to assets/... with a README and previews/ (contact sheet + 320×240 layout shot).

Row ids that appear by name: TEX-04, TEX-08, VFX-04. P0 rows go first. [INFERRED] Wider prefixes such as CC, UI, and WPN, and the columns GENERATE / SOURCE / UNITY-SIDE, appear in the later draft prompt and not in these notes. P0 itself is recovered.

The first accepted kit in this job was Scrapdune. Later batches were told to match its contact sheet. [INFERRED] The general rule "the newest finished kit becomes the bar" is that practice, stated as a rule.
