# ELM369 Operator Spine v0.1.0

Product/architecture unify pass for Phase 1.

## Purpose

Give Joseph and Ziggy **one** Phase-1 operator entrypoint over the live Python tool stack, with dual-ID + Kokomo provenance, without inventing a second copy of each tool.

## Commands

| Subcommand | Wraps | Notes |
|------------|-------|-------|
| `status` | `tools.elm_status.report.build` | JSON health envelope + Spine provenance; exit `1` if report not ok |
| `roster` | `tools.elm_dashboard.roster.roster_lanes` | Grok bot roster lanes |
| `offline` | `tools.elm_offline.engine.status` | Offline cache status (`cannot_control` radios). **Exit `1` when no snapshot** (`error: no_snapshot`); run `python3 -m tools.elm_offline snapshot` first |
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

Every Spine JSON envelope includes:

- `spine`: `operator-spine-v0.1`
- `dual_id`: primary `JMR08241978202646902`, companion `JMR0824197846902`
- `location`: Kokomo, Indiana 46902 USA
- `esign`: Joseph Michael Rose · IX JR · 🌹
- `stamp`: human-readable stamp line from `elm_policy`

## Tests

Repo convention is **unittest** (same as `elm_offline` / `elm_translator`):

```bash
python3 -m unittest tools.elm_operator.tests.test_cli -v
```

## Non-goals (this version)

- Does not touch `tools/elm_translator/` (AUDIO-TX lane — see PR #87 offline glossary DONE; STT/TTS remain non-goals).
- No live send / telephony / FLUX API.
- No force-push; ship by PR only.
- Does not mint CASE / ticket numbers.

## Follow-ons

- AUDIO-TX: merge/keep #87 offline glossary DONE; STT/TTS stay out of scope unless Joseph/Ziggy reopen that lane.
- Deeper quantum / HQM + FLUX opt-in specs (Archy lane).
- Dante console wireframe can bind to this Spine after merge.
