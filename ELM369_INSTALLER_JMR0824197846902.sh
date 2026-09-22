#!/bin/sh
set -eu

CANONICAL="JMR0824197846902"
ALIAS="JMR08241978202646902"
SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"

echo "[ELM369] Local-only installer"
echo "[ELM369] Canonical anchor: $CANONICAL"
echo "[ELM369] Alias anchor: $ALIAS"

test -f "$SCRIPT_DIR/ELM369_VIDEO_PIPELINE_JMR0824197846902.py"

echo "[ELM369] Network installation disabled."
echo "[ELM369] Credentials/secrets/private-key handling disabled."
echo "[ELM369] Running local validation..."

python3 "$SCRIPT_DIR/ELM369_VIDEO_PIPELINE_JMR0824197846902.py"

echo "[ELM369] Local validation completed."
