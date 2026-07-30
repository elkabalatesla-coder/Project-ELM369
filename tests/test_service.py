import pytest
from unittest.mock import AsyncMock

from app.service import ELM369Service
from app.models import Artifact, DeviceConnection
from datetime import timezone


@pytest.mark.asyncio
async def test_create_artifact_success(monkeypatch):
    db = object()
    svc = ELM369Service(db)

    saved = []

    async def fake_save_artifact(db_arg, artifact):
        saved.append(artifact)
        return None

    monkeypatch.setattr("app.repositories.repository.save_artifact", AsyncMock(side_effect=fake_save_artifact))
    monkeypatch.setattr("app.repositories.repository.save_audit", AsyncMock(return_value=None))

    artifact = await svc.create_artifact("name", "mod", {"k": "v"})
    assert artifact.artifact_name == "name"
    assert artifact.module == "mod"
    assert artifact.metadata == {"k": "v"}
    assert saved, "artifact should be saved"


@pytest.mark.asyncio
async def test_create_artifact_repo_failure(monkeypatch):
    db = object()
    svc = ELM369Service(db)

    async def fake_save_artifact(db_arg, artifact):
        raise Exception("db down")

    monkeypatch.setattr("app.repositories.repository.save_artifact", AsyncMock(side_effect=fake_save_artifact))

    with pytest.raises(RuntimeError):
        await svc.create_artifact("name", "mod", {})


@pytest.mark.asyncio
async def test_register_device_returns_device(monkeypatch):
    db = object()
    svc = ELM369Service(db)

    async def fake_save_device(db_arg, device):
        return None

    monkeypatch.setattr("app.repositories.repository.save_device", AsyncMock(side_effect=fake_save_device))
    monkeypatch.setattr("app.repositories.repository.save_audit", AsyncMock(return_value=None))

    device = await svc.register_device("dev1", "type1", "tcp")
    assert device.device_name == "dev1"
    assert device.status == "CONNECTED"
    assert device.connected_at.tzinfo is not None
