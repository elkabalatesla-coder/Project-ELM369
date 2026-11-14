#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail
pkg update -y
pkg install -y python git
python -m elm369 init
python -m unittest discover -s tests -v
python -m elm369 verify
