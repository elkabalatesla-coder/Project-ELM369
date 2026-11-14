# Project ELM369 — Termux Build v0.2.0

P1 Intelligence Engine added on top of an isolated, local-first Termux foundation.
This is a separate versioned implementation layer; it does not alter the canonical
GitHub repository or any immutable ELM369 baseline.

## Install / upgrade

```bash
pkg update && pkg upgrade -y
pkg install python git -y
mkdir -p ~/projects
cd ~/projects
# Put elm369_termux_v0.2.0.tar.gz in Downloads, then:
termux-setup-storage
cp ~/storage/downloads/elm369_termux_v0.2.0.tar.gz .
tar -xzf elm369_termux_v0.2.0.tar.gz
cd elm369_termux_v0.2.0
python -m elm369 init
python -m elm369 status
python -m elm369 verify
python -m unittest discover -s tests -v
```

Workspace defaults to `~/.elm369`; override with `ELM369_HOME=/path`.

## P1 commands

```bash
python -m elm369 analyze --claim "Example claim" --evidence 0.8 --confidence 0.7 --impact 0.6 --risk 0.2
python -m elm369 workflow --observation "Observed event" --evidence "log.txt"
python -m elm369 random --seed 369 --count 5
python -m elm369 registry
```

Random Protocol is **disabled by default**. The `random` command is an explicit,
local simulation request; it requires a seed for replayability and does not change
the project-wide default. It is not a cryptographic random generator.

## P1 models

- QBIT = Evidence×0.40 + Confidence×0.25 + Impact×0.20 − Risk×0.15
- QSTATE = Logic×0.40 + Learning×0.25 + Exploration×0.20 + Memory×0.15
- Inputs are normalized to [0, 1]. These are project scoring heuristics, not
  scientifically validated probabilities or quantum-state measurements.
- Workflow: Observe → Understand → Investigate. The engine records missing evidence
  and unresolved questions; it does not invent facts or autonomously authorize actions.

## Integrity and safety

SHA-256 checks detect accidental or unauthorized content changes relative to the
stored manifest. They do not prove authorship, identity, or legal ownership.
No credentials, network calls, external APIs, financial transactions, or destructive
repository operations are included.
