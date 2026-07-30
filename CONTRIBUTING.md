Contributing
============

We use pre-commit hooks to enforce formatting and linting. Please install and run pre-commit locally before making commits.

Install pre-commit and hooks:

    python -m pip install --upgrade pip
    pip install pre-commit
    pre-commit install

Run hooks against all files (useful before opening a PR):

    pre-commit run --all-files

CI will also run ruff, black, and isort on push and pull requests.
