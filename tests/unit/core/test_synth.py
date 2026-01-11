"""Unit tests for synthesis algorithm."""

from uuid import uuid4

import pytest

from dragonfly.core.synth import (
    filter_by_constraints,
    generate_monitoring,
    score_robustness,
    select_action,
    synthesize,
)
from dragonfly.core.types import (
    ActionSpec,
    Assessment,
    Decision,
    MonitoringTrigger,
    Observation,
    Situation,
)


def create_situation(
    observations: list[Observation] | None = None,
    actions: list[ActionSpec] | None = None,
    stakes: str = "medium",
    time_horizon: str = "near",
) -> Situation:
    """Factory for test situations."""
    return Situation(
        tenant_id="test-tenant",
        goal="Test goal",
        time_horizon=time_horizon,
        stakes=stakes,
        observations=observations or [],
        candidate_actions=actions or [],
    )


def create_assessment(
    situation_id,
    agent_type: str = "constraint",
    action_id=None,
    is_hard_constraint: bool = False,
    severity: str = "medium",
    claim: str = "Test assessment",
) -> Assessment:
    """Factory for test assessments."""
    return Assessment(
        situation_id=situation_id,
        agent_type=agent_type,
        claim=claim,
        support=[],
        confidence="medium",
        severity=severity,
        reversibility="reversible",
        is_hard_constraint=is_hard_constraint,
        action_id=action_id,
    )


class TestFilterByConstraints:
    """Tests for filter_by_constraints function."""

    def test_filter_removes_violated_actions(self):
        """Actions with hard constraint violations are removed."""
        action_a = ActionSpec(name="A", description="A", reversibility="reversible")
        action_b = ActionSpec(name="B", description="B", reversibility="reversible")

        assessments = [
            create_assessment(
                situation_id=uuid4(),
                action_id=action_a.id,
                is_hard_constraint=True,
                claim="Action A violates constraint",
            )
        ]

        surviving = filter_by_constraints([action_a, action_b], assessments)

        assert action_a not in surviving
        assert action_b in surviving

    def test_actions_without_violations_pass_through(self):
        """Actions without hard constraint violations pass through."""
        action_a = ActionSpec(name="A", description="A", reversibility="reversible")
        action_b = ActionSpec(name="B", description="B", reversibility="reversible")

        assessments = []  # No constraints

        surviving = filter_by_constraints([action_a, action_b], assessments)

        assert action_a in surviving
        assert action_b in surviving

    def test_all_actions_violated_returns_empty(self):
        """All actions violated returns empty list."""
        action_a = ActionSpec(name="A", description="A", reversibility="reversible")
        action_b = ActionSpec(name="B", description="B", reversibility="reversible")

        assessments = [
            create_assessment(
                situation_id=uuid4(),
                action_id=action_a.id,
                is_hard_constraint=True,
            ),
            create_assessment(
                situation_id=uuid4(),
                action_id=action_b.id,
                is_hard_constraint=True,
            ),
        ]

        surviving = filter_by_constraints([action_a, action_b], assessments)

        assert len(surviving) == 0

    def test_non_hard_constraints_dont_filter(self):
        """Non-hard constraints (warnings) don't filter actions."""
        action_a = ActionSpec(name="A", description="A", reversibility="reversible")

        assessments = [
            create_assessment(
                situation_id=uuid4(),
                action_id=action_a.id,
                is_hard_constraint=False,  # Warning only
                severity="high",
            )
        ]

        surviving = filter_by_constraints([action_a], assessments)

        assert action_a in surviving


