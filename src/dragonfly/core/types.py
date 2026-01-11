"""Core types for the Dragonfly Agent Framework.

This module defines the fundamental data structures used throughout the framework.
All types are stdlib-only dataclasses for core purity.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Literal
from uuid import UUID, uuid4

# Type aliases for constrained values
Reliability = Literal["low", "medium", "high"]
TimeHorizon = Literal["immediate", "near", "long"]
Stakes = Literal["low", "medium", "high"]
Reversibility = Literal["reversible", "costly", "irreversible"]
TimeSensitivity = Literal["immediate", "near", "flexible"]
AgentType = Literal["constraint", "stability", "reality_check"]
Confidence = Literal["low", "medium", "high"]
Severity = Literal["low", "medium", "high"]
TriggerAction = Literal["re_plan", "alert", "escalate"]


def _utc_now() -> datetime:
    """Return current UTC datetime."""
    return datetime.now(UTC)


@dataclass
class Observation:
    """A single observation about the world.

    Observations are the raw inputs to the decision process, representing
    what has been observed from various sources with associated reliability.
    """

    content: str
    source: str
    reliability: Reliability
    id: UUID = field(default_factory=uuid4)
    timestamp: datetime = field(default_factory=_utc_now)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "id": str(self.id),
            "content": self.content,
            "source": self.source,
            "reliability": self.reliability,
            "timestamp": self.timestamp.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Observation:
        """Deserialize from dictionary."""
        return cls(
            id=UUID(data["id"]),
            content=data["content"],
            source=data["source"],
            reliability=data["reliability"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
        )


@dataclass
class ActionSpec:
    """A candidate action that could be taken.

    ActionSpec represents a possible action with its characteristics,
    particularly its reversibility and time sensitivity.
    """

    name: str
    description: str
    reversibility: Reversibility
    id: UUID = field(default_factory=uuid4)
    time_sensitivity: TimeSensitivity | None = None

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "reversibility": self.reversibility,
            "time_sensitivity": self.time_sensitivity,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ActionSpec:
        """Deserialize from dictionary."""
        return cls(
            id=UUID(data["id"]),
            name=data["name"],
            description=data["description"],
            reversibility=data["reversibility"],
            time_sensitivity=data.get("time_sensitivity"),
        )


@dataclass
class Situation:
    """The complete context for a decision.

    A Situation captures everything needed to make a decision: the goal,
    current observations, candidate actions, and metadata like stakes
    and time horizon.
    """

    tenant_id: str
    goal: str
    time_horizon: TimeHorizon
    stakes: Stakes
    observations: list[Observation]
    candidate_actions: list[ActionSpec]
    id: UUID = field(default_factory=uuid4)
    context: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=_utc_now)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "id": str(self.id),
            "tenant_id": self.tenant_id,
            "goal": self.goal,
            "time_horizon": self.time_horizon,
            "stakes": self.stakes,
            "observations": [obs.to_dict() for obs in self.observations],
            "candidate_actions": [action.to_dict() for action in self.candidate_actions],
            "context": self.context,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Situation:
        """Deserialize from dictionary."""
        return cls(
            id=UUID(data["id"]),
            tenant_id=data["tenant_id"],
            goal=data["goal"],
            time_horizon=data["time_horizon"],
            stakes=data["stakes"],
            observations=[Observation.from_dict(obs) for obs in data["observations"]],
            candidate_actions=[ActionSpec.from_dict(action) for action in data["candidate_actions"]],
            context=data.get("context", {}),
            created_at=datetime.fromisoformat(data["created_at"]),
        )


@dataclass
class Assessment:
    """Output from an epistemic agent.

    An Assessment represents an agent's analysis of a situation or action,
    including claims, supporting evidence, and severity/confidence levels.
    """

    situation_id: UUID
    agent_type: AgentType
    claim: str
    support: list[UUID]
    confidence: Confidence
    severity: Severity
    reversibility: Reversibility
    is_hard_constraint: bool
    id: UUID = field(default_factory=uuid4)
    action_id: UUID | None = None
    recommended_tests: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=_utc_now)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "id": str(self.id),
            "situation_id": str(self.situation_id),
            "agent_type": self.agent_type,
            "claim": self.claim,
            "support": [str(s) for s in self.support],
            "confidence": self.confidence,
            "severity": self.severity,
            "reversibility": self.reversibility,
            "is_hard_constraint": self.is_hard_constraint,
            "action_id": str(self.action_id) if self.action_id else None,
            "recommended_tests": self.recommended_tests,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Assessment:
        """Deserialize from dictionary."""
        return cls(
            id=UUID(data["id"]),
            situation_id=UUID(data["situation_id"]),
            agent_type=data["agent_type"],
            claim=data["claim"],
            support=[UUID(s) for s in data["support"]],
            confidence=data["confidence"],
            severity=data["severity"],
            reversibility=data["reversibility"],
            is_hard_constraint=data["is_hard_constraint"],
            action_id=UUID(data["action_id"]) if data.get("action_id") else None,
            recommended_tests=data.get("recommended_tests", []),
            created_at=datetime.fromisoformat(data["created_at"]),
        )


@dataclass
class MonitoringTrigger:
    """A condition to watch that could trigger re-planning.

    MonitoringTriggers define what to watch for after a decision is made
    and what action to take if the condition is met.
    """

    condition: str
    action_on_trigger: TriggerAction

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "condition": self.condition,
            "action_on_trigger": self.action_on_trigger,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MonitoringTrigger:
        """Deserialize from dictionary."""
        return cls(
            condition=data["condition"],
            action_on_trigger=data["action_on_trigger"],
        )


@dataclass
class Decision:
    """The output of the synthesis process.

    A Decision represents the chosen action along with the rationale,
    alternatives considered, and conditions to monitor.
    """

    situation_id: UUID
    tenant_id: str
    selected_action: ActionSpec
    alternatives_considered: list[ActionSpec]
    robustness_basis: str
    assessments_used: list[UUID]
    monitoring: list[MonitoringTrigger]
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=_utc_now)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "id": str(self.id),
            "situation_id": str(self.situation_id),
            "tenant_id": self.tenant_id,
            "selected_action": self.selected_action.to_dict(),
            "alternatives_considered": [action.to_dict() for action in self.alternatives_considered],
            "robustness_basis": self.robustness_basis,
            "assessments_used": [str(a) for a in self.assessments_used],
            "monitoring": [trigger.to_dict() for trigger in self.monitoring],
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Decision:
        """Deserialize from dictionary."""
        return cls(
            id=UUID(data["id"]),
            situation_id=UUID(data["situation_id"]),
            tenant_id=data["tenant_id"],
            selected_action=ActionSpec.from_dict(data["selected_action"]),
            alternatives_considered=[
                ActionSpec.from_dict(action) for action in data["alternatives_considered"]
            ],
            robustness_basis=data["robustness_basis"],
            assessments_used=[UUID(a) for a in data["assessments_used"]],
            monitoring=[MonitoringTrigger.from_dict(trigger) for trigger in data["monitoring"]],
            created_at=datetime.fromisoformat(data["created_at"]),
        )
