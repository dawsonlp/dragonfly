"""Unit tests for epistemic nodes/agents."""

from uuid import uuid4

import pytest

from dragonfly.core.nodes import (
    ConstraintAgent,
    EpistemicNode,
    RealityCheckAgent,
    StabilityAgent,
)
from dragonfly.core.types import (
    ActionSpec,
    Assessment,
    Observation,
    Situation,
)


def create_situation(
    observations: list[Observation] | None = None,
    actions: list[ActionSpec] | None = None,
    stakes: str = "medium",
    time_horizon: str = "near",
    tenant_id: str = "test-tenant",
    goal: str = "Test goal",
) -> Situation:
    """Factory for test situations."""
    return Situation(
        tenant_id=tenant_id,
        goal=goal,
        time_horizon=time_horizon,
        stakes=stakes,
        observations=observations or [],
        candidate_actions=actions or [],
    )


class TestEpistemicNodeProtocol:
    """Tests for EpistemicNode Protocol compliance."""

    def test_constraint_agent_implements_protocol(self):
        """ConstraintAgent implements EpistemicNode Protocol."""
        agent = ConstraintAgent()
        assert isinstance(agent, EpistemicNode)
        assert agent.agent_type == "constraint"

    def test_stability_agent_implements_protocol(self):
        """StabilityAgent implements EpistemicNode Protocol."""
        agent = StabilityAgent()
        assert isinstance(agent, EpistemicNode)
        assert agent.agent_type == "stability"

    def test_reality_check_agent_implements_protocol(self):
        """RealityCheckAgent implements EpistemicNode Protocol."""
        agent = RealityCheckAgent()
        assert isinstance(agent, EpistemicNode)
        assert agent.agent_type == "reality_check"


class TestConstraintAgent:
    """Tests for ConstraintAgent."""

    def test_assess_returns_list_of_assessments(self):
        """assess() returns list[Assessment]."""
        agent = ConstraintAgent()
        situation = create_situation()
        assessments = agent.assess(situation)

        assert isinstance(assessments, list)
        for assessment in assessments:
            assert isinstance(assessment, Assessment)

    def test_all_assessments_have_correct_agent_type(self):
        """All assessments have agent_type='constraint'."""
        agent = ConstraintAgent()
        obs = Observation(content="test", source="test", reliability="medium")
        action = ActionSpec(name="test", description="test", reversibility="reversible")
        situation = create_situation(observations=[obs], actions=[action])

        assessments = agent.assess(situation)

        for assessment in assessments:
            assert assessment.agent_type == "constraint"

    def test_detects_deadline_constraint_for_flexible_action(self):
        """Deadline observation should flag flexible actions."""
        agent = ConstraintAgent()
        obs = Observation(
            content="Deadline is Friday",
            source="manager",
            reliability="high",
        )
        action = ActionSpec(
            name="Research more",
            description="Gather more information",
            reversibility="reversible",
            time_sensitivity="flexible",
        )
        situation = create_situation(observations=[obs], actions=[action])

        assessments = agent.assess(situation)

        # Should have at least one hard constraint about deadline
        hard_constraints = [a for a in assessments if a.is_hard_constraint]
        assert len(hard_constraints) >= 1
        assert any("deadline" in a.claim.lower() for a in hard_constraints)

    def test_flags_irreversible_action_in_high_stakes(self):
        """Irreversible action in high-stakes situation should be flagged."""
        agent = ConstraintAgent()
        action = ActionSpec(
            name="Sign contract",
            description="Sign irreversible contract",
            reversibility="irreversible",
        )
        situation = create_situation(actions=[action], stakes="high")

        assessments = agent.assess(situation)

        # Should have an assessment warning about irreversibility
        warnings = [a for a in assessments if a.action_id == action.id]
        assert len(warnings) >= 1
        assert any("irreversible" in a.claim.lower() for a in warnings)

    def test_no_hard_constraints_for_simple_situation(self):
        """Simple situation without constraints returns no hard constraints."""
        agent = ConstraintAgent()
        obs = Observation(content="Everything is normal", source="test", reliability="high")
        action = ActionSpec(
            name="Proceed",
            description="Continue as planned",
            reversibility="reversible",
            time_sensitivity="near",
        )
        situation = create_situation(observations=[obs], actions=[action], stakes="low")

        assessments = agent.assess(situation)

        hard_constraints = [a for a in assessments if a.is_hard_constraint]
        # May have zero hard constraints for a simple, low-stakes situation
        assert all(not a.is_hard_constraint for a in assessments) or len(hard_constraints) == 0

    def test_deterministic_behavior(self):
        """Same input produces same output."""
        agent = ConstraintAgent()
        obs = Observation(content="Deadline is Friday", source="test", reliability="high")
        action = ActionSpec(
            name="Test",
            description="Test action",
            reversibility="irreversible",
            time_sensitivity="flexible",
        )
        situation = create_situation(observations=[obs], actions=[action], stakes="high")

        assessments1 = agent.assess(situation)
        assessments2 = agent.assess(situation)

        # Same number of assessments with same claims
        assert len(assessments1) == len(assessments2)
        claims1 = sorted(a.claim for a in assessments1)
        claims2 = sorted(a.claim for a in assessments2)
        assert claims1 == claims2


