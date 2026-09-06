# Offline engine scaffold

Issue #14. Snapshots key docs, policy, backlog, sandboxes manifest, vault README paths, and completion certificate (when present) for **local** use.

This is the **supported offline path for ELM369**.

It does **not** control satellites, radios, hotspots, or telephony hardware. Those remain explicit non-goals (`cannot_control` in `status`).

```bash
python3 -m tools.elm_offline snapshot
python3 -m tools.elm_offline status
```

## Tests

```bash
python3 -m unittest discover -s tools/elm_offline/tests -v
```
