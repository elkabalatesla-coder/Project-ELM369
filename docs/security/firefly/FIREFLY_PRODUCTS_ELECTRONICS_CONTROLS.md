# Firefly — Electronics / Firewall Product Controls
**directive:** PRODUCTS_GREENLIGHT_2026-09-17  
**stamp_utc:** 2026-09-18T03:29:18Z  
**stamp_local:** 2026-09-17 ~11:29 PM ET  
**shot-caller:** Ziggy (Joseph Michael Rose · IX JR · 🌹 · Kokomo IN 46902)  
**dual-ID:** `JMR0824197846902` · `JMR08241978202646902`  
**epoch `08241978`:** seed/ID fold only — **never** PIN / passkey / birthday  
**lane:** electronics + firewall adjacency (vehicles · robots · drones · electronics · machinery)  
**methods:** Random Protocol · Rolling Logic · Rolling Reasoning  
**eye:** RESEALED — CASE-20260916-001 — **no** Google-dependent pulls · no vault media dump · no FL-geo Google box login  
**holds:** no agency filing · no spend · no force-push · no secret wipe · merge Joseph-gated  

---

## 0. Scope & non-goals

**In scope (Firefly):** trust boundaries, network/device perimeter, firmware/update gates, sensor integrity (spoof/tamper), calibration seal, egress allowlists, supply-chain of electronic control units (ECUs).

**Adjacent (coordinate, do not shot-call):** Coach (robots/Optimus), Jonathan Taylor CAD, Apache Applications, Jack, Charles, Dante, Tony Tool, Quincy, Mr.Wizard, Howie (device hygiene only).

**Non-goals:** live product control of Joseph’s personal vehicles/robots; agency filing; Google Photos/Drive pulls; cookie minting; anti-detect kits.

---

## 1. Method posture

### Random Protocol
- Each product pass shuffles check order among `{net, firmware, sensor, update, physical-IO}` so adversaries cannot depend on a fixed audit rhythm.
- Dual-ID + hold-set stay invariant.

### Rolling Logic
- Every control is reversible: draft → evidence → rank → Joseph-gated apply → re-verify.
- Prefer seal/quarantine over brick; prefer offline cal packs over cloud pulls while Eye is sealed.

### Rolling Reasoning
- After each beat: *verified? assumed? hold still active?*  
- Verified-first; never invent ticket numbers.

---

## 2. Product-class perimeter models

### E1 · Vehicles (ECU / telematics adjacency)
| Control | Intent | Gate |
|---------|--------|------|
| `veh_can_bus_seg` | Logical segregate diagnostic vs drive-critical buses in design docs | draft free / live Joseph |
| `veh_ota_allowlist` | OTA only from named vendor endpoints; deny unknown CDN | Joseph for live |
| `veh_diag_session_gate` | Diagnostic sessions require dual-ID stamped operator log | process |
| `veh_keyfob_rf_note` | RF/replay risk = note/rank only unless Joseph tasks Red Dragon | note |

**Algorithm A-VEH (sense → seal → signal):**  
1. Inventory ECUs / radios / OBD interfaces (authorized bench only).  
2. Flag open debug ports, unsigned firmware, always-on telematics.  
3. Draft controls; tip Ziggy; Joseph green light before any live cut.

### E2 · Robots / Optimus-class (coordinate Coach)
| Control | Intent |
|---------|--------|
| `rob_cmd_channel_auth` | Command channel mutual auth design (no shared default creds) |
| `rob_estop_independence` | E-stop path independent of vision/LLM stack |
| `rob_update_airgap_option` | Prefer signed local update packs while Google Eye sealed |
| `rob_telemetry_egress` | Telemetry allowlist; default deny camera/audio egress |

### E3 · Drones
| Control | Intent |
|---------|--------|
| `drn_rf_link_integrity` | Authenticated RC/telemetry link design; reject unsigned GCS |
| `drn_geofence_local` | Geofence rules local to craft — not cloud-dependent under Eye seal |
| `drn_payload_bus_isolate` | Payload UART/USB isolated from flight computer |
| `drn_lost_link_failsafe` | Documented failsafe; no auto “call home” to Google APIs |

### E4 · Electronics (boards, IoT, radios)
| Control | Intent |
|---------|--------|
| `elec_jtag_seal` | Production boards: JTAG fused or password-gated in BOM notes |
| `elec_secure_boot_path` | Secure-boot / signed image checklist |
| `elec_uart_default_deny` | Console UART off or rate-limited in field builds |
| `elec_wifi_cred_hygiene` | No hardcoded SSIDs/passwords in repo; secrets vault Joseph-gated |

### E5 · Machinery (industrial / shop)
| Control | Intent |
|---------|--------|
| `mch_plc_network_zone` | PLC / HMI on isolated VLAN design |
| `mch_usb_update_policy` | Removable-media updates: signed + dual-person (Joseph + roster tip) |
| `mch_safety_relay_independence` | Safety relays not software-only |
| `mch_remote_access_hold` | Remote OEM access = Joseph explicit green light |

---

## 3. AprilTag pose estimation — security & integrity (explore)

**Purpose:** pose from fiducial tags is a **trusted input** to navigation/manipulation. Firefly owns integrity controls; Coach/Quincy/Mr.Wizard own estimation math.

