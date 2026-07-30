from datetime import datetime, timezone
from typing import Any, Dict, Optional
import uuid
import logging

logger = logging.getLogger(__name__)


class GitHubRepositoryService:
    """
    Repository Management Service (hardened)
    """

    def __init__(self, github_client):
        self.github = github_client
        # If the client exposes a custom exception class, capture it to avoid broad excepts.
        self._client_exc = getattr(github_client, "RepositoryError", None)

    def _now_iso(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _validate_name(self, name: str, field: str = "name", max_len: int = 255) -> None:
        if not isinstance(name, str) or not name.strip():
            raise ValueError(f"{field} must be a non-empty string")
        if len(name) > max_len:
            raise ValueError(f"{field} must be <= {max_len} characters")

    ####################################################
    # Repository Functions
    ####################################################

    async def create_repository(self, name: str, private: bool = True) -> Dict[str, Any]:
        self._validate_name(name, "repository name", max_len=100)
        try:
            return await self.github.create_repository(name=name, private=private)
        except Exception as e:
            # Translate known client exceptions to a service-level error
            if self._client_exc and isinstance(e, self._client_exc):
                logger.exception("github client error creating repository %s", name)
                raise RuntimeError("failed to create repository") from e
            raise

    async def delete_repository(self, repo: str) -> Dict[str, Any]:
        self._validate_name(repo, "repo")
        try:
            return await self.github.delete_repository(repo)
        except Exception as e:
            if self._client_exc and isinstance(e, self._client_exc):
                logger.exception("github client error deleting repository %s", repo)
                raise RuntimeError("failed to delete repository") from e
            raise

    async def list_repositories(self) -> Any:
        try:
            return await self.github.list_repositories()
        except Exception as e:
            if self._client_exc and isinstance(e, self._client_exc):
                logger.exception("github client error listing repositories")
                raise RuntimeError("failed to list repositories") from e
            raise

    async def get_repository(self, repo: str) -> Any:
        self._validate_name(repo, "repo")
        try:
            return await self.github.get_repository(repo)
        except Exception as e:
            if self._client_exc and isinstance(e, self._client_exc):
                logger.exception("github client error getting repository %s", repo)
                raise RuntimeError("failed to get repository") from e
            raise

    ####################################################
    # Branch Management
    ####################################################

    async def create_branch(self, repo: str, branch: str, source: str = "main") -> Any:
        self._validate_name(repo, "repo")
        self._validate_name(branch, "branch", max_len=200)
        self._validate_name(source, "source", max_len=200)
        try:
            return await self.github.create_branch(repo, branch, source)
        except Exception as e:
            if self._client_exc and isinstance(e, self._client_exc):
                logger.exception("github client error creating branch %s in %s", branch, repo)
                raise RuntimeError("failed to create branch") from e
            raise

    async def list_branches(self, repo: str) -> Any:
        self._validate_name(repo, "repo")
        try:
            return await self.github.list_branches(repo)
        except Exception as e:
            if self._client_exc and isinstance(e, self._client_exc):
                logger.exception("github client error listing branches for %s", repo)
                raise RuntimeError("failed to list branches") from e
            raise

    async def delete_branch(self, repo: str, branch: str) -> Any:
        self._validate_name(repo, "repo")
        self._validate_name(branch, "branch")
        try:
            return await self.github.delete_branch(repo, branch)
        except Exception as e:
            if self._client_exc and isinstance(e, self._client_exc):
                logger.exception("github client error deleting branch %s in %s", branch, repo)
                raise RuntimeError("failed to delete branch") from e
            raise

    ####################################################
    # Pull Requests
    ####################################################

    async def create_pull_request(
        self,
        repo: str,
        title: str,
        head: str,
        base: str = "main",
        body: str = ""
    ) -> Any:
        self._validate_name(repo, "repo")
        self._validate_name(title, "title", max_len=300)
        try:
            return await self.github.create_pull_request(repo, title, head, base, body)
        except Exception as e:
            if self._client_exc and isinstance(e, self._client_exc):
                logger.exception("github client error creating PR in %s", repo)
                raise RuntimeError("failed to create pull request") from e
            raise

    async def merge_pull_request(self, repo: str, number: int) -> Any:
        self._validate_name(repo, "repo")
        if not isinstance(number, int) or number <= 0:
            raise ValueError("pull request number must be a positive integer")
        try:
            return await self.github.merge_pull_request(repo, number)
        except Exception as e:
            if self._client_exc and isinstance(e, self._client_exc):
                logger.exception("github client error merging PR %s#%s", repo, number)
                raise RuntimeError("failed to merge pull request") from e
            raise

    ####################################################
    # Issues
    ####################################################

    async def create_issue(self, repo: str, title: str, body: str = "") -> Any:
        self._validate_name(repo, "repo")
        if not isinstance(title, str) or not title.strip():
            raise ValueError("issue title must be non-empty")
        try:
            return await self.github.create_issue(repo, title, body)
        except Exception as e:
            if self._client_exc and isinstance(e, self._client_exc):
                logger.exception("github client error creating issue in %s", repo)
                raise RuntimeError("failed to create issue") from e
            raise

    async def close_issue(self, repo: str, number: int) -> Any:
        self._validate_name(repo, "repo")
        if not isinstance(number, int) or number <= 0:
            raise ValueError("issue number must be a positive integer")
        try:
            return await self.github.close_issue(repo, number)
        except Exception as e:
            if self._client_exc and isinstance(e, self._client_exc):
                logger.exception("github client error closing issue %s#%s", repo, number)
                raise RuntimeError("failed to close issue") from e
            raise

    ####################################################
    # Releases
    ####################################################

    async def create_release(self, repo: str, tag: str, title: str, notes: str) -> Any:
        self._validate_name(repo, "repo")
        self._validate_name(tag, "tag", max_len=200)
        try:
            return await self.github.create_release(repo, tag, title, notes)
        except Exception as e:
            if self._client_exc and isinstance(e, self._client_exc):
                logger.exception("github client error creating release %s@%s", repo, tag)
                raise RuntimeError("failed to create release") from e
            raise

    ####################################################
    # Workflow Functions
    ####################################################

    async def trigger_workflow(self, repo: str, workflow: str, branch: str = "main") -> Any:
        self._validate_name(repo, "repo")
        self._validate_name(workflow, "workflow")
        try:
            return await self.github.trigger_workflow(repo, workflow, branch)
        except Exception as e:
            if self._client_exc and isinstance(e, self._client_exc):
                logger.exception("github client error triggering workflow %s in %s", workflow, repo)
                raise RuntimeError("failed to trigger workflow") from e
            raise

    async def workflow_status(self, repo: str) -> Any:
        self._validate_name(repo, "repo")
        try:
            return await self.github.workflow_status(repo)
        except Exception as e:
            if self._client_exc and isinstance(e, self._client_exc):
                logger.exception("github client error getting workflow status for %s", repo)
                raise RuntimeError("failed to get workflow status") from e
            raise

    ####################################################
    # Security
    ####################################################

    async def list_secrets(self, repo: str) -> Any:
        self._validate_name(repo, "repo")
        try:
            return await self.github.list_secrets(repo)
        except Exception as e:
            if self._client_exc and isinstance(e, self._client_exc):
                logger.exception("github client error listing secrets for %s", repo)
                raise RuntimeError("failed to list secrets") from e
            raise

    async def repository_permissions(self, repo: str) -> Any:
        self._validate_name(repo, "repo")
        try:
            return await self.github.repository_permissions(repo)
        except Exception as e:
            if self._client_exc and isinstance(e, self._client_exc):
                logger.exception("github client error getting permissions for %s", repo)
                raise RuntimeError("failed to get repository permissions") from e
            raise

    ####################################################
    # Audit
    ####################################################

    async def audit_event(self, event: str, user: str, details: Dict[str, Any]) -> Dict[str, Any]:
        # Do not log sensitive details here. Audit is a best-effort structured record.
        self._validate_name(event, "event", max_len=200)
        self._validate_name(user, "user", max_len=200)
        return {
            "audit_id": str(uuid.uuid4()),
            "event": event,
            "user": user,
            "details": details,
            "timestamp": self._now_iso(),
        }

    ####################################################
    # Health
    ####################################################

    async def health(self) -> Dict[str, Any]:
        return {
            "service": "GitHub Repository Service",
            "status": "ONLINE",
            "version": "0.7.1",
            "timestamp": self._now_iso(),
        }
