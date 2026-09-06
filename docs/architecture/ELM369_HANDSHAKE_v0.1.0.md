# ELM369 Handshake & Personal Security Master Guide v0.1.0

Summarized from issue [#38](https://github.com/elkabalatesla-coder/Project-ELM369/issues/38) and SEC-MASTER finish pass.

**E-sign:** Joseph Michael Rose · IX JR · 🌹 / Kokomo IN 46902  
**Vaults:** primary `JMR08241978202646902` · companion `JMR0824197846902`

## Layer model

1. **Transport** — TLS / standard crypto handshake (universal; all major platforms).
2. **Application** — OAuth / API keys (platform-defined).
3. **Operator** — ELM369 AI Panel handshake (internal): session scoped to operator `JMR08241978202646902`, logged via vault logger / audit trail, never expected to be implemented by external social platforms.

## Implementation mapping (this repo)

| Concern | Tool |
|---------|------|
| Audit / session log | `tools/elm_orchestrator` `vault-log` |
| Local provenance watermark | `tools/elm_orchestrator` `watermark` |
| Gated evolution / heal | `tools/elm_evolution`, `heal` (propose / dry-run) |
| Time sync check | `tools/elm_orchestrator` `time-sync` |
| Security log fan-out | `tools/pandora_vault` |
| Geofence stamp | `tools/elm_policy` `location` / `stamp` |
| Bot roster / delegation | `docs/architecture/ELM369_GROK_BOT_ROSTER_v0.1.0.md` |

External APIs still require their own TLS + credentials; ELM369 sits above that stack for operator logging and authorization gates.

## Personal Security Master rules

### 1. Kokomo-only geo

- Declared home: **Kokomo, Indiana, USA 46902**.
- Provenance stamps, e-sign watermarks, and operator-of-record claims must use Kokomo / 46902 — not Texas, San Francisco, Florida, Oakford, or other locales.
- See `docs/policy/ELM369_GEOFENCE_KOKOMO_v0.1.0.md`.

### 2. No Florida-box Google retries

- Remote assistant / cloud desktops that geolocate outside Kokomo (commonly Florida egress) must **not** be used to retry Google/Gmail interactive sign-in on Joseph's behalf.
- Prefer: local download on Joseph's machine → vault drop under `vault/ELM369/.../sources/` or chat attach.
- Do not loop auth challenges from a mismatched geo box.

### 3. Joseph-gated filing

- Any **filing**, legal packet submission, public disclosure, or external transmission is **Joseph-gated**.
- Bots may draft, queue cases (`CASE-YYYYMMDD-NNN` via Ziggy), and propose — they do not file or send.
- Bo drafts never transmit SMS/email/phone.

### 4. Defensive posture

| Lane | Bot | Bound |
|------|-----|-------|
| Threat/scam | White Rook | Detect / guide — no offensive exploit authoring |
| Silent guard | Orange Ninja | Watch / alert |
| Offense-for-defense | Red Dragon Samurai Knight | Proposals only after Joseph **or** Ziggy authorize |

### 5. Heal / mutation

- Orchestrator heal and evolution stay **propose / dry-run** unless Joseph explicitly advances a gated step.
- No credential changes, destructive deletes, or physical actuation from handshake tooling.

## Operator checklist

1. Confirm stamp: `python3 -m tools.elm_policy stamp`
2. Review board: `python3 -m tools.elm_dashboard show`
3. Tail vault: `python3 -m tools.pandora_vault tail --channel pandora -n 20`
4. Draft only (if needed): `python3 -m tools.bo_assistant draft "…"`
5. Filing / send: **stop and ask Joseph**
