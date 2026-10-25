# ELM369 Adaptive Keyboard API Adapter

This package exposes a small standard-library WSGI adapter around the existing command registry and policy gate. It resolves allowlisted commands and records decisions; it does **not** execute generated code.

## Local launch

From the repository root, set a strong local secret and start the adapter:

```sh
export ELM369_API_TOKEN="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"
python -m elm369_adaptive_keyboard.api
```

The server binds only to `127.0.0.1:8769`. Do not bind it to `0.0.0.0` or expose it to the public internet. The token must be sent in an `Authorization: Bearer ...` header. A browser frontend should use a trusted local bridge that keeps the token out of page JavaScript; do not embed the secret in a static HTML file.

## Endpoints

- `GET /health`: basic health status; states that execution is disabled.
- `POST /v1/command`: resolves a registered command or returns a policy decision.
- `GET /v1/audit`: returns the in-memory hash-chained audit events and verification result.

Command body example:

```json
{"command":"/help"}
```

The `/run` route is fail-closed. It requires an artifact manifest, content matching the manifest SHA-256, exact registered capabilities, capability grants, risk-policy approval, and explicit confirmation. Even `READY` only means policy checks passed; an independently reviewed execution adapter would still be required.

## Security boundaries and limitations

- Request body limit 16 KiB; artifact content limit 8 KiB; command length limit 256 characters.
- Unknown routes/commands are denied; JSON and field types are validated.
- The API token is required for command and audit routes. Health is intentionally non-sensitive.
- The audit ledger is in memory and is lost on process restart. It is not a durable audit system.
- This WSGI server is a local development adapter, not a production deployment. Native Android/iOS IME integration, secure browser-to-local authentication bridge, durable audit storage, rate limiting, and sandboxed execution are not implemented.
- Never execute arbitrary code from a keyboard field. Keep production execution disabled until a separately reviewed isolated runner, resource limits, cancellation, and audit persistence are implemented.

## Tests

```sh
python -m unittest -v elm369_adaptive_keyboard.test_api elm369_adaptive_keyboard.test_policy_gate elm369_adaptive_keyboard.test_service
python -m compileall -q elm369_adaptive_keyboard
```
