"""Unit tests for LangGraph runner."""

import pytest

from dragonfly.core.types import (
    ActionSpec,
    Decision,
    Observation,
    Situation,
)
from dragonfly.service.runtime.langgraph_runner import (
    DragonflyRunner,
    get_runner,
)


def create_test_situation(
    observations: list[Observation] | None = None,
    actions: list[ActionSpec] | None = None,
    stakes: str = "medium",
) -> Situation:
    """Factory for test situations."""
    if actions is None:
        actions = [
            ActionSpec(name="Default", description="Default action", reversibility="reversible")
        ]
    return Situation(
        tenant_id="test-tenant",
        goal="Test goal",
        time_horizon="near",
        stakes=stakes,
        observations=observations or [],
        candidate_actions=actions,
    )


class TestDragonflyRunner:
    """Tests for DragonflyRunner."""

    def test_runner_instantiates(self):
        """Runner can be instantiated."""
        runner = DragonflyRunner()
        assert runner is not None

    def test_runner_run_returns_decision(self):
        """Runner.run() returns a Decision."""
        runner = DragonflyRunner()
        situation = create_test_situation()

        result = runner.run(situation)

        assert isinstance(result, Decision)

    def test_runner_decision_has_selected_action(self):
        """Runner produces decision with selected action."""
        runner = DragonflyRunner()
        situation = create_test_situation()

        decision = runner.run(situation)

        assert decision.selected_action is not None

    def test_runner_decision_has_situation_id(self):
        """Runner produces decision with correct situation_id."""
        runner = DragonflyRunner()
        situation = create_test_situation()

        decision = runner.run(situation)

        assert decision.situation_id == situation.id

    def test_runner_decision_has_tenant_id(self):
        """Runner produces decision with correct tenant_id."""
        runner = DragonflyRunner()
        situation = create_test_situation()

        decision = runner.run(situation)

        assert decision.tenant_id == situation.tenant_id

    def test_runner_selects_reversible_action(self):
        """Runner selects reversible action over irreversible."""
        runner = DragonflyRunner()
        actions = [
            ActionSpec(name="Irreversible", description="Bad choice", reversibility="irreversible"),
            ActionSpec(name="Reversible", description="Good choice", reversibility="reversible"),
        ]
        situation = create_test_situation(actions=actions)

        decision = runner.run(situation)

        assert decision.selected_action.name == "Reversible"

    def test_runner_respects_hard_constraints(self):
        """Runner respects hard constraints from agents."""
        runner = DragonflyRunner()
        # Create a situation with a deadline and a flexible action
        obs = Observation(
            content="Deadline is Friday",
            source="manager",
            reliability="high",
        )
        actions = [
            ActionSpec(
                name="Flexible",
                description="Flexible timing",
                reversibility="reversible",
                time_sensitivity="flexible",
            ),
            ActionSpec(
                name="Immediate",
                description="Do it now",
                reversibility="reversible",
                time_sensitivity="immediate",
            ),
        ]
        situation = create_test_situation(observations=[obs], actions=actions)

        decision = runner.run(situation)

        # The flexible action should be constrained by deadline
        # The immediate action should be selected
        assert decision.selected_action.name == "Immediate"

    def test_runner_produces_monitoring_for_warnings(self):
        """Runner includes monitoring triggers for high-severity warnings."""
        runner = DragonflyRunner()
        obs = Observation(
            content="Unreliable rumor",
            source="social_media",
            reliability="low",
        )
        situation = create_test_situation(observations=[obs], stakes="high")

        decision = runner.run(situation)

        # Low reliability in high stakes should generate monitoring
        assert len(decision.monitoring) >= 1

    def test_runner_assessments_used_populated(self):
        """Runner populates assessments_used in decision."""
        runner = DragonflyRunner()
        actions = [
            ActionSpec(name="Test", description="Test", reversibility="irreversible"),
        ]
        situation = create_test_situation(actions=actions, stakes="high")

        decision = runner.run(situation)

        # Should have assessments from all three agents
        assert len(decision.assessments_used) >= 1


class TestGetRunner:
    """Tests for get_runner singleton."""

    def test_get_runner_returns_runner(self):
        """get_runner() returns a DragonflyRunner."""
        runner = get_runner()
        assert isinstance(runner, DragonflyRunner)

    def test_get_runner_returns_same_instance(self):
        """get_runner() returns the same instance."""
        runner1 = get_runner()
        runner2 = get_runner()
        assert runner1 is runner2


class TestRunnerPerformance:
    """Performance tests for the runner."""

    def test_decision_under_500ms(self):
        """Decision is made in under 500ms (no LLM)."""
        import time

        runner = DragonflyRunner()
        situation = create_test_situation()

        start = time.perf_counter()
        runner.run(situation)
        elapsed = time.perf_counter() - start

        assert elapsed < 0.5, f"Decision took {elapsed:.3f}s, expected < 0.5s"
