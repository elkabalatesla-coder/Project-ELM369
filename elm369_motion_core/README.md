# ELM369 Motion–Matrix–Qbit Core v0.1.0

**Status:** isolated development implementation on branch `copilot/elm369-motion-matrix-qbit-core-v0-1`. This is not merged into `main`.

## Scope
- Dependency-free 4x4 matrix validation, multiplication, and homogeneous point transforms.
- Quaternion operations and angular-velocity integration in radians/second.
- Bounded classical QBIT-inspired decision scoring with an independent risk gate.
- Fixed-timestep motion runtime with ordered event logging and SHA-256 replay digest.
- Unit tests for core mathematical and determinism invariants.

## Important limitations
- QBIT-inspired scoring is classical weighted arithmetic, not quantum computing.
- Quaternion integration does not correct IMU drift; sensor fusion and calibration are later modules.
- Replay hashes detect differences in the event log; they do not prove authorship or provide a signed audit trail.
- Cross-platform bit-identical floating-point results are not guaranteed. Current tests check repeatability in the same runtime.
- No physical device access, rendering engine, game engine, video pipeline, fluid solver, gambling/wagering system, or deployment adapter is included in this milestone.

## Run tests
From this directory, using Python 3.10+:

```bash
python -m unittest discover -s tests -v
```

## Provenance
Canonical anchor: `JMR0824197846902`  
Companion/legacy-format anchor: `JMR08241978202646902`

These identifiers retain distinct provenance. This isolated branch does not modify the existing baseline or merge identifier records.
