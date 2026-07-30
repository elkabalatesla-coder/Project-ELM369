import pytest
from unittest.mock import AsyncMock

from app.service import ELM369Service
from app.models import Algorithm
from pydantic import ValidationError


@pytest.mark.asyncio
async def test_register_algorithm_success(monkeypatch):
    db = object()
    svc = ELM369Service(db)

    saved = []

    async def fake_save_algorithm(db_arg, algorithm):
        saved.append(algorithm)
        return None

    monkeypatch.setattr("app.repositories.repository.save_algorithm", AsyncMock(side_effect=fake_save_algorithm))
    monkeypatch.setattr("app.repositories.repository.save_audit", AsyncMock(return_value=None))

    alg = await svc.register_algorithm("alg1", "v1", "desc")
    assert alg.name == "alg1"
    assert alg.version == "v1"
    assert saved


@pytest.mark.asyncio
async def test_get_algorithms_success(monkeypatch):
    db = object()
    svc = ELM369Service(db)

    fake_list = [Algorithm(algorithm_id="ALG-1", name="a", version="v", description="", created_at=None)]
    async def fake_get_algorithms(db_arg):
        return fake_list

    monkeypatch.setattr("app.repositories.repository.get_algorithms", AsyncMock(side_effect=fake_get_algorithms))

    res = await svc.get_algorithms()
    assert res == fake_list


@pytest.mark.asyncio
async def test_list_artifacts_failure(monkeypatch):
    db = object()
    svc = ELM369Service(db)

    async def fake_get_artifacts(db_arg):
        raise Exception("db error")

    monkeypatch.setattr("app.repositories.repository.get_artifacts", AsyncMock(side_effect=fake_get_artifacts))

    with pytest.raises(RuntimeError):
        await svc.list_artifacts()


@pytest.mark.asyncio
async def test_create_artifact_schema_rejection():
    db = object()
    svc = ELM369Service(db)

    with pytest.raises(ValidationError):
        # empty artifact_name should fail validation
        await svc.create_artifact("", "mod", {})
