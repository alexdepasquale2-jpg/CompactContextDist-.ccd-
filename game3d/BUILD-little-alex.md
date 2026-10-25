# little-alex build log

Branch `little-alex/sim`. Package `sim` only (`game3d/sim`). Stdlib, headless. Do not merge to main.

Guessed names (weapon consts, event consts, `Level.Pickups`, `Vec3` helpers) are declared in `sim/contract.go` and `sim/mathx.go`.

## M1 — movement

Fixed 1/60 step. Yaw 0 faces +Z. Move.Z is forward, Move.X positive is right. Diagonals are normalized. Committed as `sim: M1 movement + M2 collision/jump`.

## M2 — collision, gravity, jump

Per-axis swept AABB against level boxes, skin gap, gravity, jump only when grounded, ceiling bonk, no tunneling. `OnGround` is set for the renderer. Same commit as M1.

## M3 — combat

### Hitscan — stopped here

This branch stops after hitscan. Finish the rest of M3 in the other repo. Do not start a later milestone here.

Done in this tree:

- `raySlab` against player boxes and level boxes.
- Pistol `Fire` applies `PistolDamage` (20) to the closest other living player and emits `EventHit` (victim, shooter in `Other`, health removed, entry point).
- A level box at an equal or nearer t blocks the shot.
- `Events()` is only the last `Step`.
- `Winner()` signature is unchanged. It already returns the lowest id at `KillLimit`, but nothing awards kills yet.

Still open in M3:

- Ammo and `Swap`. Pistol fire does not spend ammo or cool down.
- Rockets: swept projectile box and splash.
- Pickups: respawn timers and the `Active` flag. `stepPickups` is still empty.
- Death when health reaches 0, kill and death scoring, respawn at `Spawns` after a short delay.
- `EventKill`, `EventPickup`, and `EventRespawn`. Only `EventHit` is emitted.
- No RNG is drawn. `NewWorld`'s seed is stored for later use.
