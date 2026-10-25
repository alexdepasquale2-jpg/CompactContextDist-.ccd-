package sim

import (
	"math"
	"testing"
)

func spawnWorld(spawns []Vec3, walls []Box) *World {
	lv := floorOnly()
	lv.Spawns = append([]Vec3(nil), spawns...)
	lv.Boxes = append(lv.Boxes, walls...)
	w := NewWorld(lv, 1)
	for range spawns {
		w.AddPlayer()
	}
	return w
}

func eventsOf(w *World, k EventKind) []Event {
	var out []Event
	for _, e := range w.Events() {
		if e.Kind == k {
			out = append(out, e)
		}
	}
	return out
}

func TestRaySlab(t *testing.T) {
	box := Box{Min: Vec3{0, 0, 0}, Max: Vec3{1, 1, 1}}
	diag := float32(math.Sqrt(3))
	dir := Vec3{1, 1, 1}
	dir = dir.Scale(1 / dir.Len())
	cases := []struct {
		name      string
		origin, d Vec3
		maxT      float32
		hit       bool
		wantT     float32
	}{
		{"front face", Vec3{0.5, 0.5, -1}, Vec3{0, 0, 1}, 100, true, 1},
		{"from behind ray", Vec3{0.5, 0.5, 3}, Vec3{0, 0, -1}, 100, true, 2},
		{"side miss", Vec3{2, 0.5, -1}, Vec3{0, 0, 1}, 100, false, 0},
		{"ray leaving", Vec3{0.5, 0.5, 2}, Vec3{0, 0, 1}, 100, false, 0},
		{"origin inside", Vec3{0.5, 0.5, 0.5}, Vec3{0, 0, 1}, 100, true, 0},
		{"short of box", Vec3{0.5, 0.5, -1}, Vec3{0, 0, 1}, 0.5, false, 0},
		{"exact maxT", Vec3{0.5, 0.5, -1}, Vec3{0, 0, 1}, 1, true, 1},
		{"parallel outside", Vec3{0.5, 2, 0.5}, Vec3{1, 0, 0}, 100, false, 0},
		{"corner", Vec3{-1, -1, -1}, dir, 100, true, diag},
	}
	for _, c := range cases {
		t.Run(c.name, func(t *testing.T) {
			got, hit := raySlab(c.origin, c.d, box, c.maxT)
			if hit != c.hit || (hit && !near(got, c.wantT)) {
				t.Fatalf("t=%v hit=%v want t=%v hit=%v", got, hit, c.wantT, c.hit)
			}
		})
	}
}

