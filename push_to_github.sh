#!/usr/bin/env bash
set -euo pipefail

# --- PROJECT ELM369 GITHUB AUTO-PUSH SCRIPT ---
PRIMARY_ID="JMR0824197846902"
COMPANION_ID="JMR08241978202646902"

if (( $# > 1 )); then
    echo "Usage: $0 [commit message]" >&2
    exit 1
fi

echo "=================================================="
echo "[ELM369] Initializing Git Push Pipeline..."
echo "Primary ID: $PRIMARY_ID"
echo "Companion ID: $COMPANION_ID"
echo "=================================================="

cd -- "$(dirname -- "${BASH_SOURCE[0]}")"

if [[ ! -e .git ]]; then
    echo "[*] Initializing local Git repository..."
    git init
    git branch -M main
fi

if ! BRANCH=$(git symbolic-ref --quiet --short HEAD); then
    echo "[!] Detached HEAD: check out a branch before running this script." >&2
    exit 1
fi

if ! git var GIT_AUTHOR_IDENT >/dev/null || ! git var GIT_COMMITTER_IDENT >/dev/null; then
    echo "[!] Configure your Git user.name and user.email before running this script." >&2
    exit 1
fi

if ! git remote get-url origin >/dev/null 2>&1; then
    echo "[!] No remote 'origin' found."
    read -r -p "Enter your GitHub repository URL: " REPO_URL
    if [[ -z "$REPO_URL" ]]; then
        echo "[!] Repository URL must not be empty." >&2
        exit 1
    fi
    git remote add origin "$REPO_URL"
fi

git add --all
COMMIT_MSG="${1:-ELM369 Automated Termux Pipeline Sync - $(date +'%Y-%m-%d %H:%M:%S')}"

if git diff --cached --quiet; then
    echo "[*] No staged changes; pushing existing commits."
else
    DIFF_STATUS=$?
    if [[ "$DIFF_STATUS" -ne 1 ]]; then
        exit "$DIFF_STATUS"
    fi
    git commit -m "$COMMIT_MSG [IDs: $PRIMARY_ID, $COMPANION_ID]"
fi

echo "[*] Pushing to GitHub ($BRANCH)..."
git push -u origin "refs/heads/$BRANCH:refs/heads/$BRANCH"

echo "=================================================="
echo "[ELM369] Push sequence completed successfully."
echo "=================================================="
