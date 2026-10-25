# ELM369 Motion Core — Extension Milestone

Adds engine-independent camera pose controls, a complementary roll/pitch filter, axis-aligned collision detection, and a deterministic gyroscope-controlled arcade gameplay model.

## Limitations
- Camera poses are backend-neutral; no rendered window is included.
- The complementary filter estimates roll and pitch only; it cannot correct absolute yaw drift without a heading reference.
- Collision support is AABB only, not a complete physics engine.
- The arcade model is a gameplay simulation, not yet a packaged or rendered game.
- No physical device access, production sensor calibration, video pipeline, Liquid3D solver, or gambling/wagering implementation is included.

Run tests from the elm369_motion_core directory: python -m unittest discover -s tests -v.

ELM369 provenance remains distinct: canonical JMR0824197846902; companion JMR08241978202646902.
