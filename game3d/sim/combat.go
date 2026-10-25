package sim

import "math"

func eyePos(p Player) Vec3 { return p.Pos.Add(Vec3{Y: EyeHeight}) }

// aimDir points where the player is looking. Yaw 0 faces +Z; positive pitch looks up.
func aimDir(yaw, pitch float32) Vec3 {
	sy, cy := math.Sincos(float64(yaw))
	sp, cp := math.Sincos(float64(pitch))
	return Vec3{float32(sy * cp), float32(sp), float32(cy * cp)}
}

func (w *World) stepWeapon(p *Player, in Input) {
	if !in.Fire || !p.Alive || p.Weapon != WeaponPistol {
		return
	}
	w.fireHitscan(p, PistolDamage)
}

func (w *World) fireHitscan(p *Player, dmg int) {
	origin := eyePos(*p)
	dir := aimDir(p.Yaw, p.Pitch)
	best := HitscanRange
	hitID := -1
	var hitPos Vec3
	found := false
	for i := range w.players {
		o := &w.players[i]
		if o.ID == p.ID || !o.Alive {
			continue
		}
		t, ok := raySlab(origin, dir, playerBox(o.Pos), best)
		if !ok || t > best || (found && t >= best) {
			continue
		}
		best = t
		hitID = o.ID
		hitPos = origin.Add(dir.Scale(t))
		found = true
	}
	for _, b := range w.level.Boxes {
		t, ok := raySlab(origin, dir, b, best)
		if ok && t <= best {
			best = t
			hitID = -1
		}
	}
	if hitID >= 0 {
		w.hurt(hitID, p.ID, dmg, WeaponPistol, hitPos)
	}
}

func (w *World) hurt(victim, attacker, dmg int, kind WeaponKind, pos Vec3) {
	if dmg <= 0 || victim < 0 || victim >= len(w.players) {
		return
	}
	p := &w.players[victim]
	if !p.Alive {
		return
	}
	applied := dmg
	if applied > p.Health {
		applied = p.Health
	}
	if applied == 0 {
		return
	}
	p.Health -= applied
	w.events = append(w.events, Event{
		Kind:   EventHit,
		Tick:   w.tick,
		Player: victim,
		Other:  attacker,
		Amount: applied,
		Weapon: kind,
		Pos:    pos,
	})
}
