# ELM369 Operator Spine v0.1.0

Product/architecture unify pass for Phase 1 (**design doc** — code entrypoint follows).

## Purpose

Give Joseph and Ziggy **one** Phase-1 operator entrypoint over the live Python tool stack, with dual-ID + Kokomo provenance, without inventing a second copy of each tool.

## Planned commands (code PR next)

| Subcommand | Wraps | Notes |
|------------|-------|-------|
| `status` | `tools.elm_status.report.build` | JSON health envelope + Spine provenance |
| `roster` | `tools.elm_dashboard.roster.roster_lanes` | Grok bot roster lanes |
| `offline` | `tools.elm_offline.engine.status` | Offline cache status (`cannot_control` radios) |
| `stamp` | `tools.elm_policy.geofence.stamp_line` | Kokomo e-sign stamp + dual-ID JSON |
| `daily-dry-run` | `tools.elm_daily_automation.runner.run_daily(dry_run=True)` | Safe daily pass |

```bash
python3 -m tools.elm_operator status
python3 -m tools.elm_operator roster
python3 -m tools.elm_operator offline
python3 -m tools.elm_operator stamp
python3 -m tools.elm_operator daily-dry-run
```

## Provenance fields

Every Spine JSON envelope should include:

- `spine`: `operator-spine-v0.1`
- `dual_id`: primary `JMR08241978202646902`, companion `JMR0824197846902`
- `location`: Kokomo, Indiana 46902 USA
- `esign`: Joseph Michael Rose · IX JR · 🌹
- `stamp`: human-readable stamp line from `elm_policy`

## Sequencing

1. **This PR** — architecture rewrite + this design doc + REMAINING_DESIGN pointer.
2. AUDIO-TX offline slice (Charles) — clears last SCAFFOLD; no translator overlap with Spine.
3. **Follow-on** — ship `tools/elm_operator` implementing the table above.

## Non-goals (this docs PR)

- Does not add `tools/elm_operator/**` yet.
- Does not touch `tools/elm_translator/`.
- Does not rewrite `docs/STATUS.md` registry counts.
- No live send / telephony / FLUX API.
- No force-push; ship by PR only.
- Does not mint CASE / ticket numbers.
