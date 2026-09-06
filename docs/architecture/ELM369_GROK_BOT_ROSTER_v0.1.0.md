# ELM369 Grok Bot Roster v0.1.0

Live Grok bot / assistant lane map for Project ELM369.

**E-sign:** Joseph Michael Rose · IX JR · 🌹 / Kokomo IN 46902  
**Updated:** 2026-09-06

## Vault IDs

| Role | ID |
|------|----|
| Primary vault | `JMR08241978202646902` |
| Companion vault | `JMR0824197846902` |

Project tracking code / operator session stamps use the primary ID; companion designs (Bo / panel helpers) may cite both.

## Live roster

| Bot | Lane | Mission | Notes |
|-----|------|---------|-------|
| **Ziggy** | intake | Complaint / case collector | Assigns `CASE-YYYYMMDD-NNN`; first stop for intake |
| **Hope** | vault | Vault / ELM tips | Guidance on vault drop paths, provenance, offline tips |
| **Vid Cambot** | media | Media | Capture / organize media assists (no unauthorized publish) |
| **Private Eye X** | research | 9:30 dig | Scheduled research dig lane |
| **Red Dragon Samurai Knight** | defense | Offense-for-defense | **Requires Joseph or Ziggy authorization** before action proposals |
| **Orange Ninja** | guardian | Silent guardian | Watch / alert posture; no noisy actuation |
| **White Rook** | threat | Malware / threat / scam guard | Defensive detection & guidance only |
| **New Bot** | reserve | Placeholder TBD | Reserved slot — do not invent capabilities |

## Delegation workflow

1. **Intake** — Ziggy opens or resumes a case id (`CASE-YYYYMMDD-NNN`) and records the ask.
2. **Triage** — Route by lane: vault tips → Hope; media → Vid Cambot; research → Private Eye X; threat/scam → White Rook; silent watch → Orange Ninja.
3. **Defense proposals** — Red Dragon Samurai Knight may *propose* offense-for-defense steps only after **Joseph** or **Ziggy** authorizes the lane for that case.
4. **Drafts** — Bo (`tools/bo_assistant`) may draft SMS/email/phone scripts; **never sends**.
5. **Board** — AI-HUB (`tools/elm_dashboard`) shows roster lanes + case queue summary for operator review.
6. **Filing / external disclosure** — **Joseph-gated**. No bot files, publishes, or transmits without explicit Joseph approval.
7. **Heal / mutation** — Orchestrator heal stays **propose / dry-run** only unless Joseph explicitly advances a gated evolution step.

```text
Operator (Joseph / ROOT_ADMIN)
        │
        ▼
   Ziggy (CASE-…) ──► lane bots (Hope / Vid / PIX / White Rook / Orange Ninja)
        │                      │
        │                      ▼
        └──── authorize ──► Red Dragon (proposals only)
                              │
                              ▼
                     Joseph-gated filing / send
```

## Hard rules

1. **Geo:** Kokomo, Indiana **46902** only for operator-of-record / provenance stamps.
2. **No Florida-geo Google retries:** Remote boxes that geolocate elsewhere (e.g. Florida) must not retry Google/Gmail interactive sign-in for Joseph; prefer local download + vault drop / chat attach.
3. **Filing is Joseph-gated:** External filing, legal submission, or public disclosure requires Joseph's explicit go-ahead.
4. **No live SMS / phone / ADB / satellite** from these bots or scaffolds.
5. **Heal** remains propose / dry-run unless Joseph advances a gated step.

## Tooling links

| Concern | Path |
|---------|------|
| Roster on JSON board | `tools/elm_dashboard` (`show` / `roster` / `cases`) |
| Draft-only comms | `tools/bo_assistant` |
| Security logs | `tools/pandora_vault` |
| Handshake / SEC-MASTER | `docs/architecture/ELM369_HANDSHAKE_v0.1.0.md` |
| Geofence policy | `docs/policy/ELM369_GEOFENCE_KOKOMO_v0.1.0.md` |
| Panel metadata | `PROJECT_METADATA.json` → `panel_and_team_members` |

## Related vault trees

- `vault/ELM369/JMR08241978202646902/`
- `vault/ELM369/JMR0824197846902/`
