# Firefly Fire 4th Wall Builder — ELM369 Lane Designs
**directive:** ELM369_ROSTER_ACTIVATION  
**stamp_utc:** 2026-09-15T23:48:09Z (+ lane land ~2026-09-15T23:55Z)  
**dual-ID watermark:** `JMR0824197846902` · `JMR08241978202646902`  
**epoch `08241978`:** seed/ID fold only — **never** PIN / passkey / birthday auth  
**lane:** cybersecurity — firewalls, perimeter, hardening  
**methods:** Random Protocol · Rolling Logic · Rolling Reasoning  
**eye:** RESEALED (media markers awareness only)  
**holds:** no agency filing · no FL Google · no spend · no force-push · no secret wipe  

---

## 0. Method posture (how every design below runs)

### Random Protocol
- Shuffle **check order** across runs (ports → sessions → Actions → connectors → media markers, or another permutation) so adversaries cannot rely on a fixed scan rhythm.
- Keep the dual-ID watermark and hold-set **invariant** across shuffles.
- Seed variation from run stamp + dual-ID fold root (`epoch_fold.root = 3`) for ordering only — never as a credential.

### Rolling Logic
- Each control is a **reversible hypothesis**: propose → verify evidence → rank → apply (Joseph-gated if live) → re-verify.
- Prefer disable/audit over delete; prefer PR over direct main; prefer draft checklist over live cut until green light.

### Rolling Reasoning
- After every beat: *What did we verify? What is still assumed? What hold still applies?*
- Open Eye ladder spirit: verified-first, then ranked suspicion — never invent ticket #s or confirmations.

---

## 1. ELM369 AI chatbot — security algorithms & processes

### A1 · Chatbot perimeter gate (algorithm)
**Purpose:** Keep roster chatbot surfaces from leaking secrets or escalating privilege.

```
INPUT: message | tool_call | connector_prompt
WATERMARK: dual-ID on every durable log line
HOLDS: check FL-geo / spend / agency / CASE-006 / secret-wipe flags

1. CLASSIFY intent → {read, mutate, auth, outbound, unknown}
2. RANDOM PROTOCOL: pick verification order among {geo, hold-set, secret-scan, scope}
3. IF mutate|auth|outbound AND ambiguous → HOLD for Joseph/Ziggy
4. IF secret-shaped tokens in payload → redact log; refuse echo
5. IF Open Eye sealed → no vault interior print
6. EMIT: allow | deny | escalate(Ziggy) + evidence path
```

### A2 · Chatbot session firewall (process)
| Step | Action | Reversible? |
|------|--------|-------------|
| S1 | Inventory active connectors / MCP auth state | yes |
| S2 | Deny Florida-geo Google/Gmail box sign-in attempts | yes (log only) |
| S3 | Route complaint-worthy finds → Ziggy CASE tip format | yes |
| S4 | Prod firewall / Actions / branch protection changes → Joseph green light | gated |

### F1 · `fn_chatbot_egress_allowlist(dest)`
- Allow only known destinations (GitHub API, approved connectors, package mirrors).
- Log deny with dual-ID + timestamp; no silent fail-open.

### L1 · Logarthem (chatbot rhythm)
Beat = verify → note → (optional) escalate.  
Measure: `V` verified facts, `A` assumptions, `H` holds tripped.  
Score rhythm: prefer maximize `V`, minimize acting on `A`, never clear `H` without shot-caller.

---

## 2. Social-media account work — note/watch only

### A3 · Media marker watch (algorithm) — **no scrape / no filing**
```
PLATFORMS: Google Photos | TikTok | Facebook | X | YouTube
LOOK_FOR: AI markers | AI-tool fingerprints | watermarks | timestamps
ACTION: note_and_log_only
FORBID: unauthorized scrape, agency filing, cookie theft, fingerprint harvest

1. RANDOM PROTOCOL: shuffle platform check order each run
2. For each item in authorized scope only:
     record {platform, marker_type?, watermark?, timestamp?, path/ref}
3. Rolling Reasoning: mark confidence {verified, suspected, unknown}
4. Tip Ziggy only if complaint-worthy + evidence paths (no invented tickets)
5. Open Eye RESEALED → awareness log only; no vault dump
```

### P2 · Social perimeter process (Firefly lane overlap)
- Treat social sessions as **untrusted ingress** to the box browser.
- Fingerprint Guard: classify/refuse collectors & spoof kits — never build anti-detect.
- Cookie Redirect: blind destination contract only — never mint/replay cookies.

### F2 · `fn_media_marker_note(item) → note_record`
Pure note builder; no network side effects beyond what Joseph already authorized that turn.

