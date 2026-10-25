package sim

import (
	"math"
	"testing"
)

const eps = 1e-3

func near(a, b float32) bool { return math.Abs(float64(a-b)) < eps }

func floorOnly() Level {
	return Level{Boxes: []Box{{Vec3{-100, -1, -100}, Vec3{100, 0, 100}}}, Spawns: []Vec3{{0, 0, 0}}}
}

func run(w *World, id int, in Input, ticks int) Player {
	for i := 0; i < ticks; i++ {
		w.Step(map[int]Input{id: in})
	}
	return w.Players()[id]
}

func settle(w *World, id int) { run(w, id, Input{}, 2) }

func TestWalking(t *testing.T) {
	cases := []struct {
		name   string
		in     Input
		dx, dz float32
	}{
		{"forward yaw0", Input{Move: Vec3{Z: 1}}, 0, MoveSpeed},
		{"back", Input{Move: Vec3{Z: -1}}, 0, -MoveSpeed},
		{"strafe right yaw0", Input{Move: Vec3{X: 1}}, -MoveSpeed, 0},
		{"forward yaw90", Input{Move: Vec3{Z: 1}, Yaw: math.Pi / 2}, MoveSpeed, 0},
		{"half stick", Input{Move: Vec3{Z: 0.5}}, 0, MoveSpeed / 2},
		{"idle", Input{}, 0, 0},
	}
	for _, c := range cases {
		t.Run(c.name, func(t *testing.T) {
			w := NewWorld(floorOnly(), 1)
			id := w.AddPlayer()
			settle(w, id)
			p := run(w, id, c.in, 60) // 1 s
			if !near(p.Pos.X, c.dx) || !near(p.Pos.Z, c.dz) || !near(p.Pos.Y, 0) {
				t.Fatalf("pos %+v want x=%v z=%v", p.Pos, c.dx, c.dz)
			}
			if !p.OnGround {
				t.Fatal("should be grounded")
			}
		})
	}
}

func TestDiagonalNormalized(t *testing.T) {
	w := NewWorld(floorOnly(), 1)
	id := w.AddPlayer()
	settle(w, id)
	p := run(w, id, Input{Move: Vec3{X: 1, Z: 1}}, 60)
	if d := (Vec3{p.Pos.X, 0, p.Pos.Z}).Len(); !near(d, MoveSpeed) {
		t.Fatalf("diagonal dist %v want %v", d, MoveSpeed)
	}
}

func TestWallSlide(t *testing.T) {
	lv := floorOnly()
	lv.Boxes = append(lv.Boxes, Box{Vec3{-50, 0, 2}, Vec3{50, 3, 3}}) // wall across +Z
	w := NewWorld(lv, 1)
	id := w.AddPlayer()
	settle(w, id)
	// diagonal into wall: Z blocked, X keeps moving
	p := run(w, id, Input{Move: Vec3{X: -1, Z: 1}}, 120)
	if p.Pos.Z+PlayerW/2 > 2 {
		t.Fatalf("penetrated wall: z=%v", p.Pos.Z)
	}
	if !near(p.Pos.Z+PlayerW/2, 2) {
		t.Fatalf("not touching wall: z=%v", p.Pos.Z)
	}
	if p.Pos.X < 5 { // still sliding along +X (strafe left at yaw0 = +X)
		t.Fatalf("did not slide: x=%v", p.Pos.X)
	}
}

func TestNoTunneling(t *testing.T) {
	cases := []float32{10, 100, 1000, 1e5}
	for _, speed := range cases {
		lv := floorOnly()
		lv.Boxes = append(lv.Boxes, Box{Vec3{-5, 0, 3}, Vec3{5, 3, 3.01}}) // 1 cm wall
		w := NewWorld(lv, 1)
		id := w.AddPlayer()
		settle(w, id)
		w.players[0].Vel = Vec3{}
		// inject huge velocity by driving pos via a custom step
		p := &w.players[0]
		p.Pos.Z += w.sweepAxis(p.Pos, 2, speed*Tick)
		if p.Pos.Z+PlayerW/2 > 3 {
			t.Fatalf("speed %v tunneled to z=%v", speed, p.Pos.Z)
		}
		// falling at terminal velocity onto a thin floor
		lv2 := Level{Boxes: []Box{{Vec3{-5, -0.01, -5}, Vec3{5, 0, 5}}}, Spawns: []Vec3{{0, 50, 0}}}
		w2 := NewWorld(lv2, 1)
		id2 := w2.AddPlayer()
		p2 := run(w2, id2, Input{}, 600)
		if !near(p2.Pos.Y, 0) || !p2.OnGround {
			t.Fatalf("fell through thin floor: %+v", p2.Pos)
		}
	}
}

