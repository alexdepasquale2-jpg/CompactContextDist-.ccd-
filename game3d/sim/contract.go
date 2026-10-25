// Package sim is the deterministic headless simulation for the arena game
// (Conker's Bad Fur Day multiplayer style). Right-handed, Y up, meters.
// Owner: alexs-agent (Little Alex). Renderer: kens-agent (Arnold).
package sim

// Tick is the fixed timestep of one Step call (1/60 s).
const Tick float32 = 1.0 / 60.0

// Tunables.
const (
	MoveSpeed float32 = 6.0  // m/s horizontal
	Gravity   float32 = 20.0 // m/s^2 downward
	JumpSpeed float32 = 7.0  // m/s initial upward velocity
	MaxFall   float32 = 50.0 // terminal fall speed
	PlayerW   float32 = 0.6
	PlayerH   float32 = 1.8
	MaxHealth         = 100
	skin      float32 = 1e-4 // gap kept between player and walls
)

type Vec3 struct{ X, Y, Z float32 }

type WeaponKind int

const (
	WeaponNone   WeaponKind = iota
	WeaponPistol            // hitscan (TODO M3)
	WeaponRocket            // slow projectile (TODO M3)
)

// Input is one player's controls for one tick.
type Input struct {
	Move             Vec3 // x strafe (+ = right), z forward, -1..1; y ignored
	Yaw, Pitch       float32
	Fire, Jump, Swap bool
}

type Player struct {
	ID                  int
	Pos, Vel            Vec3 // Pos = center of the feet (bottom face of the box)
	Yaw, Pitch          float32
	Health              int
	Weapon              WeaponKind
	Ammo, Kills, Deaths int
	Alive               bool
	OnGround            bool // extra field (read-only for renderer)
}

type Projectile struct {
	Pos, Vel Vec3
	Owner    int
	Kind     WeaponKind
}

type Pickup struct {
	Pos    Vec3
	Kind   WeaponKind
	Active bool
}

// Box is a static level AABB.
type Box struct{ Min, Max Vec3 }

func (b Box) axisMin(i int) float32 { return b.Min.axis(i) }
func (b Box) axisMax(i int) float32 { return b.Max.axis(i) }

// Level is boxes + spawn points (+ pickup spots).
type Level struct {
	Boxes   []Box
	Spawns  []Vec3
	Pickups []Pickup
}

type EventKind int

const (
	EventHit EventKind = iota
	EventKill
	EventPickup
	EventRespawn
)

// Event is emitted during Step; Events() returns those from the last Step.
type Event struct {
	Kind   EventKind
	Tick   uint64
	Player int // subject (victim / picker / respawned)
	Other  int // attacker for Hit/Kill, -1 otherwise
	Amount int // damage for Hit
	Weapon WeaponKind
	Pos    Vec3
}
