# Project ELM369 Mission Control Dashboard

Canonical operational dashboard board for Project ELM369. The runtime JSON board is authoritative; HTML artifacts are presentation layers.

- Live progress / vault / artifacts / path verification
- **Roster lanes** (AI/Grok operations roster)
- **Case queue summary** (`CASE-YYYYMMDD-NNN`, Ziggy collector)

Vault: primary `JMR08241978202646902` · companion `JMR0824197846902`  
Stamp: Kokomo IN 46902 · Joseph Michael Rose · IX JR · 🌹

## Commands

```bash
python3 -m tools.elm_dashboard show
python3 -m tools.elm_dashboard show --no-cases
python3 -m tools.elm_dashboard roster
python3 -m tools.elm_dashboard cases
```

## Roster lanes

See `docs/architecture/ELM369_GROK_BOT_ROSTER_v0.1.0.md` for Ziggy, Hope, Vid Cambot,
Private Eye X, Red Dragon Samurai Knight, Orange Ninja, White Rook, and New Bot.

## Hard rules surfaced on the board

- Kokomo-only geo (46902)
- No Florida-box Google retries
- Filing Joseph-gated
- Heal propose/dry-run only
- No live SMS / phone / ADB / satellite

## Canonical state

`python3 -m tools.elm_dashboard show` emits `elm369.mission_control_dashboard.v1` with `dashboard_state=OPERATIONAL` and runtime tools as the source of truth.

## Tests

```bash
python3 -m unittest tools.elm_dashboard.tests.test_board -v
```