class TestScoreRobustness:
    """Tests for score_robustness function."""

    def test_reversible_scores_higher_than_irreversible(self):
        """Reversible actions score higher than irreversible."""
        reversible = ActionSpec(name="A", description="A", reversibility="reversible")
        irreversible = ActionSpec(name="B", description="B", reversibility="irreversible")

        score_rev = score_robustness(reversible, [])
        score_irrev = score_robustness(irreversible, [])

        assert score_rev > score_irrev

    def test_action_with_warnings_scores_lower(self):
        """Actions with warnings score lower than clean actions."""
        action = ActionSpec(name="A", description="A", reversibility="reversible")

        score_clean = score_robustness(action, [])

        warning = create_assessment(
            situation_id=uuid4(),
            action_id=action.id,
            is_hard_constraint=False,
            severity="high",
        )
        score_with_warning = score_robustness(action, [warning])

        assert score_clean > score_with_warning

    def test_score_is_between_0_and_1(self):
        """Score is in range [0, 1]."""
        reversible = ActionSpec(name="A", description="A", reversibility="reversible")
        irreversible = ActionSpec(name="B", description="B", reversibility="irreversible")

        for action in [reversible, irreversible]:
            score = score_robustness(action, [])
            assert 0.0 <= score <= 1.0

    def test_costly_scores_between_reversible_and_irreversible(self):
        """Costly reversibility scores between reversible and irreversible."""
        reversible = ActionSpec(name="A", description="A", reversibility="reversible")
        costly = ActionSpec(name="B", description="B", reversibility="costly")
        irreversible = ActionSpec(name="C", description="C", reversibility="irreversible")

        score_rev = score_robustness(reversible, [])
        score_costly = score_robustness(costly, [])
        score_irrev = score_robustness(irreversible, [])

        assert score_rev > score_costly > score_irrev


class TestSelectAction:
    """Tests for select_action function."""

    def test_selects_highest_scoring_action(self):
        """Selects the action with highest robustness score."""
        irreversible = ActionSpec(name="A", description="A", reversibility="irreversible")
        reversible = ActionSpec(name="B", description="B", reversibility="reversible")
        costly = ActionSpec(name="C", description="C", reversibility="costly")

        selected = select_action([irreversible, reversible, costly], [])

        assert selected.name == "B"  # Reversible has highest score

    def test_tied_scores_selects_first(self):
        """Tied scores selects deterministically."""
        action_a = ActionSpec(name="A", description="A", reversibility="reversible")
        action_b = ActionSpec(name="B", description="B", reversibility="reversible")

        selected = select_action([action_a, action_b], [])

        # Both have same score, should select first
        assert selected.name == "A"

    def test_single_action_returns_that_action(self):
        """Single action case returns that action."""
        action = ActionSpec(name="Only", description="Only option", reversibility="costly")

        selected = select_action([action], [])

        assert selected.name == "Only"


class TestGenerateMonitoring:
    """Tests for generate_monitoring function."""

    def test_high_severity_assessments_create_triggers(self):
        """High severity assessments generate monitoring triggers."""
        assessment = create_assessment(
            situation_id=uuid4(),
            is_hard_constraint=False,
            severity="high",
            claim="Market may shift",
        )

        triggers = generate_monitoring([assessment])

        assert len(triggers) >= 1
        assert any("Market" in t.condition for t in triggers)

    def test_low_severity_dont_create_triggers(self):
        """Low severity assessments don't create triggers."""
        assessment = create_assessment(
            situation_id=uuid4(),
            is_hard_constraint=False,
            severity="low",
            claim="Minor concern",
        )

        triggers = generate_monitoring([assessment])

        assert len(triggers) == 0

    def test_hard_constraints_dont_create_triggers(self):
        """Hard constraints don't create triggers (already filtered)."""
        assessment = create_assessment(
            situation_id=uuid4(),
            is_hard_constraint=True,
            severity="high",
            claim="Hard constraint",
        )

        triggers = generate_monitoring([assessment])

        # Hard constraints shouldn't create monitoring (action already blocked)
        assert len(triggers) == 0

    def test_triggers_have_appropriate_action(self):
        """Triggers have appropriate action_on_trigger values."""
        assessment = create_assessment(
            situation_id=uuid4(),
            is_hard_constraint=False,
            severity="high",
            claim="Important warning",
        )

        triggers = generate_monitoring([assessment])

        for trigger in triggers:
            assert trigger.action_on_trigger in ("re_plan", "alert", "escalate")


