"""Epistemic nodes/agents for the Dragonfly Agent Framework.

This module defines the EpistemicNode Protocol and implements the Phase 1
agents: ConstraintAgent, StabilityAgent, and RealityCheckAgent.

All agents use deterministic logic (no LLM) for Phase 1 validation.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from dragonfly.core.types import (
    ActionSpec,
    AgentType,
    Assessment,
    Situation,
)

# Keywords that indicate deadline/time constraints
DEADLINE_KEYWORDS = frozenset([
    "deadline", "due", "by friday", "by monday", "by tuesday", "by wednesday",
    "by thursday", "end of", "must complete", "time limit", "urgent",
    "asap", "immediately", "today", "tomorrow", "this week",
])

# Keywords that indicate increase/growth
INCREASE_KEYWORDS = frozenset([
    "increase", "grow", "rise", "up", "higher", "more", "expand", "gain",
])

# Keywords that indicate decrease/decline
DECREASE_KEYWORDS = frozenset([
    "decrease", "drop", "fall", "down", "lower", "less", "shrink", "decline",
])


@runtime_checkable
class EpistemicNode(Protocol):
    """Protocol for epistemic agents.

    All epistemic nodes must implement this protocol to participate
    in the decision graph.
    """

    @property
    def agent_type(self) -> AgentType:
        """Return the agent type identifier."""
        ...

    def assess(self, situation: Situation) -> list[Assessment]:
        """Analyze situation and return assessments."""
        ...


class ConstraintAgent:
    """Identifies hard constraints, failure modes, and irreversibility warnings.

    Phase 1 uses deterministic keyword-based logic to detect constraints.
    """

    @property
    def agent_type(self) -> AgentType:
        """Return the agent type identifier."""
        return "constraint"

    def assess(self, situation: Situation) -> list[Assessment]:
        """Analyze situation for constraints.

        Checks for:
        - Deadline constraints vs. flexible actions
        - Irreversible actions in high-stakes situations
        """
        assessments: list[Assessment] = []

        # Check for deadline constraints
        has_deadline = self._has_deadline_indicator(situation)

        for action in situation.candidate_actions:
            # Check deadline vs flexible time sensitivity
            if has_deadline and action.time_sensitivity == "flexible":
                assessments.append(
                    Assessment(
                        situation_id=situation.id,
                        agent_type=self.agent_type,
                        claim=f"Action '{action.name}' may miss deadline due to flexible timing",
                        support=[obs.id for obs in situation.observations],
                        confidence="high",
                        severity="high",
                        reversibility="irreversible",
                        is_hard_constraint=True,
                        action_id=action.id,
                    )
                )

            # Check irreversible action in high stakes
            if action.reversibility == "irreversible" and situation.stakes == "high":
                assessments.append(
                    Assessment(
                        situation_id=situation.id,
                        agent_type=self.agent_type,
                        claim=f"Irreversible action '{action.name}' in high-stakes situation",
                        support=[],
                        confidence="high",
                        severity="high",
                        reversibility="irreversible",
                        is_hard_constraint=False,  # Warning, not hard constraint
                        action_id=action.id,
                    )
                )

            # Check irreversible action in medium stakes with no reversible alternative
            elif action.reversibility == "irreversible" and situation.stakes == "medium":
                assessments.append(
                    Assessment(
                        situation_id=situation.id,
                        agent_type=self.agent_type,
                        claim=f"Irreversible action '{action.name}' limits future options",
                        support=[],
                        confidence="medium",
                        severity="medium",
                        reversibility="irreversible",
                        is_hard_constraint=False,
                        action_id=action.id,
                    )
                )

        return assessments

    def _has_deadline_indicator(self, situation: Situation) -> bool:
        """Check if any observation indicates a deadline."""
        for obs in situation.observations:
            content_lower = obs.content.lower()
            for keyword in DEADLINE_KEYWORDS:
                if keyword in content_lower:
                    return True
        return False


class StabilityAgent:
    """Identifies agency-preserving moves under uncertainty.

    Focuses on reversibility and minimax-regret considerations.
    Phase 1 uses deterministic scoring based on reversibility.
    """

    # Severity mapping based on reversibility
    REVERSIBILITY_SEVERITY: dict[str, str] = {
        "reversible": "low",
        "costly": "medium",
        "irreversible": "high",
    }

    @property
    def agent_type(self) -> AgentType:
        """Return the agent type identifier."""
        return "stability"

    def assess(self, situation: Situation) -> list[Assessment]:
        """Analyze situation for stability concerns.

        Evaluates each action's reversibility and generates assessments
        warning about actions that reduce future optionality.
        """
        assessments: list[Assessment] = []

        for action in situation.candidate_actions:
            severity = self.REVERSIBILITY_SEVERITY.get(action.reversibility, "medium")

            # Increase severity for high-stakes situations
            if situation.stakes == "high" and action.reversibility == "irreversible":
                severity = "high"

            if action.reversibility == "irreversible":
                assessments.append(
                    Assessment(
                        situation_id=situation.id,
                        agent_type=self.agent_type,
                        claim=f"Action '{action.name}' is irreversible and reduces future options",
                        support=[],
                        confidence="high",
                        severity=severity,
                        reversibility="irreversible",
                        is_hard_constraint=False,
                        action_id=action.id,
                    )
                )
            elif action.reversibility == "costly":
                assessments.append(
                    Assessment(
                        situation_id=situation.id,
                        agent_type=self.agent_type,
                        claim=f"Action '{action.name}' is costly to reverse",
                        support=[],
                        confidence="medium",
                        severity=severity,
                        reversibility="costly",
                        is_hard_constraint=False,
                        action_id=action.id,
                    )
                )
            else:
                # Reversible actions get positive assessment
                assessments.append(
                    Assessment(
                        situation_id=situation.id,
                        agent_type=self.agent_type,
                        claim=f"Action '{action.name}' preserves optionality (reversible)",
                        support=[],
                        confidence="high",
                        severity="low",
                        reversibility="reversible",
                        is_hard_constraint=False,
                        action_id=action.id,
                    )
                )

        return assessments


class RealityCheckAgent:
    """Identifies contradictions, disconfirmations, and missing information.

    Phase 1 uses deterministic logic to detect:
    - Low reliability observations in high stakes
    - Conflicting observations
    - Missing observations
    """

    @property
    def agent_type(self) -> AgentType:
        """Return the agent type identifier."""
        return "reality_check"

    def assess(self, situation: Situation) -> list[Assessment]:
        """Analyze situation for reality check concerns.

        Checks for:
        - Low reliability sources in high-stakes decisions
        - Conflicting observations
        - Insufficient information
        """
        assessments: list[Assessment] = []

        # Check for low reliability in high stakes
        for obs in situation.observations:
            if obs.reliability == "low" and situation.stakes in ("high", "medium"):
                severity = "high" if situation.stakes == "high" else "medium"
                assessments.append(
                    Assessment(
                        situation_id=situation.id,
                        agent_type=self.agent_type,
                        claim=f"Low reliability source '{obs.source}' informing {situation.stakes}-stakes decision",
                        support=[obs.id],
                        confidence="high",
                        severity=severity,
                        reversibility="reversible",
                        is_hard_constraint=False,
                        recommended_tests=[f"Verify information from {obs.source}"],
                    )
                )

        # Check for conflicting observations
        conflicts = self._detect_conflicts(situation.observations)
        for obs1, obs2 in conflicts:
            assessments.append(
                Assessment(
                    situation_id=situation.id,
                    agent_type=self.agent_type,
                    claim=f"Conflicting observations: '{obs1.source}' vs '{obs2.source}'",
                    support=[obs1.id, obs2.id],
                    confidence="high",
                    severity="medium",
                    reversibility="reversible",
                    is_hard_constraint=False,
                    recommended_tests=["Gather additional data to resolve conflict"],
                )
            )

        # Check for missing observations
        if not situation.observations and situation.candidate_actions:
            assessments.append(
                Assessment(
                    situation_id=situation.id,
                    agent_type=self.agent_type,
                    claim="No observations available to inform decision",
                    support=[],
                    confidence="high",
                    severity="medium",
                    reversibility="reversible",
                    is_hard_constraint=False,
                    recommended_tests=["Gather relevant observations before deciding"],
                )
            )

        return assessments

    def _detect_conflicts(
        self, observations: list
    ) -> list[tuple]:
        """Detect conflicting observations.

        Uses simple keyword-based conflict detection:
        - Observations predicting increase vs. decrease
        """
        conflicts: list[tuple] = []

        # Group observations by directional content
        increase_obs = []
        decrease_obs = []

        for obs in observations:
            content_lower = obs.content.lower()

            has_increase = any(kw in content_lower for kw in INCREASE_KEYWORDS)
            has_decrease = any(kw in content_lower for kw in DECREASE_KEYWORDS)

            if has_increase and not has_decrease:
                increase_obs.append(obs)
            elif has_decrease and not has_increase:
                decrease_obs.append(obs)

        # If we have both increase and decrease predictions, they conflict
        for inc_obs in increase_obs:
            for dec_obs in decrease_obs:
                conflicts.append((inc_obs, dec_obs))

        return conflicts
