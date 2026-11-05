# ELM369 Gyro Matrix 369

Deterministic, simulation-only 9×9 butterfly matrix controlled by three angular
rates (X/Y/Z, radians per second). The three input rates control three stages,
each with three pairwise rotations. Integrated rates are bounded with `tanh`.
This is a linear transform scaffold, not a trained neural network or a sensor
driver.

**Safety boundary:** no hardware access, network calls, persistent state, or
physical actuation. Matrix output is not authorization for any external action.

## Usage

```bash
python3 -m tools.gyro_matrix_369 0.1 -0.2 0.3 --dt 0.01
```

Python API:

```python
from tools.gyro_matrix_369 import build_matrix, transform

matrix = build_matrix((0.1, -0.2, 0.3), 0.01)
output = transform(matrix, (1, 0, 0, 0, 0, 0, 0, 0, 0))
```

## Tests

```bash
python3 -m unittest tools.gyro_matrix_369.tests.test_matrix -v
```
