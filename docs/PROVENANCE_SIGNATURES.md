# Provenance signatures

- `PROJECT_METADATA.json` uses a detached-signature model so the JSON can stay unchanged after review and signing.
- Generate and verify signatures outside this repository with an authorized private key; never commit private keys, passphrases, or other secret signing material.
- If a public key is intentionally published for reviewers, place only the public key material under `vault/public/`.
- Store detached signature artifacts separately from `PROJECT_METADATA.json` and keep temporary signing outputs out of version control.
- GitHub pull request requirements, CODEOWNER review, and direct-push restrictions must be configured in repository branch protection or ruleset settings; `CODEOWNERS` documents ownership but does not enforce those settings by itself.