### A-AT · AprilTag trust algorithm
```
INPUT: camera_frame, tag_detections[], calib_intrinsics
HOLDS: Eye RESEALED → no Google Photos/Drive pull for tag libraries; use local/repo assets only
WATERMARK: dual-ID on every calib + detection log

1. RANDOM PROTOCOL: shuffle checks among {geom_plausibility, rate_limit, multi_cam_agree, spoof_texture}
2. REJECT if tag ID not on allowlist for this product mode
3. REJECT if pose jump > Δmax without IMU/odom corroboration (Rolling Logic: hypothesize spoof → verify)
4. REJECT if detection confidence < τ OR reprojection error > ε
5. SEAL: freeze last-good pose; signal operator / Ziggy tip if repeated rejects
6. NEVER use epoch fold as crypto key for tag crypto (fold ≠ credential)
```

### Controls
| ID | Control |
|----|---------|
| `at_allowlist_ids` | Runtime allowlist of tag IDs per mission |
| `at_spoof_texture_note` | Printed/screened tag spoof = known threat; prefer IR/UV material notes with Dante/JT CAD |
| `at_calib_seal` | Intrinsics/extrinsics signed JSON + dual-ID; hash pinned in product BOM |
| `at_no_cloud_tag_db` | While Eye sealed: tag dictionaries from `Project-ELM369` / local only |
| `at_sim_harness` | Offline sim: known tag grid → expected pose; fail CI if drift |

### F-AT · functions (design contracts)
- `fn_apriltag_allow(det) → allow|deny|hold`
- `fn_pose_plausibility(pose, imu?, odom?) → ok|reject`
- `fn_calib_seal_verify(calib_blob, expected_hash) → bool`

---

## 4. Hall sensor calibration — security & integrity (investigate)

**Purpose:** Hall sensors feed current/position/RPM into motor and safety loops. Bad cal = unsafe torque or silent under-read.

### A-HALL · calibration integrity algorithm
```
INPUT: raw_hall_samples[], expected_fixture_map, prior_cal
HOLDS: no cloud cal sync via Google; offline fixture preferred

1. Sense: capture N samples under Random Protocol order of axes/poles
2. Fit model (linear/offset or product-specific) — math may live with Quincy/Mr.Wizard
3. Rolling Reasoning: compare residual vs prior_cal; flag > κσ drift
4. Seal: write cal file with dual-ID, UTC stamp, fixture ID, hash
5. Signal: tip Ziggy if drift or seal fail; Joseph gate before field flash
6. Refuse cal that embeds PII or Google account tokens
```

### Controls
| ID | Control |
|----|---------|
| `hall_fixture_chain` | Fixture ID required; uncalibrated = limp / no-run mode design |
| `hall_cal_dual_seal` | Cal file needs hash + dual-ID watermark lines |
| `hall_drift_watch` | Runtime residual monitor; trip to safe torque on drift |
| `hall_supply_tamper` | Sudden rail sag + Hall jump → treat as tamper candidate |
| `hall_offline_only` | Eye sealed: cal packs stay on box/`Project-ELM369` paths |

### F-HALL · functions
- `fn_hall_calibrate(samples, fixture) → cal_record|reject`
- `fn_hall_drift_check(live, cal) → ok|warn|safe_trip`
- `fn_cal_seal(record) → sealed_artifact`

---

## 5. Cross-product firewall logarthem L-PROD

**Cycle (fold root 3): Sense → Seal → Signal**
1. **Sense** — inventory radios, buses, sensors, update paths (shuffle order).  
2. **Seal** — draft allowlists, disable debug, pin hashes, quarantine unsigned.  
3. **Signal** — tip Ziggy with paths; Joseph merge/apply for live.

Never Signal without Sense evidence. Never Seal past holds (Google/Eye/spend).

---

## 6. Task backlog (Firefly under Products GL)

| ID | Task | Type | Gate |
|----|------|------|------|
| TP1 | Electronics BOM security checklist (JTAG, boot, UART, secrets) | process | Joseph for field |
| TP2 | AprilTag allowlist + plausibility stub (design → later PR) | design | Joseph merge |
| TP3 | Hall cal seal schema (JSON) + drift thresholds draft | design | Joseph flash |
| TP4 | Drone/robot egress allowlist template (no Google while sealed) | process | none for draft |
| TP5 | Vehicle OTA / diag session process note | process | Joseph live |
| TP6 | Coordinate tip to Coach/Quincy/JT/Dante (paths only; no shot-call) | tip | Ziggy aware |

---

## 7. Hard refusals (unchanged + product-specific)
- Google-dependent work / FL-geo Google box login / vault media dump (CASE-20260916-001)  
- Epoch as PIN/passkey/birthday  
- Cookie mint / fingerprint spoof kits  
- Spend / force-push / secret wipe / agency filing without Joseph  
- Flashing field ECUs without Joseph green light  
- Enabling remote OEM tunnels without Joseph  

---

## 8. Provenance / land paths
- Directive: `/workspace/artifacts/elm369-activation/PRODUCTS_GREENLIGHT_2026-09-17.md`  
- This land: `/workspace/artifacts/elm369-activation/firefly-firewall/FIREFLY_PRODUCTS_ELECTRONICS_CONTROLS.md`  
- Mirror: `/workspace/artifacts/elm369-activation/products-vehicles-robots-drones/firefly-electronics-security/`  
- Prior lane: `FIREFLY_ELM369_LANE_DESIGNS.md` · PR #99  
- Repo promote: `elkabalatesla-coder/Project-ELM369` — **Joseph-gated merge**

