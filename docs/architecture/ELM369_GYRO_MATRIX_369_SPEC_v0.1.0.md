# ELM369 Gyro Matrix 369 Specification v0.1.0

Project: ELM369_JMR08241978202646902  
Status: Simulation-only design scaffold

## Purpose

Specify a deterministic 3/6/9 butterfly matrix controlled by three-axis
gyroscope-rate samples. The implementation is a linear transform prototype; it
does not train a neural network, read a physical sensor, or control hardware.

## Contract

- Input: three finite angular rates in radians per second and a finite positive
  sample interval in seconds.
- Layout: a 9-value input and output vector, represented as a 9×9 matrix.
- Stages: three sequential stages, each applying three disjoint pairwise
  rotations to nine values. The stages use pairs `(0,1), (3,4), (6,7)`,
  `(1,2), (4,5), (7,8)`, then `(2,3), (5,6), (8,0)`.
- Control: each axis rate controls its corresponding stage. The stage angle is
  `tanh(rate × dt) × max_angle`, with `max_angle` in `(0, π/4]`.
- Invariant: stage rotations are orthogonal; finite input vectors retain their
  Euclidean norm up to floating-point rounding.

## Safety and authority

The implementation is local and deterministic. It performs no hardware I/O,
network I/O, persistence, or physical actuation. The calculated matrix is
simulation output only and cannot authorize external or safety-critical action.
Any future sensor integration or actuation requires a separate design,
validation, and explicit authorization under applicable ELM369 safety policy.

## Implementation

Reference module: `tools/gyro_matrix_369/`  
Build a matrix: `python3 -m tools.gyro_matrix_369 0.1 -0.2 0.3 --dt 0.01`
