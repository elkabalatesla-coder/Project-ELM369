"""Project ELM369
Service Layer (hardened)
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional
import uuid
import logging

from app.repositories import repository
from app.models import (
    Artifact,
    Algorithm,
    DeviceConnection,
    AuditLog,
)
from app.schemas import ArtifactInput, AlgorithmInput, DeviceInput

logger = logging.getLogger(__name__)

# Resolve optional repository/DB exception types at import time.
_repo_exc = getattr(repository, "RepositoryError", None)
try:
    from sqlalchemy.exc import SQLAlchemyError as _SQLAlchemyError
except Exception:
    _SQLAlchemyError = None


class ELM369Service:
    def __init__(self, db):
        self.db = db

    ####################################################
    # ARTIFACTS
    ####################################################
    async def create_artifact(
        self,
        artifact_name: str,
        module: str,
        metadata: dict,
    ) -> Artifact:
        """Create and persist an Artifact.

        Validates input, persists via repository, records a best-effort audit entry,
        and translates repository errors to service-level RuntimeError for expected DB errors.
        Programming errors are re-raised.
        """
        # Validate input
        inp = ArtifactInput(artifact_name=artifact_name, module=module, metadata=metadata)

        artifact = Artifact(
            artifact_id=f"ELM369-{str(uuid.uuid4())}",
            artifact_name=inp.artifact_name,
            module=inp.module,
            metadata=inp.metadata,
            created_at=datetime.now(timezone.utc),
        )

        try:
            await repository.save_artifact(self.db, artifact)
            # small audit note (best-effort) if repository supports it
            if getattr(repository, "save_audit", None):
                try:
                    audit = AuditLog(action="create_artifact", target_id=artifact.artifact_id, timestamp=datetime.now(timezone.utc))
                    await repository.save_audit(self.db, audit)
                except Exception:
                    logger.debug("audit save failed (non-fatal)", exc_info=True)
        except Exception as e:
            # Handle expected repo/DB errors gracefully, re-raise unexpected exceptions
            if _repo_exc and isinstance(e, _repo_exc):
                logger.exception("repository error while saving artifact")
                raise RuntimeError("failed to persist artifact") from e
            if _SQLAlchemyError and isinstance(e, _SQLAlchemyError):
                logger.exception("database error while saving artifact")
                raise RuntimeError("failed to persist artifact") from e
            # Unknown/unexpected exception -> re-raise to surface programming errors
            raise

        return artifact

    async def list_artifacts(self) -> List[Artifact]:
        try:
            return await repository.get_artifacts(self.db)
        except Exception as e:
            if _repo_exc and isinstance(e, _repo_exc):
                logger.exception("repository error while listing artifacts")
                raise RuntimeError("failed to list artifacts") from e
            if _SQLAlchemyError and isinstance(e, _SQLAlchemyError):
                logger.exception("database error while listing artifacts")
                raise RuntimeError("failed to list artifacts") from e
            raise

    ####################################################
    # ALGORITHMS
    ####################################################
    async def register_algorithm(
        self,
        algorithm_name: str,
        version: str,
        description: str,
    ) -> Algorithm:
        inp = AlgorithmInput(algorithm_name=algorithm_name, version=version, description=description)

        algorithm = Algorithm(
            algorithm_id=f"ALG-{str(uuid.uuid4())}",
            name=inp.algorithm_name,
            version=inp.version,
            description=inp.description,
            created_at=datetime.now(timezone.utc),
        )

        try:
            await repository.save_algorithm(self.db, algorithm)
        except Exception as e:
            if _repo_exc and isinstance(e, _repo_exc):
                logger.exception("repository error while saving algorithm")
                raise RuntimeError("failed to persist algorithm") from e
            if _SQLAlchemyError and isinstance(e, _SQLAlchemyError):
                logger.exception("database error while saving algorithm")
                raise RuntimeError("failed to persist algorithm") from e
            raise

        return algorithm

    async def get_algorithms(self) -> List[Algorithm]:
        try:
            return await repository.get_algorithms(self.db)
        except Exception as e:
            if _repo_exc and isinstance(e, _repo_exc):
                logger.exception("repository error while getting algorithms")
                raise RuntimeError("failed to get algorithms") from e
            if _SQLAlchemyError and isinstance(e, _SQLAlchemyError):
                logger.exception("database error while getting algorithms")
                raise RuntimeError("failed to get algorithms") from e
            raise

    ####################################################
    # DEVICE CONNECTIONS
    ####################################################
    async def register_device(
        self,
        device_name: str,
        device_type: str,
        connection_type: str,
    ) -> DeviceConnection:
        inp = DeviceInput(device_name=device_name, device_type=device_type, connection_type=connection_type)

        device = DeviceConnection(
            device_name=inp.device_name,
            device_type=inp.device_type,
            connection_type=inp.connection_type,
            status="CONNECTED",
            connected_at=datetime.now(timezone.utc),
        )

        try:
            await repository.save_device(self.db, device)
            # audit best-effort if repository supports it
            if getattr(repository, "save_audit", None):
                try:
                    audit = AuditLog(action="register_device", target_id=device.device_name, timestamp=datetime.now(timezone.utc))
                    await repository.save_audit(self.db, audit)
                except Exception:
                    logger.debug("audit save failed (non-fatal)", exc_info=True)
        except Exception as e:
            if _repo_exc and isinstance(e, _repo_exc):
                logger.exception("repository error while registering device")
                raise RuntimeError("failed to register device") from e
            if _SQLAlchemyError and isinstance(e, _SQLAlchemyError):
                logger.exception("database error while registering device")
                raise RuntimeError("failed to register device") from e
            raise

        return device
