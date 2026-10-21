# ELM369 Motion Arena — Godot 4 prototype

**Status:** isolated engine-adapter prototype; not a production game or a sensor-certified build.

## Run
1. Install Godot 4.x.
2. Open this folder's `project.godot` in Godot.
3. Press **F6** to run the current scene or **F5** to run the project.
4. Use **Left/Right arrows** on desktop. On supported Android devices, tilt input is read from the accelerometer. Press **R** after game over to restart.

## Prototype behavior
- Procedurally builds a simple 3D arena, follow camera, player, green collectibles, red hazards, and HUD.
- Collectibles award 10 points once each; hazards consume one life each.
- Movement uses a frame-delta-scaled speed and clamps the player to arena bounds.
- Keyboard input overrides tilt input for deterministic desktop testing.

## ELM369 boundaries
- This is an engine adapter, not a replacement for the Python motion core or the repository's immutable baseline.
- The QBIT-inspired score in the broader project is classical arithmetic. This demo does not run quantum hardware or quantum simulation.
- Accelerometer axes, units, filtering, device orientation, and neutral calibration differ by hardware. Validate and calibrate on each target device. The prototype does not claim full gyroscope fusion: this first adapter reads accelerometer tilt only.
- The demo uses direct distance checks for contacts rather than a production physics/gameplay pipeline.
- No video rendering/export, Liquid3D fluid simulation, networking, wagering, payments, or real-money gambling is implemented. Arcade scoring is included; any gambling-style game would require separate legal, age, fairness, and jurisdiction-specific compliance design.
- No automated Godot runtime test is claimed until the project is run under an installed Godot 4 executable.

## Next engineering steps
1. Add neutral-pose calibration and filtered sensor fusion with keyboard fallback.
2. Add seeded, replayable target/hazard spawning and deterministic simulation ticks.
3. Add automated headless Godot parse/startup tests in CI.
4. Add engine-neutral genre profiles and a separately scoped video/Liquid3D adapter.
