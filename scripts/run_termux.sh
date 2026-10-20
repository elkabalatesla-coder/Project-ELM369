#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
REPO_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
CONFIG_FILE=${1:-"$REPO_ROOT/PROJECT_TERMUX.json"}

exec python3 - "$CONFIG_FILE" "$REPO_ROOT" <<'PY'
import json
import os
import re
import subprocess
import sys
from pathlib import Path

config_path = Path(sys.argv[1])
repo_root = Path(sys.argv[2])

try:
    config = json.loads(config_path.read_text(encoding="utf-8"))
except (OSError, json.JSONDecodeError) as exc:
    print(f"[termux-runner] Cannot read config {config_path}: {exc}", file=sys.stderr)
    raise SystemExit(2)
if not isinstance(config, dict):
    print("[termux-runner] Config must contain a JSON object.", file=sys.stderr)
    raise SystemExit(2)

env = os.environ.copy()
configured_env = config.get("env", {})
if not isinstance(configured_env, dict):
    print("[termux-runner] 'env' must be a JSON object.", file=sys.stderr)
    raise SystemExit(2)
for key, value in configured_env.items():
    if not isinstance(key, str) or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", key) or not isinstance(value, str):
        print(f"[termux-runner] Invalid environment entry: {key!r}", file=sys.stderr)
        raise SystemExit(2)
    env[key] = value
    print(f"[termux-runner] Set environment variable {key}")

ignored_dirs = {".git", ".venv", "venv", "__pycache__", "node_modules"}
json_files = (
    path for path in repo_root.rglob("*.json")
    if not any(part in ignored_dirs for part in path.relative_to(repo_root).parts)
)
errors = []
for path in json_files:
    try:
        json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        errors.append(f"{path.relative_to(repo_root)}: {exc}")
if errors:
    print("[termux-runner] Invalid JSON documents:\n" + "\n".join(errors), file=sys.stderr)
    raise SystemExit(1)
print("[termux-runner] JSON validation passed.")

commands = config.get("commands", [])
if not isinstance(commands, list) or any(not isinstance(command, str) for command in commands):
    print("[termux-runner] 'commands' must be an array of strings.", file=sys.stderr)
    raise SystemExit(2)

for command in commands:
    print(f"[termux-runner] Running: {command}", flush=True)
    result = subprocess.run(command, shell=True, cwd=repo_root, env=env)
    if result.returncode:
        print(f"[termux-runner] Command failed with exit code {result.returncode}.", file=sys.stderr)
        raise SystemExit(result.returncode)

print("[termux-runner] Pipeline checks completed.")
PY