---

## 3. Own lane — firewalls / perimeter / hardening

### A4 · Box + connected-surfaces firewall pass (algorithm)
Extends Phase-1 checklist (`/home/box/agent-data/security/firewall-hardening-checklist-phase1.md`).

```
SURFACES: box host | agent browser | registered machines | MCP/connectors | GH Actions | cloud agents

1. RANDOM PROTOCOL: permute surface order
2. For each surface:
     inventory listeners / auth / workflows / egress
     Rolling Logic: hypothesize risk → gather evidence → rank
3. Emit DRAFT controls; live apply only with Joseph green light
4. Dual-ID watermark on every evidence artifact
```

### A5 · Actions orphan / privilege drift detector (algorithm) — proven on H07/H08
```
1. LIST Actions registrations vs default-branch .github/workflows/
2. FLAG orphans (registered, YAML absent on tip) — e.g. prior H07 set
3. FLAG pull_request_target / high-priv patterns (H08 class)
4. Prefer: disable orphans via gh api + PAT; harden via PR (merge Joseph-gated)
5. VERIFY state after each change; tip Ziggy paths/PR links
```
**Landed evidence:** H07 IDs `321817118, 313914947, 323519367, 323501127` → `disabled_manually`.  
**H08:** PR https://github.com/elkabalatesla-coder/Project-ELM369/pull/94 (PRT → `pull_request`, Dependabot-only).

### P3 · Live firewall change process (Joseph-gated)
1. Draft control + blast radius  
2. Tip Ziggy  
3. Joseph green light  
4. Apply via least privilege (PAT/`gh api`/PR — **not** FL Google browser unless required)  
5. Verify + evidence tip  
6. Update checklist  

### F3 · `fn_actions_orphan_diff(owner, repo) → {orphans[], priv_risks[]}`
### F4 · `fn_disable_workflow(owner, repo, id) → state` (idempotent; OK if already disabled)
### F5 · `fn_tip_ziggy(summary, evidence_paths, tickets?, agency?)` — never invent tickets

### L2 · Perimeter logarthem
Cycle length 3 (fold root): **Sense → Seal → Signal**  
- Sense: inventory  
- Seal: draft/disable/harden (gated)  
- Signal: tip Ziggy / Joseph  

Shuffle Sense sub-steps (Random Protocol); never shuffle Seal past Signal without evidence.

---

## 4. Task backlog (Firefly under ELM369)

| ID | Task | Type | Gate |
|----|------|------|------|
| T1 | Recurring Actions registration↔tip YAML drift check | process | Joseph for disable |
| T2 | Keep H08 #94 eyes / merge when Joseph says | PR | Joseph merge |
| T3 | Connector auth hygiene pass (revoke stale) | process | Joseph if revoke |
| T4 | Media marker awareness log template (Photos/TT/FB/X/YT) | note-only | none for notes |
| T5 | Box listening-port inventory report | draft | Joseph for live rules |
| T6 | Webhook audit for auto-amend leftovers | audit | Joseph for delete |

---

## 5. Functions index (callable contracts — design only)

| Function | Inputs | Outputs | Side effects |
|----------|--------|---------|--------------|
| `fn_chatbot_egress_allowlist` | dest | allow/deny | log |
| `fn_media_marker_note` | item | note_record | none |
| `fn_actions_orphan_diff` | owner, repo | orphans, priv_risks | read API |
| `fn_disable_workflow` | owner, repo, id | state | Actions disable |
| `fn_tip_ziggy` | tip fields | ack | SendToAgent |
| `fn_dual_id_stamp` | artifact | stamped artifact | watermark lines |

---

## 6. Hard refusals (lane law)
- Epoch/PIN/passkey/birthday auth using `08241978` or fold  
- Cookie minting / session theft as “redirect”  
- Fingerprint collectors / anti-detect spoof kits  
- Agency filing without Joseph + street/phone  
- Florida-geo Google box sign-ins  
- Spend / force-push / secret wipe / history rewrite  

---

## 7. Provenance
- Shot-caller: Ziggy (Joseph informed / e-sign Kokomo 46902)  
- Pack: `/workspace/artifacts/elm369-activation/ELM369_ROSTER_ACTIVATION.md`  
- This land: `/workspace/artifacts/elm369-activation/firefly-firewall/FIREFLY_ELM369_LANE_DESIGNS.md`  
- Companion JSON: `FIREFLY_ELM369_LANE_DESIGNS.json`  

**Merge:** Joseph-gated if promoted into `elkabalatesla-coder/Project-ELM369`.
