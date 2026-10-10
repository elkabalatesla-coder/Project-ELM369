"""ELM369 gyroscope processing safety layer (sensor-agnostic, software-only).

This module validates and filters gyro samples. It does not access hardware,
write device settings, or issue actuator commands. Callers must provide samples
in radians/second and timestamps in seconds.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Iterable, Optional, Tuple

Vector3 = Tuple[float, float, float]


class GyroSampleError(ValueError):
    """Raised when a sample is malformed or unsafe to process."""


def _vector3(values: Iterable[float], field: str) -> Vector3:
    try:
        result = tuple(float(v) for v in values)
    except (TypeError, ValueError) as exc:
        raise GyroSampleError(f"{field} must contain three numeric values") from exc
    if len(result) != 3 or not all(isfinite(v) for v in result):
        raise GyroSampleError(f"{field} must contain exactly three finite values")
    return result  # type: ignore[return-value]


@dataclass(frozen=True)
class GyroConfig:
    max_rate_rad_s: float = 35.0
    deadband_rad_s: float = 0.002
    low_pass_alpha: float = 0.25
    max_dt_s: float = 0.25
    max_calibration_samples: int = 5000

    def __post_init__(self) -> None:
        if not isfinite(self.max_rate_rad_s) or self.max_rate_rad_s <= 0:
            raise ValueError("max_rate_rad_s must be finite and positive")
        if not isfinite(self.deadband_rad_s) or self.deadband_rad_s < 0:
            raise ValueError("deadband_rad_s must be finite and non-negative")
        if not 0 < self.low_pass_alpha <= 1:
            raise ValueError("low_pass_alpha must be in (0, 1]")
        if not isfinite(self.max_dt_s) or self.max_dt_s <= 0:
            raise ValueError("max_dt_s must be finite and positive")
        if self.max_calibration_samples < 2:
            raise ValueError("max_calibration_samples must be at least 2")


@dataclass(frozen=True)
class GyroReading:
    timestamp_s: float
    raw_rad_s: Vector3
    corrected_rad_s: Vector3
    status: str


class GyroscopeProcessor:
    """Calibrate bias and safely filter timestamped 3-axis gyro readings."""

    def __init__(self, config: Optional[GyroConfig] = None) -> None:
        self.config = config or GyroConfig()
        self._bias: Vector3 = (0.0, 0.0, 0.0)
        self._filtered: Optional[Vector3] = None
        self._last_timestamp: Optional[float] = None
        self._calibrated = False

    @property
    def bias_rad_s(self) -> Vector3:
        return self._bias

    @property
    def calibrated(self) -> bool:
        return self._calibrated

    def calibrate(self, stationary_samples: Iterable[Iterable[float]]) -> Vector3:
        """Set bias to the per-axis mean of stationary samples; no implicit calibration."""
        samples = []
        for sample in stationary_samples:
            if len(samples) >= self.config.max_calibration_samples:
                raise GyroSampleError("calibration sample limit exceeded")
            samples.append(_vector3(sample, "calibration sample"))
        if len(samples) < 2:
            raise GyroSampleError("at least two stationary samples are required")
        # Reject likely motion/outliers rather than learning a dangerous bias.
        for sample in samples:
            if any(abs(v) > self.config.max_rate_rad_s for v in sample):
                raise GyroSampleError("calibration sample exceeds configured rate limit")
        means = tuple(sum(sample[i] for sample in samples) / len(samples) for i in range(3))
        if any(abs(v) > 1.0 for v in means):
            raise GyroSampleError("calibration bias is implausibly large; verify stationary sensor")
        self._bias = means  # type: ignore[assignment]
        self._filtered = None
        self._last_timestamp = None
        self._calibrated = True
        return self._bias

    def reset(self, *, clear_calibration: bool = False) -> None:
        """Reset filter/time state. Bias is preserved unless explicitly cleared."""
        self._filtered = None
        self._last_timestamp = None
        if clear_calibration:
            self._bias = (0.0, 0.0, 0.0)
            self._calibrated = False

    def process(self, timestamp_s: float, raw_rad_s: Iterable[float]) -> GyroReading:
        if not isfinite(timestamp_s):
            raise GyroSampleError("timestamp must be finite")
        raw = _vector3(raw_rad_s, "gyro sample")
        if any(abs(v) > self.config.max_rate_rad_s for v in raw):
            raise GyroSampleError("gyro rate exceeds configured safety limit")
        if self._last_timestamp is not None:
            dt = timestamp_s - self._last_timestamp
            if dt <= 0:
                raise GyroSampleError("timestamps must increase strictly")
            if dt > self.config.max_dt_s:
                self.reset()
                raise GyroSampleError("timestamp gap exceeded limit; filter state reset")

        corrected = tuple(0.0 if abs(raw[i] - self._bias[i]) < self.config.deadband_rad_s
                          else raw[i] - self._bias[i] for i in range(3))
        if self._filtered is None:
            filtered = corrected
        else:
            a = self.config.low_pass_alpha
            filtered = tuple(a * corrected[i] + (1 - a) * self._filtered[i]
                             for i in range(3))
        self._filtered = filtered  # type: ignore[assignment]
        self._last_timestamp = timestamp_s
        return GyroReading(timestamp_s, raw, filtered,
                           "OK_CALIBRATED" if self._calibrated else "OK_UNCALIBRATED")
