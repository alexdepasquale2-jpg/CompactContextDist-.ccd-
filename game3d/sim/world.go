package sim

import (
	"math"
	"sort"
)

// World holds all simulation state. Not safe for concurrent use.
type World struct {
	level   Level
	seed    int64
	tick    uint64
	players []Player // sorted by ID; iteration order is deterministic
	nextID  int
	projs   []Projectile
	pickups []Pickup
	events  []Event
	// KillLimit for Winner(); 0 disables.
	KillLimit int
}

func NewWorld(level Level, seed int64) *World {
	w := &World{level: level, seed: seed, KillLimit: 10}
	w.pickups = append([]Pickup(nil), level.Pickups...)
	return w
}

// AddPlayer spawns a player at spawn point (id mod len(spawns)) and returns its ID.
func (w *World) AddPlayer() int {
	id := w.nextID
	w.nextID++
	p := Player{ID: id, Health: MaxHealth, Alive: true, Weapon: WeaponPistol}
	if n := len(w.level.Spawns); n > 0 {
		p.Pos = w.level.Spawns[id%n]
	}
	w.players = append(w.players, p)
	return id
}

// Step advances exactly one Tick. Players without an entry get a zero Input.
func (w *World) Step(inputs map[int]Input) {
	w.tick++
	w.events = w.events[:0]
	for i := range w.players {
		p := &w.players[i]
		if !p.Alive {
			continue // TODO(M3): respawn timer -> EventRespawn
		}
		in := inputs[p.ID]
		w.stepPlayer(p, in)
		w.stepWeapon(p, in)
	}
	w.stepProjectiles()
	w.stepPickups()
}

func (w *World) stepPlayer(p *Player, in Input) {
	p.Yaw, p.Pitch = in.Yaw, in.Pitch
	// Horizontal: normalize so diagonals are not faster; analog <1 kept.
	mx, mz := in.Move.X, in.Move.Z
	if l := float32(math.Sqrt(float64(mx*mx + mz*mz))); l > 1 {
		mx, mz = mx/l, mz/l
	}
	s, c := float32(math.Sin(float64(p.Yaw))), float32(math.Cos(float64(p.Yaw)))
	// yaw 0 faces +Z; right = forward x up = (-cos, 0, sin).
	fwd := Vec3{s, 0, c}
	right := Vec3{-c, 0, s}
	h := fwd.Scale(mz).Add(right.Scale(mx)).Scale(MoveSpeed)
	p.Vel.X, p.Vel.Z = h.X, h.Z

	if in.Jump && p.OnGround {
		p.Vel.Y = JumpSpeed
		p.OnGround = false
	}
	p.Vel.Y -= Gravity * Tick
	if p.Vel.Y < -MaxFall {
		p.Vel.Y = -MaxFall
	}
	d := p.Vel.Scale(Tick)
	// Per-axis swept move: X, then Y, then Z.
	p.OnGround = false
	for _, a := range [3]int{0, 1, 2} {
		want := d.axis(a)
		got := w.sweepAxis(p.Pos, a, want)
		np := p.Pos
		np.setAxis(a, np.axis(a)+got)
		p.Pos = np
		if got != want {
			if a == 1 && want < 0 {
				p.OnGround = true
			}
			v := p.Vel
			v.setAxis(a, 0) // ceiling bonk / wall stop
			p.Vel = v
		}
	}
	// Grounded check when standing still on a surface (resting contact).
	if !p.OnGround && p.Vel.Y <= 0 && w.sweepAxis(p.Pos, 1, -2*skin) > -2*skin {
		p.OnGround = true
	}
}

func playerBox(pos Vec3) Box {
	hw := PlayerW / 2
	return Box{Vec3{pos.X - hw, pos.Y, pos.Z - hw}, Vec3{pos.X + hw, pos.Y + PlayerH, pos.Z + hw}}
}

// sweepAxis returns how far the player at pos can move along axis a (signed),
// clipped against every level box that overlaps on the other two axes. This is
// an exact swept test, so no tunneling regardless of speed.
func (w *World) sweepAxis(pos Vec3, a int, delta float32) float32 {
	if delta == 0 {
		return 0
	}
	pb := playerBox(pos)
	for _, b := range w.level.Boxes {
		overlap := true
		for o := 0; o < 3; o++ {
			if o == a {
				continue
			}
			if pb.axisMax(o) <= b.axisMin(o) || pb.axisMin(o) >= b.axisMax(o) {
				overlap = false
				break
			}
		}
		if !overlap {
			continue
		}
		if delta > 0 && b.axisMin(a) >= pb.axisMax(a)-skin {
			if lim := b.axisMin(a) - pb.axisMax(a) - skin; lim < delta {
				delta = max32(lim, 0)
			}
		} else if delta < 0 && b.axisMax(a) <= pb.axisMin(a)+skin {
			if lim := b.axisMax(a) - pb.axisMin(a) + skin; lim > delta {
				delta = min32(lim, 0)
			}
		}
	}
	return delta
}

func max32(a, b float32) float32 {
	if a > b {
		return a
	}
	return b
}
func min32(a, b float32) float32 {
	if a < b {
		return a
	}
	return b
}

// TODO(M3): move projectiles with swept box vs level/players; hitscan weapons use ray tests on Fire.
func (w *World) stepProjectiles() {}

// TODO(M3): overlap pickups -> give weapon/ammo, EventPickup, respawn timer.
func (w *World) stepPickups() {}

func (w *World) Players() []Player {
	out := append([]Player(nil), w.players...)
	sort.Slice(out, func(i, j int) bool { return out[i].ID < out[j].ID })
	return out
}
func (w *World) Projectiles() []Projectile { return append([]Projectile(nil), w.projs...) }
func (w *World) Pickups() []Pickup         { return append([]Pickup(nil), w.pickups...) }
func (w *World) Level() Level              { return w.level }

// Events returns events emitted by the most recent Step (copy).
func (w *World) Events() []Event { return append([]Event(nil), w.events...) }

// Winner returns the first player (lowest ID on ties) reaching KillLimit.
// TODO(M3): kills are not scored until weapons land, so this is false for now.
func (w *World) Winner() (id int, done bool) {
	if w.KillLimit <= 0 {
		return -1, false
	}
	for _, p := range w.players {
		if p.Kills >= w.KillLimit {
			return p.ID, true
		}
	}
	return -1, false
}
