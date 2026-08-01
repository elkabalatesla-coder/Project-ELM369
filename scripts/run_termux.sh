#!/usr/bin/env sh
# run_termux.sh — Termux runner for PROJECT_TERMUX.json
# - Uses jq when available to parse JSON, falls back to simple shell parsing.
# - Expected keys in PROJECT_TERMUX.json:
#     env: object of KEY: value
#     commands: array of command strings to run in order

CONFIG_FILE="$(dirname "$0")/../PROJECT_TERMUX.json"
[ -f "$CONFIG_FILE" ] || CONFIG_FILE="PROJECT_TERMUX.json"

have_jq() {
  command -v jq >/dev/null 2>&1
}

load_env_with_jq() {
  jq -r '(.env // {}) | to_entries[] | "\(.key)=\(.value)"' "$1" 2>/dev/null
}

load_commands_with_jq() {
  jq -r '(.commands // [])[]' "$1" 2>/dev/null
}

# Fallback minimal parser for simple JSON (no nested objects, no escaped quotes)
load_env_fallback() {
  awk '/"env"[[:space:]]*:/ {p=1; next} p && /}/ {exit} p {print}' "$1" \
    | sed -n 's/^[[:space:]]*"\([^"[:space:]]\+\)"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1=\2/p'
}

load_commands_fallback() {
  awk '/"commands"[[:space:]]*:/ {p=1; next} p && /]/ {exit} p {print}' "$1" \
    | sed -n 's/^[[:space:]]*"\(.*\)".*/\1/p'
}

echo "[termux-runner] Using config: $CONFIG_FILE"

if have_jq; then
  echo "[termux-runner] Using jq to parse JSON"
  for kv in $(load_env_with_jq "$CONFIG_FILE"); do
    export "$kv"
    echo "[termux-runner] export $kv"
  done
  commands=$(load_commands_with_jq "$CONFIG_FILE")
else
  echo "[termux-runner] jq not found — using fallback parser (limited)"
  for kv in $(load_env_fallback "$CONFIG_FILE"); do
    export "$kv"
    echo "[termux-runner] export $kv"
  done
  commands=$(load_commands_fallback "$CONFIG_FILE")
fi

if [ -z "$commands" ]; then
  echo "[termux-runner] No commands found in config. Exiting."
  exit 0
fi

echo "[termux-runner] Running configured commands..."
# Run each command in a subshell, stop on failure
IFS=$'\n'
for cmd in $commands; do
  echo "[termux-runner] $cmd"
  sh -c "$cmd" || {
    echo "[termux-runner] Command failed: $cmd"
    exit 2
  }
done
echo "[termux-runner] All commands completed."
