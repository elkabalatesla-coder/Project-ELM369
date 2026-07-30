Auto-merge & repository permissions

To allow auto-merge for Dependabot or automated-fix PRs:

- Enable auto-merge:
  - Settings → Merge button → enable "Allow auto-merge" for the repository.
- Workflow permissions:
  - If you add a workflow/Action that attempts to enable auto-merge programmatically, the workflow must have write permission for pull requests.
  - Go to Settings → Actions → General → Workflow permissions and ensure "Read and write permissions" is set, or that the token used has the necessary repo scope.
- Branch protection:
  - Branch protection rules may block auto-merge if required checks or approvals are missing. Make sure required status checks are configured and stable.
  - Consider whether maintainers should be allowed to bypass specific protections for automated dependency updates where appropriate.
- Dependabot PRs:
  - Dependabot PRs are created by dependabot[bot]; maintainers should review these changes and then either enable auto-merge in the PR UI or merge once checks pass.
  - If you rely on automation to enable auto-merge, ensure the automation account/token has the necessary permissions.

Notes:
- Programmatically enabling auto-merge from a GitHub Action can fail if repository or organization permissions restrict the workflow token. Confirm Workflow permissions and required access before relying on automation.
- This repository now lists backports.zoneinfo in pyproject.toml and requirements.txt to provide compatibility for Python < 3.9. Add these to your environment when running Python tooling.
