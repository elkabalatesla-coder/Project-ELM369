# ELM369 QBIT / QSTATE Design Notes v0.1.0

Project: ELM369_JMR08241978202646902  
Status: Design scaffolding (from archived `elkabalatesla-coder-ELM369_Qbit` intent)  
Related: `docs/architecture/ELM369_AUTOMATED_EVOLUTION_SPEC_v1.0.0.md`

## Purpose

Define a **decision evidence layer** for ELM369 that scores confidence and risk without bypassing safety, authority, or provenance gates.

A high QSTATE must never alone authorize production mutation, credential change, destructive deletion, or physical actuation.

## Definitions

### QBIT

A single decision packet: evidence, confidence, impact, and risk inputs that feed a scored recommendation.

Fields (conceptual):

| Field | Meaning |
|-------|---------|
| `qbit_id` | Stable id for this decision packet |
| `subject` | What is being decided (change, repair, integrate, …) |
| `evidence` | Observations / artifacts supporting the case |
| `confidence` | 0–1 belief the evidence is sound |
| `impact` | Expected benefit if ALLOW |
| `risk` | Expected harm if wrong |
| `recommendation` | ALLOW, ALLOW_WITH_LIMITS, MODIFY, DEFER, REQUEST_AUTHORIZATION, HANDOVER, QUARANTINE, ABORT, EMERGENCY |

### QSTATE

Composite score (from evolution spec):

```
QSTATE = 0.40L + 0.25M + 0.20R + 0.15H
```

| Term | Working meaning (v0.1) |
|------|------------------------|
| **L** | Likelihood / evidence strength |
| **M** | Magnitude of beneficial impact |
| **R** | Readiness (tests, rollback, provenance present) |
| **H** | Harm inverse — higher when residual risk is lower |

Each term is normalized to **0.0–1.0** before weighting.

## Separation of concerns (hard rule)

Keep these layers separate in code and policy:

1. **Scoring** — computes QSTATE / recommendation hints
2. **Policy** — evolution operations and gates
3. **Authority** — who may approve what
4. **Safety governor** — hard stops (destructive, credentials, actuation)

A score is an input to policy, never a bypass.

## Decision outcomes

Reuse the evolution-spec set:

`ALLOW` · `ALLOW_WITH_LIMITS` · `MODIFY` · `DEFER` · `REQUEST_AUTHORIZATION` · `HANDOVER` · `QUARANTINE` · `ABORT` · `EMERGENCY`

## Minimal workflow

1. Collect evidence → build QBIT
2. Compute QSTATE terms and weighted score
3. Map score + hard constraints → recommendation
4. Run mandatory gates (schema, tests, safety, authorization)
5. Act only if gates pass; otherwise DEFER / REQUEST_AUTHORIZATION / ABORT

## Machine-readable contract

See `schemas/qbit/qbit.schema.json` and example instance `schemas/qbit/examples/qbit.example.json`.

## Non-goals (v0.1)

- No quantum hardware claims
- No autonomous production deploy from QSTATE alone
- No credential or destructive operations from this layer
