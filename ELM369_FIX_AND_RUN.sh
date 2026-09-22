#!/bin/sh
set -eu

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
PIPELINE="$SCRIPT_DIR/ELM369_VIDEO_PIPELINE_JMR0824197846902.py"
ALIAS="$SCRIPT_DIR/ELM369_VIDEO_PIPELINE_JMR08241978202646902.py"

echo "[ELM369 FIX] Canonical anchor: JMR0824197846902"
echo "[ELM369 FIX] Alias anchor: JMR08241978202646902"

test -f "$PIPELINE"
echo "[ELM369 FIX] Canonical implementation present."

if command -v python3 >/dev/null 2>&1; then
  python3 -m py_compile "$PIPELINE"
  python3 "$PIPELINE"
else
  echo "[ELM369 FIX] Python 3 is required." >&2
  exit 1
fi

echo "[ELM369 FIX] Local-only validation complete."