func TestHitscan(t *testing.T) {
	front := Vec3{0, EyeHeight, 5 - PlayerW/2}
	right := Vec3{5 - PlayerW/2, EyeHeight, 0}
	back := Vec3{0, EyeHeight, PlayerW / 2}
	cases := []struct {
		name     string
		spawns   []Vec3
		walls    []Box
		shooter  int
		fire     bool
		yaw      float32
		pitch    float32
		health   []int
		victim   int
		checkPos bool
		pos      Vec3
	}{
		{
			name: "player in front", fire: true, shooter: 0, victim: 1, checkPos: true, pos: front,
			spawns: []Vec3{{0, 0, 0}, {0, 0, 5}},
			health: []int{MaxHealth, MaxHealth - PistolDamage},
		},
		{
			name: "wall blocks", fire: true, shooter: 0, victim: -1,
			spawns: []Vec3{{0, 0, 0}, {0, 0, 5}},
			walls:  []Box{{Min: Vec3{-2, 0, 2}, Max: Vec3{2, 3, 2.4}}},
			health: []int{MaxHealth, MaxHealth},
		},
		{
			name: "near target only", fire: true, shooter: 0, victim: 1,
			spawns: []Vec3{{0, 0, 0}, {0, 0, 4}, {0, 0, 8}},
			health: []int{MaxHealth, MaxHealth - PistolDamage, MaxHealth},
		},
		{
			name: "off to the side", fire: true, shooter: 0, victim: -1,
			spawns: []Vec3{{0, 0, 0}, {4, 0, 0}},
			health: []int{MaxHealth, MaxHealth},
		},
		{
			name: "yaw faces +X", fire: true, shooter: 0, victim: 1, yaw: float32(math.Pi / 2), checkPos: true, pos: right,
			spawns: []Vec3{{0, 0, 0}, {5, 0, 0}},
			health: []int{MaxHealth, MaxHealth - PistolDamage},
		},
		{
			name: "pitch up misses", fire: true, shooter: 0, victim: -1, pitch: 1.2,
			spawns: []Vec3{{0, 0, 0}, {0, 0, 5}},
			health: []int{MaxHealth, MaxHealth},
		},
		{
			name: "coplanar wall wins", fire: true, shooter: 0, victim: -1,
			spawns: []Vec3{{0, 0, 0}, {0, 0, 5 + PlayerW/2}},
			walls:  []Box{{Min: Vec3{-1, 0, 5}, Max: Vec3{1, 3, 6}}},
			health: []int{MaxHealth, MaxHealth},
		},
		{
			name: "trigger up", fire: false, shooter: 0, victim: -1,
			spawns: []Vec3{{0, 0, 0}, {0, 0, 5}},
			health: []int{MaxHealth, MaxHealth},
		},
		{
			name: "far player shoots back", fire: true, shooter: 1, victim: 0, yaw: float32(math.Pi), checkPos: true, pos: back,
			spawns: []Vec3{{0, 0, 0}, {0, 0, 5}},
			health: []int{MaxHealth - PistolDamage, MaxHealth},
		},
		{
			name: "straight down hits floor not self", fire: true, shooter: 0, victim: -1, pitch: -1.2,
			spawns: []Vec3{{0, 0, 0}},
			health: []int{MaxHealth},
		},
	}
	for _, c := range cases {
		t.Run(c.name, func(t *testing.T) {
			w := spawnWorld(c.spawns, c.walls)
			w.Step(map[int]Input{c.shooter: {Fire: c.fire, Yaw: c.yaw, Pitch: c.pitch}})
			ps := w.Players()
			if len(ps) != len(c.health) {
				t.Fatalf("players %d", len(ps))
			}
			for id, hp := range c.health {
				if ps[id].ID != id || ps[id].Health != hp {
					t.Fatalf("player %d health %d want %d", id, ps[id].Health, hp)
				}
			}
			hits := eventsOf(w, EventHit)
			if len(eventsOf(w, EventKill)) != 0 {
				t.Fatal("pistol chip should not kill")
			}
			if c.victim < 0 {
				if len(hits) != 0 {
					t.Fatalf("unexpected hit %+v", hits)
				}
				return
			}
			if len(hits) != 1 {
				t.Fatalf("hits %+v", hits)
			}
			h := hits[0]
			if h.Player != c.victim || h.Other != c.shooter || h.Amount != PistolDamage || h.Weapon != WeaponPistol || h.Tick == 0 || h.Kind != EventHit {
				t.Fatalf("event %+v", h)
			}
			if c.checkPos && (!near(h.Pos.X, c.pos.X) || !near(h.Pos.Y, c.pos.Y) || !near(h.Pos.Z, c.pos.Z)) {
				t.Fatalf("pos %+v want %+v", h.Pos, c.pos)
			}
		})
	}
}

func TestEventsAreLastStepOnly(t *testing.T) {
	w := spawnWorld([]Vec3{{0, 0, 0}, {0, 0, 5}}, nil)
	w.Step(nil)
	if len(w.Events()) != 0 {
		t.Fatal("idle step emitted events")
	}
	w.Step(map[int]Input{0: {Fire: true}})
	if len(eventsOf(w, EventHit)) != 1 {
		t.Fatal("expected one hit")
	}
	w.Step(map[int]Input{0: {}})
	if len(w.Events()) != 0 {
		t.Fatalf("stale events %+v", w.Events())
	}
}
