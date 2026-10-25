package sim

import "math"

func (a Vec3) Add(b Vec3) Vec3      { return Vec3{a.X + b.X, a.Y + b.Y, a.Z + b.Z} }
func (a Vec3) Sub(b Vec3) Vec3      { return Vec3{a.X - b.X, a.Y - b.Y, a.Z - b.Z} }
func (a Vec3) Scale(s float32) Vec3 { return Vec3{a.X * s, a.Y * s, a.Z * s} }
func (a Vec3) Len() float32         { return float32(math.Sqrt(float64(a.X*a.X + a.Y*a.Y + a.Z*a.Z))) }
func (a Vec3) axis(i int) float32   { return [3]float32{a.X, a.Y, a.Z}[i] }
func (a *Vec3) setAxis(i int, v float32) {
	switch i {
	case 0:
		a.X = v
	case 1:
		a.Y = v
	case 2:
		a.Z = v
	default:
		panic("axis out of range")
	}
}

// raySlab is the ray vs AABB slab test. dir does not have to be unit length;
// hitscan passes a unit direction so t is meters. maxT is inclusive. A ray
// that starts inside the box hits at t = 0.
func raySlab(origin, dir Vec3, b Box, maxT float32) (float32, bool) {
	tmin := float32(0)
	tmax := maxT
	for a := 0; a < 3; a++ {
		o := origin.axis(a)
		d := dir.axis(a)
		mn := b.axisMin(a)
		mx := b.axisMax(a)
		if d > -1e-8 && d < 1e-8 {
			if o < mn || o > mx {
				return 0, false
			}
			continue
		}
		inv := 1 / d
		t1 := (mn - o) * inv
		t2 := (mx - o) * inv
		if t1 > t2 {
			t1, t2 = t2, t1
		}
		if t1 > tmin {
			tmin = t1
		}
		if t2 < tmax {
			tmax = t2
		}
		if tmin > tmax {
			return 0, false
		}
	}
	return tmin, true
}
