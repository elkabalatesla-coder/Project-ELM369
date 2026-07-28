# gmail/setup/README.md

This guide explains options to forward Gmail messages to the Auto‑Amend webhook.

Option A — Google Apps Script (recommended for simple forwarding)
1. In Gmail, create a new Label (e.g., "AutoAmend") and setup filters to apply the label to messages you want to forward.
2. In Google Apps Script (https://script.google.com), create a new project and add a script that watches labeled messages and POSTs to the webhook URL.
3. Use Script Properties to store the webhook URL and a signing secret.
4. Example Apps Script: https://developers.google.com/apps-script/guides/triggers

Option B — Gmail API (server-side)
1. Create a Google Cloud project, enable Gmail API, and create OAuth credentials (web app or service account with domain-wide delegation if available).
2. Use the Gmail API to watch or list messages and forward selected messages to the webhook.
3. Secure: sign requests to the webhook with the shared secret using HMAC-SHA256 in header X-Hub-Signature-256.

Security notes
- Do NOT embed webhook URL or secrets into public code or client-side scripts.
- Use HTTPS with a valid certificate for webhook endpoints.
- Use a rotating secret or signed JWTs for authentication where possible.
