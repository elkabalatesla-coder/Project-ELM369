import pytest
from unittest.mock import AsyncMock

from app.github_service import GitHubRepositoryService


@pytest.mark.asyncio
async def test_create_repository_success(monkeypatch):
    client = AsyncMock()
    client.create_repository = AsyncMock(return_value={"name": "r"})
    svc = GitHubRepositoryService(client)
    res = await svc.create_repository("r", private=True)
    assert res["name"] == "r"


@pytest.mark.asyncio
async def test_create_repository_validation_error():
    client = AsyncMock()
    svc = GitHubRepositoryService(client)
    with pytest.raises(ValueError):
        await svc.create_repository("", private=True)


@pytest.mark.asyncio
async def test_create_repository_client_error(monkeypatch):
    class ClientError(Exception):
        pass

    client = AsyncMock()
    client.create_repository = AsyncMock(side_effect=ClientError("boom"))
    # expose the client error class so service can map it
    client.RepositoryError = ClientError

    svc = GitHubRepositoryService(client)

    with pytest.raises(RuntimeError):
        await svc.create_repository("repo-x", private=True)
