#!/usr/bin/env bash
# security/playbooks/blacklist_api_curl.sh
# Usage: IDAM_API_URL=https://idam.example.com/api/v1/blacklist IDAM_API_TOKEN=... ./blacklist_api_curl.sh
set -euo pipefail
API_URL="${IDAM_API_URL:-https://idam.example.com/api/v1/blacklist}"
TOKEN="${IDAM_API_TOKEN:-}"
if [ -z "$TOKEN" ]; then echo "Set IDAM_API_TOKEN"; exit 1; fi
curl -sS -X POST "$API_URL" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"project_id":"ELM369","node_identifier":"JMR0824197846902","reason":"Legacy identity node decommissioned — compromised/inactive","action":"blacklist"}'
