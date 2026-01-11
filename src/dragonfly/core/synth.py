"""Synthesis algorithm for the Dragonfly Agent Framework.

This module implements the synthesis process that:
1. Filters actions violating hard constraints
2. Scores remaining actions by robustness
3. Selects the best action
4. Generates monitoring triggers

The synthesis asks "which actions survive disagreement?" not "which model is true?"
"""

from __future__ import annotations

from dragonfly.core.types import (
    ActionSpec,
    Assessment,
    Decision,
    MonitoringTrigger,
    Situation,
)

# Reversibility scores (0-1, higher is better)
REVERSIBILITY_SCORES: dict[str, float] = {
    "reversible": 1.0,
    "costly": 0.5,
    "irreversible": 0.0,
}

# Severity weights for penalty calculation
SEVERITY_WEIGHTS: dict[str, float] = {
    "low": 0.1,
    "medium": 0.2,
    "high": 0.3,
}


def filter_by_constraints(
    actions: list[ActionSpec],
    assessments: list[Assessment],
) -> list[ActionSpec]:
    """Filter out actions that violate hard constraints.

    Args:
        actions: List of candidate actions
        assessments: List of assessments from all agents

    Returns:
        List of actions that don't violate any hard constraints
    """
    # Find action IDs with hard constraint violations
    violated_action_ids = {
        a.action_id
        for a in assessments
        if a.is_hard_constraint and a.action_id is not None
    }

    # Return actions that aren't violated
    return [
        action for action in actions
        if action.id not in violated_action_ids
    ]


def score_robustness(
    action: ActionSpec,
    assessments: list[Assessment],
) -> float:
    """Calculate robustness score for an action.

    Score components:
    - Reversibility (60% weight): reversible > costly > irreversible
    - Warning penalty (40% weight): fewer/milder warnings = better

    Args:
        action: Action to score
        assessments: List of assessments (may include ones for other actions)

    Returns:
        Robustness score in range [0.0, 1.0]
    """
    # Reversibility component (0-1)
    rev_score = REVERSIBILITY_SCORES.get(action.reversibility, 0.5)

    # Warning penalty component
    # Get warnings for this specific action
    action_warnings = [
        a for a in assessments
        if a.action_id == action.id and not a.is_hard_constraint
    ]

    # Calculate total penalty from warnings
    warning_penalty = sum(
        SEVERITY_WEIGHTS.get(w.severity, 0.2)
        for w in action_warnings
    )

    # Clamp to [0, 1] range
    constraint_score = max(0.0, 1.0 - warning_penalty)

    # Combined score with weights
    # 60% reversibility, 40% constraint satisfaction
    return 0.6 * rev_score + 0.4 * constraint_score


def select_action(
    actions: list[ActionSpec],
    assessments: list[Assessment],
) -> ActionSpec:
    """Select the best action based on robustness scores.

    Args:
        actions: List of candidate actions (should be non-empty)
        assessments: List of assessments

    Returns:
        The action with the highest robustness score
    """
    if not actions:
        raise ValueError("Cannot select from empty action list")

    # Score all actions
    scored = [(action, score_robustness(action, assessments)) for action in actions]

    # Sort by score (descending), then by original order for ties
    scored.sort(key=lambda x: (-x[1], actions.index(x[0])))

    return scored[0][0]


def generate_monitoring(
    assessments: list[Assessment],
) -> list[MonitoringTrigger]:
    """Generate monitoring triggers from high-severity assessments.

    Args:
        assessments: List of assessments from all agents

    Returns:
        List of monitoring triggers
    """
    triggers: list[MonitoringTrigger] = []

    for assessment in assessments:
        # Only generate triggers for non-hard-constraint, high-severity warnings
        if not assessment.is_hard_constraint and assessment.severity == "high":
            triggers.append(
                MonitoringTrigger(
                    condition=f"Monitor: {assessment.claim}",
                    action_on_trigger="alert",
                )
            )

    return triggers


def _find_most_reversible(actions: list[ActionSpec]) -> ActionSpec:
    """Find the most reversible action from a list.

    Used as fallback when no actions survive constraints.
    """
    if not actions:
        raise ValueError("Cannot find most reversible from empty list")

    # Sort by reversibility score
    sorted_actions = sorted(
        actions,
        key=lambda a: REVERSIBILITY_SCORES.get(a.reversibility, 0.5),
        reverse=True,
    )
    return sorted_actions[0]


def synthesize(
    situation: Situation,
    assessments: list[Assessment],
) -> Decision:
    """Synthesize a decision from situation and assessments.

    The synthesis process:
    1. Filter actions that violate hard constraints
    2. Score remaining actions by robustness
    3. Select the best action
    4. Generate monitoring triggers

    Args:
        situation: The decision situation
        assessments: List of assessments from all agents

    Returns:
        A Decision object with the selected action and rationale
    """
    # Filter by hard constraints
    surviving_actions = filter_by_constraints(
        situation.candidate_actions,
        assessments,
    )

    # Generate monitoring triggers
    monitoring = generate_monitoring(assessments)

    # Collect assessment IDs used
    assessments_used = [a.id for a in assessments]

    # Determine alternatives (all except selected)
    if surviving_actions:
        # Select best action from survivors
        selected_action = select_action(surviving_actions, assessments)
        score = score_robustness(selected_action, assessments)

        alternatives = [
            a for a in situation.candidate_actions
            if a.id != selected_action.id
        ]

        robustness_basis = (
            f"Passed all hard constraints. "
            f"Selected '{selected_action.name}' with robustness score {score:.2f}. "
            f"Action is {selected_action.reversibility}."
        )
    else:
        # No actions survive - select most reversible as fallback
        selected_action = _find_most_reversible(situation.candidate_actions)
        
        alternatives = [
            a for a in situation.candidate_actions
            if a.id != selected_action.id
        ]

        robustness_basis = (
            f"No action passed all hard constraints. "
            f"Selected '{selected_action.name}' as most reversible fallback option."
        )

    return Decision(
        situation_id=situation.id,
        tenant_id=situation.tenant_id,
        selected_action=selected_action,
        alternatives_considered=alternatives,
        robustness_basis=robustness_basis,
        assessments_used=assessments_used,
        monitoring=monitoring,
    )
