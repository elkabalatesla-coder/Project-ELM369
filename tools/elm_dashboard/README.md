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
# Research and outreach workspace

The existing dashboard also provides a local, read-only outreach portal:

```bash
cd /home/runner/work/Project-ELM369/Project-ELM369
python3 -m tools.elm_dashboard outreach
python3 -m tools.elm_dashboard outreach --format html > /tmp/elm369-outreach.html
```

Open `/tmp/elm369-outreach.html` in a browser. It contains an initial shortlist
covering universities, research labs, engineering vendors, and charities, with
tailored drafts and links to organization sites. This is not an exhaustive list.
The source directory is
`/home/runner/work/Project-ELM369/Project-ELM369/data/registries/elm369_outreach.json`.
The portal is generated on demand; it does not save edits, approvals, receipts,
or conversation history.

Research is preliminary: direct page retrieval was blocked by DNS/network
restrictions. The Purdue contact URL was surfaced in search; other links are
homepage leads, not verified contact endpoints. Verify each current route,
eligibility, and terms before use. Opening a link does not establish communication.
No clinical, emergency, or trafficking-reporting channels should receive project
outreach. No repository files, personal details, or draft payloads are transmitted
automatically. The portal has no embedded scripts, remote assets, or submit forms.

Every draft remains unapproved and unsent. Before any manual submission, obtain
approval of the exact recipient, message, sender name, and reply address. Retain
the submission receipt privately and distinguish submitted, acknowledged,
responded, and agreed-partnership states. The project identifiers do not prove
affiliation, accreditation, charity endorsement, or research validation.

For the academic inquiry track, request public teaching references and independent
review of workspace boundaries, singularities, floating-point error, and PID
discretization. For vendors, ask about training, simulator access, licensing, and
hardware safety limits. For charities, ask about approved giving routes, research
designation, fundraising requirements, and name/logo permissions. The 1% model
is not a pledge, transfer, donation receipt, or accounting system.

Public hosting, authentication, persistent correspondence storage, external account
access, and automated delivery are **not configured**. A live collaboration portal
requires the operator to select a hosting domain, access policy, authorized sender
and reply address, approved recipients/messages, and data-retention policy before
deployment. Never commit credentials, personal contact details, or private replies.
