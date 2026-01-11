"""Unit tests for core types."""

from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest

from dragonfly.core.types import (
    ActionSpec,
    Assessment,
    Decision,
    MonitoringTrigger,
    Observation,
    Situation,
)


class TestObservation:
    """Tests for Observation type."""

    def test_observation_creation_with_required_fields(self):
        """Create Observation with all required fields."""
        obs = Observation(
            content="Market is volatile",
            source="analyst_report",
            reliability="high",
        )
        assert obs.content == "Market is volatile"
        assert obs.source == "analyst_report"
        assert obs.reliability == "high"

    def test_observation_has_auto_generated_uuid(self):
        """Observation has auto-generated UUID."""
        obs = Observation(
            content="test",
            source="test",
            reliability="medium",
        )
        assert isinstance(obs.id, UUID)

    def test_observation_has_auto_generated_timestamp(self):
        """Observation has auto-generated timestamp."""
        obs = Observation(
            content="test",
            source="test",
            reliability="medium",
        )
        assert isinstance(obs.timestamp, datetime)

    def test_observation_accepts_explicit_id(self):
        """Observation accepts explicit UUID."""
        explicit_id = uuid4()
        obs = Observation(
            id=explicit_id,
            content="test",
            source="test",
            reliability="medium",
        )
        assert obs.id == explicit_id

    def test_observation_serializes_to_dict(self):
        """Observation serializes to dict."""
        obs = Observation(
            content="test content",
            source="test source",
            reliability="high",
        )
        d = obs.to_dict()
        assert d["content"] == "test content"
        assert d["source"] == "test source"
        assert d["reliability"] == "high"
        assert "id" in d
        assert "timestamp" in d

    def test_observation_deserializes_from_dict(self):
        """Observation deserializes from dict."""
        original = Observation(
            content="test",
            source="test",
            reliability="low",
        )
        d = original.to_dict()
        restored = Observation.from_dict(d)
        assert restored.id == original.id
        assert restored.content == original.content
        assert restored.reliability == original.reliability


class TestActionSpec:
    """Tests for ActionSpec type."""

    def test_action_spec_creation_with_required_fields(self):
        """Create ActionSpec with required fields."""
        action = ActionSpec(
            name="Wait",
            description="Wait for more information",
            reversibility="reversible",
        )
        assert action.name == "Wait"
        assert action.description == "Wait for more information"
        assert action.reversibility == "reversible"

    def test_action_spec_time_sensitivity_is_optional(self):
        """ActionSpec time_sensitivity is optional."""
        action = ActionSpec(
            name="test",
            description="test",
            reversibility="reversible",
        )
        assert action.time_sensitivity is None

    def test_action_spec_accepts_time_sensitivity(self):
        """ActionSpec accepts time_sensitivity."""
        action = ActionSpec(
            name="Act now",
            description="Take immediate action",
            reversibility="irreversible",
            time_sensitivity="immediate",
        )
        assert action.time_sensitivity == "immediate"

    def test_action_spec_has_auto_generated_uuid(self):
        """ActionSpec has auto-generated UUID."""
        action = ActionSpec(
            name="test",
            description="test",
            reversibility="costly",
        )
        assert isinstance(action.id, UUID)

    def test_action_spec_serializes_to_dict(self):
        """ActionSpec serializes to dict."""
        action = ActionSpec(
            name="test",
            description="test desc",
            reversibility="reversible",
            time_sensitivity="near",
        )
        d = action.to_dict()
        assert d["name"] == "test"
        assert d["reversibility"] == "reversible"
        assert d["time_sensitivity"] == "near"

    def test_action_spec_deserializes_from_dict(self):
        """ActionSpec deserializes from dict."""
        original = ActionSpec(
            name="test",
            description="test",
            reversibility="costly",
        )
        d = original.to_dict()
        restored = ActionSpec.from_dict(d)
        assert restored.id == original.id
        assert restored.name == original.name


