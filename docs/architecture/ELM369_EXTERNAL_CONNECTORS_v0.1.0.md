# ELM369 External Connectors v0.1.0

Project: ELM369_JMR08241978202646902  
E-sign: Joseph Michael Rose · IX JR · 🌹  
Location stamp: Kokomo, Indiana 46902 USA

## Purpose

Document how external content and services connect to this repo — and what stays intentionally out of scope.

## Grok export drop path (supported)

1. Place a real Grok/X export (`.json`, `.jsonl`, or `.zip`) under:
   `vault/ELM369/JMR08241978202646902/sources/grok/raw/`
2. Ingest and normalize:
   ```bash
   python3 -m tools.grok_archive ingest --path vault/ELM369/JMR08241978202646902/sources/grok/raw
   python3 -m tools.grok_archive extract-backlog
   ```
3. Layout: `sources/grok/{raw,normalized,extracted}/` — see `tools/grok_archive/README.md`.

No live Grok API scrape is required for archive intake; a dropped export file is the supported path.

## FLUX image compose (scaffold)

- `tools/elm_flux` composes prompts in **dry-run** mode by default.
- Live image API generation remains opt-in / unwired in this change set; CI never calls out.
- Do not commit tokens.

## Offline vs telephony (non-goals)

- **Supported offline path:** `tools/elm_offline` snapshots docs/policy, STATUS, BACKLOG, sandboxes manifest, vault READMEs, and completion certificate (when present) into a local cache. Use `snapshot` / `status`.
- **Explicit non-goals / cannot_control:** telephony, radio, satellite, hotspot hardware control. Offline cache is local files only — not a modem or RF controller.

## Related tools

| Concern | Tool |
|---------|------|
| Grok export ingest | `tools/grok_archive` |
| Offline snapshot | `tools/elm_offline` |
| FLUX prompt compose | `tools/elm_flux` |
