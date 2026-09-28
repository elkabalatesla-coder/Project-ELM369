from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any

class Domain(str, Enum):
    AI='AI'; AGENTS='AGENTS'; DIGITAL_TWIN='DIGITAL_TWIN'; ROBOTICS='ROBOTICS'; VEHICLE='VEHICLE'; DRONE='DRONE'; CLOUD='CLOUD'; BLOCKCHAIN='BLOCKCHAIN'; CRM='CRM'; INDUSTRIAL='INDUSTRIAL'

@dataclass(frozen=True)
class Capability:
    domain: Domain
    name: str
    version: str='0.1.0'
    inputs: tuple[str,...]=()
    outputs: tuple[str,...]=()
    constraints: tuple[str,...]=()
    metadata: dict[str,Any]=field(default_factory=dict)
    def to_dict(self):
        d=asdict(self); d['domain']=self.domain.value; return d

@dataclass(frozen=True)
class ExpansionRequest:
    identifier: str
    domain: Domain
    task: str
    capabilities: tuple[Capability,...]=()
    authorization_required: bool=True
    def to_dict(self):
        return {'identifier':self.identifier,'domain':self.domain.value,'task':self.task,'capabilities':[c.to_dict() for c in self.capabilities],'authorization_required':self.authorization_required}

class ExpansionPlanner:
    def plan(self, request: ExpansionRequest):
        if not request.task.strip(): raise ValueError('task is required')
        return {
            'identity': request.identifier,
            'domain': request.domain.value,
            'task': request.task,
            'steps': ['inventory','design','validate','authorize','execute','verify','audit'],
            'authorization_required': request.authorization_required,
            'capabilities': [c.name for c in request.capabilities],
            'execution_status': 'NOT_EXECUTED'
        }

DEFAULT_CAPABILITIES = {
    Domain.AI: Capability(Domain.AI,'model_inference'),
    Domain.AGENTS: Capability(Domain.AGENTS,'agent_orchestration'),
    Domain.DIGITAL_TWIN: Capability(Domain.DIGITAL_TWIN,'state_replication'),
    Domain.ROBOTICS: Capability(Domain.ROBOTICS,'robot_control_interface'),
    Domain.VEHICLE: Capability(Domain.VEHICLE,'vehicle_interface'),
    Domain.DRONE: Capability(Domain.DRONE,'drone_interface'),
    Domain.CLOUD: Capability(Domain.CLOUD,'cloud_service_adapter'),
    Domain.BLOCKCHAIN: Capability(Domain.BLOCKCHAIN,'provenance_anchor'),
    Domain.CRM: Capability(Domain.CRM,'identity_contract_history'),
    Domain.INDUSTRIAL: Capability(Domain.INDUSTRIAL,'industrial_build_orchestration'),
}
