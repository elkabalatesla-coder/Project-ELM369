# elm_operator — Operator Spine v0.1

Phase-1 ops facade for Project ELM369.

```bash
python3 -m tools.elm_operator status
python3 -m tools.elm_operator roster
python3 -m tools.elm_operator offline
python3 -m tools.elm_operator stamp
python3 -m tools.elm_operator daily-dry-run
```

## Exit codes

| Command | `0` | `1` |
|---------|-----|-----|
| `status` | report `ok` | report not ok |
| `offline` | snapshot present (`ok: true`) | **no snapshot** (`error: no_snapshot`) or not ok |
| `roster` / `stamp` | success | (rare parse/import failure) |
| `daily-dry-run` | daily report ok | daily report not ok |

Run `python3 -m tools.elm_offline snapshot` before expecting `offline` to exit 0.

## Tests

```bash
python3 -m unittest tools.elm_operator.tests.test_cli -v
```

See `docs/architecture/ELM369_OPERATOR_SPINE_v0.1.0.md`.
