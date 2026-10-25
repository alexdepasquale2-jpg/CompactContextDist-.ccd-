# little-alex build log

Branch `little-alex/sim`. Package `sim` only (`game3d/sim`). Stdlib, headless. Do not merge to main.

Guessed names (weapon consts, event consts, `Level.Pickups`, `Vec3` helpers) are declared in `sim/contract.go` and `sim/mathx.go`.

## M1 — movement

Fixed 1/60 step. Yaw 0 faces +Z. Move.Z is forward, Move.X positive is right. Diagonals are normalized. Committed as `sim: M1 movement + M2 collision/jump`.

## M2 — collision, gravity, jump

Per-axis swept AABB against level boxes, skin gap, gravity, jump only when grounded, ceiling bonk, no tunneling. `OnGround` is set for the renderer. Same commit as M1.

## M3 — combat

### Hitscan

`raySlab` against player and level boxes. Pistol `Fire` applies `PistolDamage` to the closest living other player and emits `EventHit`. A level box at equal or nearer t blocks the shot. Not in yet: ammo, swap, rockets, pickups, death, respawn, scoring.
