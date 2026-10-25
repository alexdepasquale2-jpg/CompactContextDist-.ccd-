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
	default:
		a.Z = v
	}
}
