# ELM369 Operator Console — wireframe v0.1.0

**Design / docs only** — no live deploy, no production host.
**Bound to:** Operator Spine v0.1 (`docs/architecture/ELM369_OPERATOR_SPINE_v0.1.0.md`)
**Authority:** Ziggy GO #2 · Joseph informed · 2026-09-07
**Stamp:** Kokomo, Indiana 46902 USA · Joseph Michael Rose · IX JR · 🌹

## Purpose

One operator-facing **wireframe** for Phase 1 that mirrors Spine commands and dashboard surfaces:
**Status · Roster · Cases · Daily · Vault** — with Joseph-gated actions locked in chrome.

This is the UI/UX binding layer over Spine. Code entrypoint (`tools/elm_operator`) remains Devon’s follow-on; this doc does not implement it.

## Chrome (always visible)

```
┌─ ELM369 Operator Console ────────────────────────────── Kokomo 46902 · IX JR 🌹 ─┐
│ dual: JMR08241978202646902 / JMR0824197846902     spine: operator-spine-v0.1   │
│ [Status] [Roster] [Cases] [Daily] [Vault]     🔒 Joseph-gated actions locked     │
└────────────────────────────────────────────────────────────────────────────────┘
```

- Provenance strip: location, e-sign, dual vault IDs, Spine version
- Nav tabs map 1:1 to operator concerns (not a second tool copy)
- Padlock badge on any control that files, sends, spends, force-pushes, or elevates CASE-006

## Screens

### 1. Status
| Region | Source (Spine / tools) | Shows |
|--------|------------------------|-------|
| Health card | `elm_operator status` → `elm_status` | registry counts, DONE/SCAFFOLD, avg % |
| Hard holds | policy | Kokomo-only, no Florida Google, filing gated, heal dry-run |
| Quick actions | Spine | Refresh status · copy stamp (read-only) |

### 2. Roster
| Region | Source | Shows |
|--------|--------|-------|
| Pod board | `elm_operator roster` → `elm_dashboard.roster` | Command / Security / ELM Build / Phase 2–3 pods |
| Lane detail | roster.py | bot, role, status, agent_id when present |
| Filter | UI only | by pod · OPERATIONAL vs PLACEHOLDER |

### 3. Cases
| Region | Source | Shows |
|--------|--------|-------|
| Case queue | `elm_dashboard` cases | open CASE-YYYYMMDD-NNN (Ziggy-minted only) |
| Tip intake | read-only list | summary + evidence paths |
| 🔒 File / elevate | Joseph gate | disabled until Joseph unlocks |

### 4. Daily
| Region | Source | Shows |
|--------|--------|-------|
| Cadence | Spine + roster board | 8:00 White Rook · 9:15 Ziggy · 9:30 PX · 10:00 Angel/Gyro · EOD Nathan |
| Dry-run | `elm_operator daily-dry-run` | last dry-run JSON summary |
| 🔒 Live schedule mutate | Joseph gate | off by default |

### 5. Vault
| Region | Source | Shows |
|--------|--------|-------|
| Drop paths | Hope lane / vault READMEs | `vault/.../sources/grok/raw/` etc. |
| Offline | `elm_operator offline` | cache status; radios `cannot_control` |
| Stamp | `elm_operator stamp` | Kokomo e-sign line + dual-ID JSON |
| 🔒 Destructive wipe / secret ops | Joseph gate | locked |

## Joseph gates in chrome (non-negotiable)

| Action | Default UI | Unlock |
|--------|------------|--------|
| Agency filing / external disclosure | Locked | Joseph |
| Live send (SMS/email/phone) | Hidden / locked | Never from console (Bo drafts only) |
| Spend / keys / force-push | Locked | Joseph |
| CASE-006 account flags elevate | Locked | Joseph |
| Heal / evolution advance beyond dry-run | Locked | Joseph |
| Live FLUX API | Locked | Future opt-in |

Unlocked controls still require explicit confirm; Spine remains propose/dry-run by default.

## Information architecture

```
Operator (Joseph / Ziggy)
        │
        ▼
 Console wireframe (this doc)
        │
        ▼
 Operator Spine CLI  ──wraps──►  elm_status / elm_dashboard / elm_offline /
        │                         elm_policy / elm_daily_automation
        ▼
 Vault + OpenAPI orchestrator (gated) + Grok roster pods
```

## Non-goals (this PR)

- No hosted website / Vercel / AWS deploy
- No `tools/elm_operator/**` implementation (Devon follow-on)
- No `tools/elm_translator/**` changes
- No inventing CASE/ticket numbers
- No force-push

## Acceptance (later build)

- Wireframe sections map to Spine subcommands without duplicating tool logic
- Chrome always shows Kokomo + dual-ID + Joseph-gate padlocks
- Visual system tokens (v0.1) apply to chrome colors/type when implemented

## Related

- `docs/architecture/ELM369_OPERATOR_SPINE_v0.1.0.md`
- `docs/architecture/ELM369_GROK_BOT_ROSTER_v0.1.0.md`
- `docs/architecture/ELM369_VISUAL_SYSTEM_v0.1.0.md`
- `tools/elm_dashboard/`