class TestSynthesize:
    """Tests for full synthesize function."""

    def test_synthesize_returns_decision(self):
        """synthesize returns a Decision object."""
        action = ActionSpec(name="Test", description="Test", reversibility="reversible")
        situation = create_situation(actions=[action])
        assessments = []

        decision = synthesize(situation, assessments)

        assert isinstance(decision, Decision)

    def test_decision_has_selected_action(self):
        """Decision has a selected_action."""
        action = ActionSpec(name="Test", description="Test", reversibility="reversible")
        situation = create_situation(actions=[action])

        decision = synthesize(situation, [])

        assert decision.selected_action is not None
        assert decision.selected_action.name == "Test"

    def test_decision_has_robustness_basis(self):
        """Decision has a non-empty robustness_basis."""
        action = ActionSpec(name="Test", description="Test", reversibility="reversible")
        situation = create_situation(actions=[action])

        decision = synthesize(situation, [])

        assert decision.robustness_basis != ""

    def test_decision_has_situation_id(self):
        """Decision references the correct situation."""
        action = ActionSpec(name="Test", description="Test", reversibility="reversible")
        situation = create_situation(actions=[action])

        decision = synthesize(situation, [])

        assert decision.situation_id == situation.id

    def test_decision_has_tenant_id(self):
        """Decision has correct tenant_id."""
        action = ActionSpec(name="Test", description="Test", reversibility="reversible")
        situation = create_situation(actions=[action])

        decision = synthesize(situation, [])

        assert decision.tenant_id == situation.tenant_id

    def test_decision_has_assessments_used(self):
        """Decision has list of assessment IDs used."""
        action = ActionSpec(name="Test", description="Test", reversibility="reversible")
        situation = create_situation(actions=[action])
        assessment = create_assessment(situation.id, "constraint")

        decision = synthesize(situation, [assessment])

        assert assessment.id in decision.assessments_used

    def test_decision_filters_by_constraints(self):
        """Decision filters out actions with hard constraints."""
        action_a = ActionSpec(name="A", description="A", reversibility="reversible")
        action_b = ActionSpec(name="B", description="B", reversibility="reversible")
        situation = create_situation(actions=[action_a, action_b])

        # Hard constraint on action A
        assessment = create_assessment(
            situation.id,
            action_id=action_a.id,
            is_hard_constraint=True,
        )

        decision = synthesize(situation, [assessment])

        assert decision.selected_action.name == "B"

    def test_decision_selects_most_robust(self):
        """Decision selects most robust action."""
        reversible = ActionSpec(name="A", description="A", reversibility="reversible")
        irreversible = ActionSpec(name="B", description="B", reversibility="irreversible")
        situation = create_situation(actions=[reversible, irreversible])

        decision = synthesize(situation, [])

        assert decision.selected_action.name == "A"  # Reversible is more robust

    def test_decision_includes_monitoring(self):
        """Decision includes monitoring triggers for high severity warnings."""
        action = ActionSpec(name="Test", description="Test", reversibility="reversible")
        situation = create_situation(actions=[action])
        warning = create_assessment(
            situation.id,
            is_hard_constraint=False,
            severity="high",
            claim="Important warning",
        )

        decision = synthesize(situation, [warning])

        assert len(decision.monitoring) >= 1

    def test_decision_with_no_surviving_actions(self):
        """Decision handles case where no actions survive constraints."""
        action = ActionSpec(name="Only", description="Only option", reversibility="reversible")
        situation = create_situation(actions=[action])
        
        # Hard constraint on the only action
        assessment = create_assessment(
            situation.id,
            action_id=action.id,
            is_hard_constraint=True,
        )

        decision = synthesize(situation, [assessment])

        # Should still return a decision, likely the most reversible as fallback
        assert decision.selected_action is not None
        assert "constraint" in decision.robustness_basis.lower() or "no action" in decision.robustness_basis.lower()
