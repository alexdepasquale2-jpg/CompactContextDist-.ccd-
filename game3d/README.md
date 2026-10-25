Drop-in for testing/game3d/: copy ONLY sim/ to testing/game3d/sim/ (replacing the stub contract.go/mathx.go).
go.mod here is LOCAL TESTING ONLY (no raylib) — do NOT copy it; use Arnold's go.mod.
Test: GOWORK=off go vet ./... && GOWORK=off go test ./...   (in repo: also go build -tags noaudio)