class TestSituation:
    """Tests for Situation type."""

    def test_situation_creation_with_required_fields(self):
        """Create Situation with all required fields."""
        obs = Observation(content="test", source="test", reliability="medium")
        action = ActionSpec(name="test", description="test", reversibility="reversible")

        situation = Situation(
            tenant_id="tenant-1",
            goal="Make a decision",
            time_horizon="near",
            stakes="medium",
            observations=[obs],
            candidate_actions=[action],
        )

        assert situation.tenant_id == "tenant-1"
        assert situation.goal == "Make a decision"
        assert situation.time_horizon == "near"
        assert situation.stakes == "medium"
        assert len(situation.observations) == 1
        assert len(situation.candidate_actions) == 1

    def test_situation_has_auto_generated_uuid(self):
        """Situation has auto-generated UUID."""
        situation = Situation(
            tenant_id="tenant-1",
            goal="test",
            time_horizon="immediate",
            stakes="low",
            observations=[],
            candidate_actions=[],
        )
        assert isinstance(situation.id, UUID)

    def test_situation_has_auto_generated_timestamp(self):
        """Situation has auto-generated timestamp."""
        situation = Situation(
            tenant_id="tenant-1",
            goal="test",
            time_horizon="immediate",
            stakes="low",
            observations=[],
            candidate_actions=[],
        )
        assert isinstance(situation.created_at, datetime)

    def test_situation_context_defaults_to_empty_dict(self):
        """Situation context defaults to empty dict."""
        situation = Situation(
            tenant_id="tenant-1",
            goal="test",
            time_horizon="immediate",
            stakes="low",
            observations=[],
            candidate_actions=[],
        )
        assert situation.context == {}

    def test_situation_accepts_context(self):
        """Situation accepts context dict."""
        situation = Situation(
            tenant_id="tenant-1",
            goal="test",
            time_horizon="immediate",
            stakes="low",
            observations=[],
            candidate_actions=[],
            context={"key": "value"},
        )
        assert situation.context == {"key": "value"}

    def test_situation_serializes_to_dict(self):
        """Situation serializes to dict with nested objects."""
        obs = Observation(content="test", source="test", reliability="medium")
        action = ActionSpec(name="test", description="test", reversibility="reversible")

        situation = Situation(
            tenant_id="tenant-1",
            goal="test goal",
            time_horizon="near",
            stakes="high",
            observations=[obs],
            candidate_actions=[action],
        )

        d = situation.to_dict()
        assert d["tenant_id"] == "tenant-1"
        assert d["goal"] == "test goal"
        assert len(d["observations"]) == 1
        assert len(d["candidate_actions"]) == 1

    def test_situation_deserializes_from_dict(self):
        """Situation deserializes from dict."""
        obs = Observation(content="test", source="test", reliability="medium")
        action = ActionSpec(name="test", description="test", reversibility="reversible")

        original = Situation(
            tenant_id="tenant-1",
            goal="test",
            time_horizon="near",
            stakes="medium",
            observations=[obs],
            candidate_actions=[action],
        )

        d = original.to_dict()
        restored = Situation.from_dict(d)
        assert restored.id == original.id
        assert restored.tenant_id == original.tenant_id
        assert len(restored.observations) == 1
        assert len(restored.candidate_actions) == 1


class TestAssessment:
    """Tests for Assessment type."""

    def test_assessment_creation_with_required_fields(self):
        """Create Assessment with required fields."""
        situation_id = uuid4()

        assessment = Assessment(
            situation_id=situation_id,
            agent_type="constraint",
            claim="Action violates budget constraint",
            support=[],
            confidence="high",
            severity="high",
            reversibility="irreversible",
            is_hard_constraint=True,
        )

        assert assessment.situation_id == situation_id
        assert assessment.agent_type == "constraint"
        assert assessment.claim == "Action violates budget constraint"
        assert assessment.is_hard_constraint is True

    def test_assessment_has_auto_generated_uuid(self):
        """Assessment has auto-generated UUID."""
        assessment = Assessment(
            situation_id=uuid4(),
            agent_type="stability",
            claim="test",
            support=[],
            confidence="medium",
            severity="low",
            reversibility="reversible",
            is_hard_constraint=False,
        )
        assert isinstance(assessment.id, UUID)

    def test_assessment_action_id_is_optional(self):
        """Assessment action_id is optional."""
        assessment = Assessment(
            situation_id=uuid4(),
            agent_type="constraint",
            claim="test",
            support=[],
            confidence="medium",
            severity="medium",
            reversibility="reversible",
            is_hard_constraint=False,
        )
        assert assessment.action_id is None

    def test_assessment_accepts_action_id(self):
        """Assessment accepts action_id."""
        action_id = uuid4()
        assessment = Assessment(
            situation_id=uuid4(),
            agent_type="constraint",
            claim="test",
            support=[],
            confidence="medium",
            severity="medium",
            reversibility="reversible",
            is_hard_constraint=False,
            action_id=action_id,
        )
        assert assessment.action_id == action_id

    def test_assessment_recommended_tests_defaults_to_empty(self):
        """Assessment recommended_tests defaults to empty list."""
        assessment = Assessment(
            situation_id=uuid4(),
            agent_type="reality_check",
            claim="test",
            support=[],
            confidence="medium",
            severity="medium",
            reversibility="reversible",
            is_hard_constraint=False,
        )
        assert assessment.recommended_tests == []

    def test_assessment_accepts_recommended_tests(self):
        """Assessment accepts recommended_tests."""
        assessment = Assessment(
            situation_id=uuid4(),
            agent_type="reality_check",
            claim="test",
            support=[],
            confidence="medium",
            severity="medium",
            reversibility="reversible",
            is_hard_constraint=False,
            recommended_tests=["Test A", "Test B"],
        )
        assert assessment.recommended_tests == ["Test A", "Test B"]

    def test_assessment_serializes_to_dict(self):
        """Assessment serializes to dict."""
        assessment = Assessment(
            situation_id=uuid4(),
            agent_type="constraint",
            claim="test claim",
            support=[],
            confidence="high",
            severity="high",
            reversibility="irreversible",
            is_hard_constraint=True,
        )
        d = assessment.to_dict()
        assert d["agent_type"] == "constraint"
        assert d["claim"] == "test claim"
        assert d["is_hard_constraint"] is True

    def test_assessment_deserializes_from_dict(self):
        """Assessment deserializes from dict."""
        original = Assessment(
            situation_id=uuid4(),
            agent_type="stability",
            claim="test",
            support=[],
            confidence="medium",
            severity="medium",
            reversibility="reversible",
            is_hard_constraint=False,
        )
        d = original.to_dict()
        restored = Assessment.from_dict(d)
        assert restored.id == original.id
        assert restored.agent_type == original.agent_type


