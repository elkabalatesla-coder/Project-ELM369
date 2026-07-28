# auto-amend/engine/README.md

Auto‑Amend Engine (overview)

Purpose
- Collect inbound signals (email/webhook), produce draft PRs or automated amendments, and record auditable events.
- Default mode: generate a draft and require human approval before any repo write.

Components
- Webhook receiver (secure/webhook/handler.py)
- Draft processor (auto-amend/drafts -> reviewed manually or via UI)
- Optional automation: create PRs via GitHub App or gh CLI after manual approval

Environment variables (examples)
- AUTOAMEND_SHARED_SECRET=...   # HMAC secret for webhook verification
- GITHUB_TOKEN=...              # Use a GitHub App or short-lived PAT for automation (only if approved)
- AUTOAMEND_AUDIT_DIR=./security/audit/webhook

Developer run (local)
- python3 -m venv .venv
- source .venv/bin/activate
- pip install -r requirements.txt  # flask
- export AUTOAMEND_SHARED_SECRET="your-secret"
- python secure/webhook/handler.py

Approval flow (recommended)
1. Webhook receives an email -> writes draft and audit record.
2. Human reviewer inspects draft (auto-amend/drafts) and approves via a small script or PR body addition.
3. Approved drafts can be transformed into pull requests using gh/REST API with a scoped token.

Notes on automation
- Keep human_authorization_required = true for production by default.
- Prefer GitHub App for better granularity and auditable tokens.
