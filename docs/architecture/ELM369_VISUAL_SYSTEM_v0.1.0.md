# ELM369 Visual System v0.1.0

**Docs only** — tokens + watermark rules for apps, sites, packs, and Operator Console chrome.
**Authority:** Ziggy GO #3 · Joseph informed · 2026-09-07
**Stamp:** Kokomo, Indiana 46902 USA · Joseph Michael Rose · IX JR · 🌹

## Purpose

One shared visual language so Reggie packs, artifact gallery, Liquid-3D sketches, console wireframe, and future Web Master pages do not drift.

## Brand marks

| Element | Value |
|---------|-------|
| Operator name | Joseph Michael Rose |
| Initials | IX JR |
| E-symbol | 🌹 |
| Primary vault ID | `JMR08241978202646902` |
| Companion vault ID | `JMR0824197846902` |
| Geo | Kokomo, Indiana 46902 USA |
| Project | ELM369 / Project-ELM369 |

## Color tokens (v0.1)

Aligned with existing artifacts gallery (cyan-on-dark). Hex are design targets — implement later in CSS/theme.

| Token | Hex | Use |
|-------|-----|-----|
| `--elm-bg` | `#0B1220` | App / console background |
| `--elm-surface` | `#121A2B` | Cards, panels |
| `--elm-border` | `#1E2A44` | Dividers |
| `--elm-text` | `#E6EDF7` | Primary text |
| `--elm-muted` | `#8B9BB8` | Secondary text |
| `--elm-accent` | `#3DE0FF` | Links, focus, active tab (cyan) |
| `--elm-accent-2` | `#7C5CFF` | Secondary accent (violet) |
| `--elm-success` | `#3DDC97` | Healthy / DONE |
| `--elm-warn` | `#F5C542` | SCAFFOLD / hold |
| `--elm-danger` | `#FF5C7A` | Locked / threat |
| `--elm-lock` | `#F5C542` | Joseph-gate padlock |

## Typography

| Role | Guidance |
|------|----------|
| UI sans | System UI stack or Inter / IBM Plex Sans |
| Mono | JetBrains Mono / ui-monospace for IDs, CASE #, paths |
| Hierarchy | Console title 16–18px semibold · section 14px · body 13px · mono 12px |

## Spacing & radius

- Base unit: 8px
- Card radius: 8–12px
- Dense operator tables: 4px row gap OK
- Focus ring: 2px `--elm-accent`

## Watermark / provenance rules

1. **Operator chrome** always shows: `Kokomo, Indiana 46902 USA · Joseph Michael Rose · IX JR · 🌹`
2. **Export packs / PDFs** (Reggie): footer watermark with dual vault IDs + date (ET labeled) + e-sign line
3. **Local hash watermark** (`elm_orchestrator watermark`) is provenance, **not** a CA certificate — label UI copy accordingly
4. Never display Florida or non-Kokomo as operator location
5. Never invent CASE / ticket numbers in chrome; show Ziggy-minted IDs only
6. Draft-only surfaces (Bo) must badge **NEVER SENDS**

### Watermark placement

| Surface | Placement |
|---------|-----------|
| Console | Top chrome strip |
| PDF/ZIP pack | Footer every page + cover |
| Gallery HTML | Small footer |
| Spine JSON | `esign`, `location`, `dual_id`, `spine` fields |

## Iconography (light)

- Padlock = Joseph gate
- Rose 🌹 = e-sign mark (sparingly; chrome / stamps)
- Status dots: success / warn / danger tokens above

## Do / Don’t

| Do | Don’t |
|----|-------|
| Cyan-on-dark operator aesthetic | Bright consumer pastels for ops console |
| Lock gated actions visually | Hide gates only in copy |
| Reuse tokens across packs + console | One-off hex per bot |
| Cite Kokomo 46902 | Imply remote-box geo is Joseph |

## Rollout

1. This doc (v0.1 tokens + rules)
2. Apply to Operator Console wireframe mockups / CSS when UI ships
3. Reggie pack templates adopt footer rules on next pack design pass
4. Web Master public pages (when tasked) inherit tokens

## Non-goals

- No live brand site deploy in this PR
- No trademark filing
- No change to watermark crypto beyond documenting existing local-hash behavior

## Related

- `docs/architecture/ELM369_OPERATOR_CONSOLE_WIREFRAME_v0.1.0.md`
- `docs/architecture/ELM369_OPERATOR_SPINE_v0.1.0.md`
- `docs/ELM369_IDENTITY.md`
- `docs/policy/ELM369_GEOFENCE_KOKOMO_v0.1.0.md`