class TestMonitoringTrigger:
    """Tests for MonitoringTrigger type."""

    def test_monitoring_trigger_creation(self):
        """Create MonitoringTrigger with required fields."""
        trigger = MonitoringTrigger(
            condition="Market shifts significantly",
            action_on_trigger="alert",
        )
        assert trigger.condition == "Market shifts significantly"
        assert trigger.action_on_trigger == "alert"

    def test_monitoring_trigger_serializes_to_dict(self):
        """MonitoringTrigger serializes to dict."""
        trigger = MonitoringTrigger(
            condition="test condition",
            action_on_trigger="re_plan",
        )
        d = trigger.to_dict()
        assert d["condition"] == "test condition"
        assert d["action_on_trigger"] == "re_plan"

    def test_monitoring_trigger_deserializes_from_dict(self):
        """MonitoringTrigger deserializes from dict."""
        original = MonitoringTrigger(
            condition="test",
            action_on_trigger="escalate",
        )
        d = original.to_dict()
        restored = MonitoringTrigger.from_dict(d)
        assert restored.condition == original.condition
        assert restored.action_on_trigger == original.action_on_trigger


class TestDecision:
    """Tests for Decision type."""

    def test_decision_creation_with_required_fields(self):
        """Create Decision with required fields."""
        situation_id = uuid4()
        action = ActionSpec(name="test", description="test", reversibility="reversible")

        decision = Decision(
            situation_id=situation_id,
            tenant_id="tenant-1",
            selected_action=action,
            alternatives_considered=[],
            robustness_basis="Action passed all constraints",
            assessments_used=[],
            monitoring=[],
        )

        assert decision.situation_id == situation_id
        assert decision.tenant_id == "tenant-1"
        assert decision.selected_action == action
        assert decision.robustness_basis == "Action passed all constraints"

    def test_decision_has_auto_generated_uuid(self):
        """Decision has auto-generated UUID."""
        action = ActionSpec(name="test", description="test", reversibility="reversible")
        decision = Decision(
            situation_id=uuid4(),
            tenant_id="tenant-1",
            selected_action=action,
            alternatives_considered=[],
            robustness_basis="test",
            assessments_used=[],
            monitoring=[],
        )
        assert isinstance(decision.id, UUID)

    def test_decision_has_auto_generated_timestamp(self):
        """Decision has auto-generated timestamp."""
        action = ActionSpec(name="test", description="test", reversibility="reversible")
        decision = Decision(
            situation_id=uuid4(),
            tenant_id="tenant-1",
            selected_action=action,
            alternatives_considered=[],
            robustness_basis="test",
            assessments_used=[],
            monitoring=[],
        )
        assert isinstance(decision.created_at, datetime)

    def test_decision_with_monitoring_triggers(self):
        """Decision accepts monitoring triggers."""
        action = ActionSpec(name="test", description="test", reversibility="reversible")
        trigger = MonitoringTrigger(condition="test", action_on_trigger="alert")

        decision = Decision(
            situation_id=uuid4(),
            tenant_id="tenant-1",
            selected_action=action,
            alternatives_considered=[],
            robustness_basis="test",
            assessments_used=[],
            monitoring=[trigger],
        )

        assert len(decision.monitoring) == 1
        assert decision.monitoring[0].condition == "test"

    def test_decision_serializes_to_dict(self):
        """Decision serializes to dict with nested objects."""
        action = ActionSpec(name="test action", description="test", reversibility="reversible")
        trigger = MonitoringTrigger(condition="test", action_on_trigger="alert")

        decision = Decision(
            situation_id=uuid4(),
            tenant_id="tenant-1",
            selected_action=action,
            alternatives_considered=[],
            robustness_basis="test basis",
            assessments_used=[],
            monitoring=[trigger],
        )

        d = decision.to_dict()
        assert d["tenant_id"] == "tenant-1"
        assert d["robustness_basis"] == "test basis"
        assert d["selected_action"]["name"] == "test action"
        assert len(d["monitoring"]) == 1

    def test_decision_deserializes_from_dict(self):
        """Decision deserializes from dict."""
        action = ActionSpec(name="test", description="test", reversibility="reversible")

        original = Decision(
            situation_id=uuid4(),
            tenant_id="tenant-1",
            selected_action=action,
            alternatives_considered=[],
            robustness_basis="test",
            assessments_used=[],
            monitoring=[],
        )

        d = original.to_dict()
        restored = Decision.from_dict(d)
        assert restored.id == original.id
        assert restored.tenant_id == original.tenant_id
        assert restored.selected_action.name == original.selected_action.name
