from typing import Any, Dict
from pydantic import BaseModel, Field


class ArtifactInput(BaseModel):
    artifact_name: str = Field(..., min_length=1)
    module: str = Field(..., min_length=1)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AlgorithmInput(BaseModel):
    algorithm_name: str = Field(..., min_length=1)
    version: str = Field(..., min_length=1)
    description: str = Field(default="")


class DeviceInput(BaseModel):
    device_name: str = Field(..., min_length=1)
    device_type: str = Field(..., min_length=1)
    connection_type: str = Field(..., min_length=1)
