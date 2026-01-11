"""FastAPI routes for the Dragonfly Agent Framework.

This module provides the HTTP API endpoints for the decision service.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from dragonfly.core.types import (
    ActionSpec,
    Decision,
    Observation,
    Situation,
)
from dragonfly.service.runtime.langgraph_runner import get_runner


router = APIRouter()


class ObservationRequest(BaseModel):
    """Request model for an observation."""

    content: str
    source: str
    reliability: str  # "low" | "medium" | "high"


class ActionSpecRequest(BaseModel):
    """Request model for an action specification."""

    name: str
    description: str
    reversibility: str  # "reversible" | "costly" | "irreversible"
    time_sensitivity: str | None = None  # "immediate" | "near" | "flexible"


class SituationRequest(BaseModel):
    """Request model for a decision situation."""

    tenant_id: str
    goal: str
    time_horizon: str  # "immediate" | "near" | "long"
    stakes: str  # "low" | "medium" | "high"
    observations: list[ObservationRequest]
    candidate_actions: list[ActionSpecRequest]
    context: dict[str, Any] = {}


class MonitoringTriggerResponse(BaseModel):
    """Response model for a monitoring trigger."""

    condition: str
    action_on_trigger: str


class ActionSpecResponse(BaseModel):
    """Response model for an action specification."""

    id: str
    name: str
    description: str
    reversibility: str
    time_sensitivity: str | None = None


class DecisionResponse(BaseModel):
    """Response model for a decision."""

    id: str
    situation_id: str
    tenant_id: str
    selected_action: ActionSpecResponse
    alternatives_considered: list[ActionSpecResponse]
    robustness_basis: str
    assessments_used: list[str]
    monitoring: list[MonitoringTriggerResponse]
    created_at: str


def _observation_from_request(req: ObservationRequest) -> Observation:
    """Convert request to core type."""
    return Observation(
        content=req.content,
        source=req.source,
        reliability=req.reliability,
    )


def _action_spec_from_request(req: ActionSpecRequest) -> ActionSpec:
    """Convert request to core type."""
    return ActionSpec(
        name=req.name,
        description=req.description,
        reversibility=req.reversibility,
        time_sensitivity=req.time_sensitivity,
    )


def _decision_to_response(decision: Decision) -> DecisionResponse:
    """Convert core Decision to response model."""
    return DecisionResponse(
        id=str(decision.id),
        situation_id=str(decision.situation_id),
        tenant_id=decision.tenant_id,
        selected_action=ActionSpecResponse(
            id=str(decision.selected_action.id),
            name=decision.selected_action.name,
            description=decision.selected_action.description,
            reversibility=decision.selected_action.reversibility,
            time_sensitivity=decision.selected_action.time_sensitivity,
        ),
        alternatives_considered=[
            ActionSpecResponse(
                id=str(action.id),
                name=action.name,
                description=action.description,
                reversibility=action.reversibility,
                time_sensitivity=action.time_sensitivity,
            )
            for action in decision.alternatives_considered
        ],
        robustness_basis=decision.robustness_basis,
        assessments_used=[str(a) for a in decision.assessments_used],
        monitoring=[
            MonitoringTriggerResponse(
                condition=t.condition,
                action_on_trigger=t.action_on_trigger,
            )
            for t in decision.monitoring
        ],
        created_at=decision.created_at.isoformat(),
    )


@router.post("/decide", response_model=DecisionResponse)
async def decide(request: SituationRequest) -> DecisionResponse:
    """Process a decision request.

    Takes a situation with observations and candidate actions,
    runs it through the decision graph, and returns a Decision.
    """
    try:
        # Convert request to core types
        observations = [_observation_from_request(o) for o in request.observations]
        actions = [_action_spec_from_request(a) for a in request.candidate_actions]

        situation = Situation(
            tenant_id=request.tenant_id,
            goal=request.goal,
            time_horizon=request.time_horizon,
            stakes=request.stakes,
            observations=observations,
            candidate_actions=actions,
            context=request.context,
        )

        # Run the decision graph
        runner = get_runner()
        decision = runner.run(situation)

        return _decision_to_response(decision)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {e}")


@router.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}
