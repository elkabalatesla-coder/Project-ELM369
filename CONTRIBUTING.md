Auto-merge & repository permissions

To allow auto-merge for Dependabot or automated-fix PRs:

- Enable auto-merge:
  - Settings → Merge button → enable "Allow auto-merge" for the repository.
- Workflow permissions:
  - GitHub Actions workflows that programmatically enable auto-merge must run with a token that has write permission for pull requests.
  - Go to Settings → Actions → General → Workflow permissions and ensure "Read and write permissions" is set for workflows that need to modify pull requests.
  - If your organization restricts the default GITHUB_TOKEN, you can create a Personal Access Token (PAT) with `repo` scope and add it to repository secrets (recommended secret name: `AUTO_MERGE_PAT`).
- Branch protection:
  - Branch protection rules may block auto-merge if required checks or approvals are missing. Make sure required status checks are configured and stable.
  - If you want automated dependency updates to auto-merge, consider creating an exception for Dependabot or allowing specific required checks to be skipped for dependabot PRs where appropriate.
- Dependabot PRs and automated-fix PRs:
  - Dependabot PRs are created by dependabot[bot]. This repository enables an Action to attempt auto-merging Dependabot and PRs labelled `auto-fix` or `dependabot` when they are opened, labeled, or updated.
  - Maintainership: maintainers should still review dependency updates. The workflow only attempts to enable auto-merge when PRs meet the author/label criteria; it will not bypass branch protection or required checks.

Notes about this repository
- Backports.zoneinfo compatibility:
  - This repository includes backports.zoneinfo in pyproject.toml and requirements.txt to provide compatibility for Python < 3.9.
  - A helper module was added at tools/timezone.py that provides a ZoneInfo fallback for older Python versions. Import with:

    from tools.timezone import get_timezone

    tz = get_timezone()  # defaults to America/Indiana/Indianapolis

- Automation caveats:
  - Programmatic enabling of auto-merge from a GitHub Action can fail if repository or organization permissions restrict the workflow token. Confirm Workflow permissions and required access before relying on automation.
  - If the workflow fails to enable auto-merge, check the Actions logs for errors and verify that the GITHUB_TOKEN or PAT used has the repo permissions required.

If you prefer this automation disabled, delete the workflow file at .github/workflows/enable-automerge.yml or update its conditions.
