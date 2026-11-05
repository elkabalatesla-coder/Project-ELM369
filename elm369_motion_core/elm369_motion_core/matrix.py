"""Small dependency-free 4x4 matrix utilities using row-major storage.

Vectors are treated as column vectors: p' = M @ p. Transform composition
order must be documented by each caller; this module does not assume a
specific graphics API's handedness or clip-space convention.
"""
from __future__ import annotations
from math import isfinite
from typing import Iterable, Sequence

Matrix4 = tuple[tuple[float, float, float, float], ...]


def matrix4(values: Iterable[Iterable[float]]) -> Matrix4:
    rows = tuple(tuple(float(v) for v in row) for row in values)
    if len(rows) != 4 or any(len(row) != 4 for row in rows):
        raise ValueError("A 4x4 matrix must contain four rows of four values.")
    if not all(isfinite(v) for row in rows for v in row):
        raise ValueError("Matrix values must be finite.")
    return rows


def identity4() -> Matrix4:
    return ((1.0, 0.0, 0.0, 0.0),
            (0.0, 1.0, 0.0, 0.0),
            (0.0, 0.0, 1.0, 0.0),
            (0.0, 0.0, 0.0, 1.0))


def multiply4(a: Sequence[Sequence[float]],
              b: Sequence[Sequence[float]]) -> Matrix4:
    aa, bb = matrix4(a), matrix4(b)
    return matrix4(tuple(
        tuple(sum(aa[i][k] * bb[k][j] for k in range(4))
              for j in range(4))
        for i in range(4)
    ))


def transform_point(matrix: Sequence[Sequence[float]],
                    point: Sequence[float]) -> tuple[float, float, float, float]:
    """Transform (x,y,z,w); 3D points normally use w=1."""
    m = matrix4(matrix)
    if len(point) != 4:
        raise ValueError("Point must have four homogeneous coordinates.")
    p = tuple(float(v) for v in point)
    if not all(isfinite(v) for v in p):
        raise ValueError("Point coordinates must be finite.")
    return tuple(sum(m[i][j] * p[j] for j in range(4))
                 for i in range(4))  # type: ignore[return-value]
