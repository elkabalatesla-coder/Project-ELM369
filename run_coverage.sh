#!/usr/bin/env bash
# Project ELM369 — local pytest + branch coverage
# Canonical: JMR0824197846902
# Companion: JMR08241978202646902

set -Eeuo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPORT_DIR="${REPORT_DIR:-htmlcov}"
COVERAGE_THRESHOLD="${COVERAGE_THRESHOLD:-80}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

cd "$ROOT_DIR"

printf '%s\n' "=============================================================="
printf '%s\n' "Project ELM369 — Pytest / Coverage"
printf '%s\n' "Canonical ID: JMR0824197846902"
printf '%s\n' "Companion ID: JMR08241978202646902"
printf '%s\n' "Coverage threshold: ${COVERAGE_THRESHOLD}%"
printf '%s\n' "=============================================================="

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "[ERROR] Python interpreter not found: $PYTHON_BIN" >&2
  exit 127
fi

if ! "$PYTHON_BIN" -c 'import pytest, pytest_cov, coverage, openapi_spec_validator' >/dev/null 2>&1; then
  echo "[ERROR] Test dependencies are missing." >&2
  echo "Install the pinned toolchain with:" >&2
  echo "  $PYTHON_BIN -m pip install -r requirements-ci.txt" >&2
  exit 2
fi

if [[ ! "$COVERAGE_THRESHOLD" =~ ^[0-9]+([.][0-9]+)?$ ]]; then
  echo "[ERROR] COVERAGE_THRESHOLD must be a numeric percentage." >&2
  exit 2
fi

rm -f .coverage coverage.xml
rm -rf "$REPORT_DIR"

echo "[1/3] Validating the OpenAPI 3.1 contract..."
"$PYTHON_BIN" -m openapi_spec_validator docs/openapi/elm369-openapi.yaml

echo "[2/3] Running tests and measuring line + branch coverage..."
"$PYTHON_BIN" -m pytest \
  -v \
  --cov \
  --cov-branch \
  --cov-report=term-missing \
  --cov-report="html:${REPORT_DIR}" \
  --cov-report=xml:coverage.xml \
  --cov-fail-under="$COVERAGE_THRESHOLD"

echo "[3/3] Coverage reports generated:"
echo "  HTML: $REPORT_DIR/index.html"
echo "  XML:  coverage.xml"

REPORT_PATH="$ROOT_DIR/$REPORT_DIR/index.html"
if [[ "${CI:-}" == "true" || "${NO_BROWSER:-0}" == "1" ]]; then
  exit 0
fi

if command -v xdg-open >/dev/null 2>&1; then
  xdg-open "$REPORT_PATH" >/dev/null 2>&1 &
elif command -v termux-open >/dev/null 2>&1; then
  termux-open "$REPORT_PATH" >/dev/null 2>&1 &
elif command -v open >/dev/null 2>&1; then
  open "$REPORT_PATH" >/dev/null 2>&1 &
elif command -v cmd.exe >/dev/null 2>&1; then
  cmd.exe /c start "" "$(cygpath -w "$REPORT_PATH")" >/dev/null 2>&1 &
else
  echo "[INFO] No supported browser launcher found; open $REPORT_PATH manually."
fi
