**package sim — exported API** (stdlib only, headless). ★ = differs from / not in your BUILD3D stub
```go
// conventions ★: right-handed, Y up, meters; yaw 0 faces +Z; Move.Z forward, Move.X + = right; Pos = feet center
const Tick float32 = 1.0/60.0                       // ★
const MoveSpeed=6, Gravity=20, JumpSpeed=7, MaxFall=50 // ★ float32 tunables
const PlayerW=0.6, PlayerH=1.8; const MaxHealth=100 // ★ (box size was prose)
const EyeHeight=1.6, HitscanRange=200, PistolDamage=20 // ★ hitscan
type Vec3 struct{ X, Y, Z float32 }
func (Vec3) Add(Vec3) Vec3; Sub(Vec3) Vec3; Scale(float32) Vec3; Len() float32 // ★ mathx.go (yours may differ)
type WeaponKind int; const WeaponNone, WeaponPistol, WeaponRocket WeaponKind // ★ names guessed
type Input struct{ Move Vec3; Yaw, Pitch float32; Fire, Jump, Swap bool }
type Player struct{ ID int; Pos, Vel Vec3; Yaw, Pitch float32; Health int; Weapon WeaponKind
    Ammo, Kills, Deaths int; Alive bool; OnGround bool /*★*/ }
type Projectile struct{ Pos, Vel Vec3; Owner int; Kind WeaponKind }
type Pickup struct{ Pos Vec3; Kind WeaponKind; Active bool }
type Box struct{ Min, Max Vec3 }
type Level struct{ Boxes []Box; Spawns []Vec3; Pickups []Pickup /*★*/ }
type EventKind int; const EventHit, EventKill, EventPickup, EventRespawn EventKind
type Event struct{ Kind EventKind; Tick uint64; Player, Other, Amount int; Weapon WeaponKind; Pos Vec3 } // Other=-1 if none
type World struct{ KillLimit int /*★ default 10, 0=off*/ }
func NewWorld(level Level, seed int64) *World
func SampleLevel() Level                            // ★ 20x20 arena, crate, overhang
func (w *World) AddPlayer() int                     // spawn = Spawns[id % len]
func (w *World) Step(inputs map[int]Input)          // one Tick; missing id = zero Input
func (w *World) Players() []Player                  // copy, sorted by ID
func (w *World) Projectiles() []Projectile; Pickups() []Pickup; Level() Level
func (w *World) Events() []Event                    // last Step only, copy
func (w *World) Winner() (id int, done bool)        // unchanged
```

Hitscan (pistol): origin is feet + (0, EyeHeight, 0). Direction is yaw/pitch (yaw 0 = +Z, positive pitch = up). Slab test against every other living player box and every level box. Closest hit wins; a level box at the same t as a player blocks the shot. EventHit carries the victim, the shooter in Other, Amount = health actually removed, WeaponPistol, and the entry point. One pistol hit does not kill. Ammo, swap, rockets, pickups, death, and respawn are still open. Events() is cleared at the start of the next Step.
