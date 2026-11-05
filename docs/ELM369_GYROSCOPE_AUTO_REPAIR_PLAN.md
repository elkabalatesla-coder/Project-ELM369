# ELM369 Gyroscope Processing — v1

This additive implementation establishes a sensor-agnostic software layer for 3-axis gyroscope samples. It is deliberately isolated from the existing baseline and does not connect to hardware, alter device calibration, or command robots/vehicles/drones.

## Contract
- Inputs: timestamp in seconds and three angular-rate values in radians/second.
- Validation: finite numeric values, exactly three axes, configured rate limits, strictly increasing timestamps, and bounded time gaps.
- Correction: optional explicit stationary-sample bias calibration, per-axis deadband, and first-order low-pass filtering.
- Failure behavior: invalid samples raise `GyroSampleError`; excessive timestamp gaps reset filter/time state and reject the current sample.
- Status: readings distinguish calibrated from uncalibrated processing. Uncalibrated output is not certified sensor data.

## Scope limits
This does not provide absolute orientation, gravity compensation, sensor-fusion with an accelerometer/magnetometer, hardware self-test, physical gyro repair, or actuator safety certification. Calibration assumes the sensor is stationary; a real deployment must validate mounting, units, axis mapping, temperature drift, sensor datasheet limits, and platform-specific fail-safe behavior.

## Tests
Run from the repository root:
```sh
python -m unittest discover -s tests
```

## Governance
Additive branch only. Do not merge into `main` until reviewed and tested on representative recorded sensor data and, separately, on target hardware under a documented safety plan. Existing identifiers and baseline files remain untouched.
