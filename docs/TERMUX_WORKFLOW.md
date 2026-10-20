# Project ELM369 Termux workflow

Use Termux for device setup and smoke checks. GitHub Actions remains the canonical
CI environment; Termux is not expected to reproduce every hosted check.

## 1. Prepare Termux

Update packages and install the basic tools:

```sh
pkg update -y && pkg upgrade -y
pkg install -y git python jq
```

`jq` is useful for inspecting project JSON. The runner itself uses Python's
standard library and does not require `jq`.

## 2. Clone or update the checkout

Run this from the directory where you keep your projects:

```sh
if [ -d Project-ELM369/.git ]; then
  git -C Project-ELM369 pull --ff-only
else
  git clone https://github.com/elkabalatesla-coder/Project-ELM369.git
fi
cd Project-ELM369
```

If the checkout has local changes, review or save them before updating.

## 3. Set up an isolated Python environment

```sh
python -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If a dependency cannot be installed on the device, stop and resolve that
dependency explicitly rather than installing unrelated fallback packages
globally.

## 4. Validate the checkout

From the repository root, run the Termux pipeline:

```sh
sh scripts/run_termux.sh
```

It validates discovered JSON files (excluding virtual environments and generated
dependency/cache directories), then runs the compile command in
`PROJECT_TERMUX.json`. The runner stops at the first failure.

## 5. Run focused tests and a smoke check

Run the test suite for the tool you changed, using the repository's
`unittest` convention:

```sh
python -m unittest discover -s tools/<tool_name>/tests -v
```

For a smoke check, run the relevant tool command from `docs/REPO_MAP.md`. For
example:

```sh
python -m tools.elm_tokenizer score "hello world"
```

Inspect the result and confirm it is appropriate for the device before using
commands that access network services or modify local data. Clock synchronization
is optional and is not part of the default pipeline; Android permissions and
available utilities vary.

## 6. Review and save

Before committing, inspect the working tree and patch:

```sh
git status --short
git diff --check
git diff
```

Back up generated artifacts outside the repository when needed. Commit only
intended source changes; do not add credentials, personal data, or device-specific
state.