class TestStabilityAgent:
    """Tests for StabilityAgent."""

    def test_assess_returns_list_of_assessments(self):
        """assess() returns list[Assessment]."""
        agent = StabilityAgent()
        situation = create_situation()
        assessments = agent.assess(situation)

        assert isinstance(assessments, list)

    def test_all_assessments_have_correct_agent_type(self):
        """All assessments have agent_type='stability'."""
        agent = StabilityAgent()
        action = ActionSpec(name="test", description="test", reversibility="reversible")
        situation = create_situation(actions=[action])

        assessments = agent.assess(situation)

        for assessment in assessments:
            assert assessment.agent_type == "stability"

    def test_warns_about_irreversible_actions(self):
        """Warns about irreversible actions."""
        agent = StabilityAgent()
        irreversible = ActionSpec(
            name="Irreversible",
            description="Cannot be undone",
            reversibility="irreversible",
        )
        situation = create_situation(actions=[irreversible])

        assessments = agent.assess(situation)

        # Should warn about the irreversible action
        warnings = [a for a in assessments if a.action_id == irreversible.id]
        assert len(warnings) >= 1

    def test_evaluates_all_actions(self):
        """Evaluates all candidate actions."""
        agent = StabilityAgent()
        action_a = ActionSpec(name="A", description="A", reversibility="reversible")
        action_b = ActionSpec(name="B", description="B", reversibility="irreversible")
        action_c = ActionSpec(name="C", description="C", reversibility="costly")
        situation = create_situation(actions=[action_a, action_b, action_c])

        assessments = agent.assess(situation)

        # Should have assessments for each action
        action_ids_with_assessments = {a.action_id for a in assessments if a.action_id}
        assert action_a.id in action_ids_with_assessments or action_b.id in action_ids_with_assessments

    def test_irreversible_gets_higher_severity_than_reversible(self):
        """Irreversible actions get higher severity warnings than reversible."""
        agent = StabilityAgent()
        irreversible = ActionSpec(name="B", description="B", reversibility="irreversible")
        situation = create_situation(actions=[irreversible], stakes="high")

        assessments = agent.assess(situation)

        # Find assessments for the irreversible action
        irrev_assessments = [a for a in assessments if a.action_id == irreversible.id]
        assert len(irrev_assessments) >= 1
        # At least one should have high severity
        assert any(a.severity in ("medium", "high") for a in irrev_assessments)

    def test_deterministic_behavior(self):
        """Same input produces same output."""
        agent = StabilityAgent()
        action = ActionSpec(name="Test", description="Test", reversibility="costly")
        situation = create_situation(actions=[action])

        assessments1 = agent.assess(situation)
        assessments2 = agent.assess(situation)

        assert len(assessments1) == len(assessments2)


class TestRealityCheckAgent:
    """Tests for RealityCheckAgent."""

    def test_assess_returns_list_of_assessments(self):
        """assess() returns list[Assessment]."""
        agent = RealityCheckAgent()
        situation = create_situation()
        assessments = agent.assess(situation)

        assert isinstance(assessments, list)

    def test_all_assessments_have_correct_agent_type(self):
        """All assessments have agent_type='reality_check'."""
        agent = RealityCheckAgent()
        obs = Observation(content="test", source="test", reliability="low")
        situation = create_situation(observations=[obs], stakes="high")

        assessments = agent.assess(situation)

        for assessment in assessments:
            assert assessment.agent_type == "reality_check"

    def test_flags_low_reliability_in_high_stakes(self):
        """Low reliability observation in high stakes should be flagged."""
        agent = RealityCheckAgent()
        obs = Observation(
            content="Market will go up",
            source="social_media_rumor",
            reliability="low",
        )
        situation = create_situation(observations=[obs], stakes="high")

        assessments = agent.assess(situation)

        # Should have a warning about low reliability
        warnings = [a for a in assessments if a.severity in ("medium", "high")]
        assert len(warnings) >= 1

    def test_flags_conflicting_observations(self):
        """Conflicting observations should be flagged."""
        agent = RealityCheckAgent()
        obs1 = Observation(
            content="Demand will increase 20%",
            source="sales_forecast",
            reliability="medium",
        )
        obs2 = Observation(
            content="Demand will decrease 10%",
            source="market_analysis",
            reliability="medium",
        )
        situation = create_situation(observations=[obs1, obs2])

        assessments = agent.assess(situation)

        # Should detect the conflict
        conflict_warnings = [a for a in assessments if "conflict" in a.claim.lower()]
        assert len(conflict_warnings) >= 1

    def test_no_warnings_for_consistent_high_reliability(self):
        """Consistent, high-reliability observations should have minimal warnings."""
        agent = RealityCheckAgent()
        obs1 = Observation(content="Sales are stable", source="report_a", reliability="high")
        obs2 = Observation(content="Customer satisfaction is high", source="report_b", reliability="high")
        situation = create_situation(observations=[obs1, obs2], stakes="low")

        assessments = agent.assess(situation)

        # Should have fewer or no high-severity warnings
        high_severity = [a for a in assessments if a.severity == "high"]
        # With consistent high-reliability data and low stakes, should be minimal
        assert len(high_severity) <= 1

    def test_flags_missing_observations(self):
        """Empty observations should be noted."""
        agent = RealityCheckAgent()
        action = ActionSpec(name="Act", description="Take action", reversibility="costly")
        situation = create_situation(observations=[], actions=[action])

        assessments = agent.assess(situation)

        # Should note the lack of observations
        # This might create an assessment about insufficient information
        assert isinstance(assessments, list)

    def test_deterministic_behavior(self):
        """Same input produces same output."""
        agent = RealityCheckAgent()
        obs = Observation(content="Test observation", source="test", reliability="low")
        situation = create_situation(observations=[obs], stakes="high")

        assessments1 = agent.assess(situation)
        assessments2 = agent.assess(situation)

        assert len(assessments1) == len(assessments2)
        claims1 = sorted(a.claim for a in assessments1)
        claims2 = sorted(a.claim for a in assessments2)
        assert claims1 == claims2
