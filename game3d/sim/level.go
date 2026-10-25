package sim

// SampleLevel: 20x20 m floor (top at y=0), four perimeter walls, a central
// crate (1 m tall) and a raised platform with a low ceiling slab for tests/demo.
func SampleLevel() Level {
	return Level{
		Boxes: []Box{
			{Vec3{-10, -1, -10}, Vec3{10, 0, 10}},   // floor
			{Vec3{-10, 0, -10.5}, Vec3{10, 4, -10}}, // N wall
			{Vec3{-10, 0, 10}, Vec3{10, 4, 10.5}},   // S wall
			{Vec3{-10.5, 0, -10}, Vec3{-10, 4, 10}}, // W wall
			{Vec3{10, 0, -10}, Vec3{10.5, 4, 10}},   // E wall
			{Vec3{-1, 0, -1}, Vec3{1, 1, 1}},        // crate
			{Vec3{4, 2.5, 4}, Vec3{8, 3, 8}},        // overhang (ceiling test)
		},
		Spawns:  []Vec3{{-8, 0, -8}, {8, 0, -8}, {-8, 0, 8}, {8, 0, 8}},
		Pickups: []Pickup{{Pos: Vec3{0, 1, 0}, Kind: WeaponRocket, Active: true}},
	}
}