func TestLandingAndJump(t *testing.T) {
	lv := floorOnly()
	lv.Spawns = []Vec3{{0, 5, 0}}
	w := NewWorld(lv, 1)
	id := w.AddPlayer()
	p := run(w, id, Input{}, 1)
	if p.OnGround {
		t.Fatal("grounded mid-air")
	}
	p = run(w, id, Input{}, 120)
	if !p.OnGround || !near(p.Pos.Y, 0) || p.Vel.Y != 0 {
		t.Fatalf("landing: %+v", p)
	}
	// jump
	p = run(w, id, Input{Jump: true}, 1)
	if p.OnGround || p.Pos.Y <= 0 {
		t.Fatalf("jump didn't lift: %+v", p)
	}
	// holding jump mid-air must not add height (jump only when grounded)
	peakHeld := float32(0)
	for i := 0; i < 30; i++ {
		p = run(w, id, Input{Jump: true}, 1)
		if p.Pos.Y > peakHeld {
			peakHeld = p.Pos.Y
		}
	}
	want := JumpSpeed * JumpSpeed / (2 * Gravity)
	if peakHeld > want+0.2 {
		t.Fatalf("air jump: peak %v > %v", peakHeld, want)
	}
}

func TestJumpOnlyWhenGrounded(t *testing.T) {
	cases := []struct {
		name     string
		spawnY   float32
		wantLift bool
	}{{"grounded", 0, true}, {"airborne", 3, false}}
	for _, c := range cases {
		t.Run(c.name, func(t *testing.T) {
			lv := floorOnly()
			lv.Spawns = []Vec3{{0, c.spawnY, 0}}
			w := NewWorld(lv, 1)
			id := w.AddPlayer()
			if c.spawnY == 0 {
				settle(w, id)
			}
			p := run(w, id, Input{Jump: true}, 1)
			if (p.Vel.Y > 0) != c.wantLift {
				t.Fatalf("vel.y=%v wantLift=%v", p.Vel.Y, c.wantLift)
			}
		})
	}
}

func TestCeilingBonk(t *testing.T) {
	lv := floorOnly()
	lv.Boxes = append(lv.Boxes, Box{Vec3{-2, 2.2, -2}, Vec3{2, 3, 2}})
	w := NewWorld(lv, 1)
	id := w.AddPlayer()
	settle(w, id)
	p := run(w, id, Input{Jump: true}, 1)
	maxY := p.Pos.Y
	bonked := false
	for i := 0; i < 60; i++ {
		p = run(w, id, Input{}, 1)
		if p.Pos.Y+PlayerH > 2.2+eps {
			t.Fatalf("head in ceiling: %v", p.Pos.Y)
		}
		if p.Pos.Y > maxY {
			maxY = p.Pos.Y
		}
		if near(p.Pos.Y+PlayerH, 2.2) {
			bonked = true
		}
	}
	if !bonked || !p.OnGround {
		t.Fatalf("bonked=%v grounded=%v maxY=%v", bonked, p.OnGround, maxY)
	}
}

func TestStandOnCrate(t *testing.T) {
	w := NewWorld(SampleLevel(), 1)
	id := w.AddPlayer()
	w.players[0].Pos = Vec3{0, 3, 0}
	p := run(w, id, Input{}, 120)
	if !near(p.Pos.Y, 1) || !p.OnGround {
		t.Fatalf("crate landing %+v", p.Pos)
	}
}

func TestDeterminism(t *testing.T) {
	script := func(i int) map[int]Input {
		return map[int]Input{
			0: {Move: Vec3{X: float32(i%7) / 7, Z: 1}, Yaw: float32(i) * 0.01, Jump: i%45 == 0},
			1: {Move: Vec3{X: -1, Z: float32(i%5) / 5}, Yaw: -float32(i) * 0.02, Jump: i%30 == 0},
		}
	}
	sim := func() []Player {
		w := NewWorld(SampleLevel(), 42)
		w.AddPlayer()
		w.AddPlayer()
		for i := 0; i < 1200; i++ {
			w.Step(script(i))
		}
		return w.Players()
	}
	a, b := sim(), sim()
	for i := range a {
		if a[i] != b[i] {
			t.Fatalf("diverged: %+v vs %+v", a[i], b[i])
		}
	}
}

func TestStaysInArena(t *testing.T) {
	w := NewWorld(SampleLevel(), 1)
	id := w.AddPlayer()
	p := run(w, id, Input{Move: Vec3{X: 1, Z: -1}, Jump: true}, 600)
	if p.Pos.X < -10 || p.Pos.X > 10 || p.Pos.Z < -10 || p.Pos.Z > 10 || p.Pos.Y < 0 {
		t.Fatalf("escaped: %+v", p.Pos)
	}
}

func TestStubs(t *testing.T) {
	w := NewWorld(SampleLevel(), 1)
	w.AddPlayer()
	w.Step(nil)
	if _, done := w.Winner(); done {
		t.Fatal("no winner yet")
	}
	if len(w.Events()) != 0 || len(w.Projectiles()) != 0 || len(w.Pickups()) != 1 {
		t.Fatal("stub state")
	}
	w.players[0].Kills = 10
	if id, done := w.Winner(); !done || id != 0 {
		t.Fatal("winner at kill limit")
	}
}
