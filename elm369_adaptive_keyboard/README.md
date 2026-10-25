# ELM369 Adaptive Keyboard Policy Modules

Python 3.8+, standard library only. These modules provide a strict allowlist command registry, fail-closed artifact policy decisions, and an in-memory SHA-256 chained audit ledger. They do not execute artifacts.

From the repository root, run:

```bash
python -m unittest -v elm369_adaptive_keyboard.test_policy_gate
```

`READY` means policy checks passed; it is **not** an execution signal. A separately reviewed execution adapter must verify isolation, resource limits, runtime identity, and cancellation before running a registered artifact. The current ledger is in-memory and is not a durable evidence store.


## Command orchestration boundary

`KeyboardCommandService.request()` is the UI-facing orchestration seam. It resolves slash commands through the allowlist, audits unknown commands, and routes the demo-run command through the fail-closed policy gate. It returns `READY` only after manifest/hash/capability/risk/confirmation checks; it still does **not** execute code. An HTTP/API adapter can wrap this class after authentication, request validation, rate limiting, and durable audit storage are designed.

Run all package tests:

```bash
python -m unittest -v elm369_adaptive_keyboard.test_policy_gate elm369_adaptive_keyboard.test_service
```
