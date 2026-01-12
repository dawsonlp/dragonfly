"""Functional tests for the Dragonfly decision framework.

These tests verify user-visible behaviors of the decision API.
"""

import pytest
from fastapi.testclient import TestClient

from dragonfly.service.api.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


def test_prefers_reversible_action(client):
    """Framework selects reversible action over irreversible when no constraints."""
    response = client.post("/api/v1/decide", json={
        "tenant_id": "test",
        "goal": "Choose deployment strategy",
        "time_horizon": "near",
        "stakes": "medium",
        "observations": [
            {"content": "Feature is ready", "source": "ci", "reliability": "high"}
        ],
        "candidate_actions": [
            {"name": "Full rollout", "description": "Deploy to all users", "reversibility": "irreversible"},
            {"name": "Gradual rollout", "description": "Deploy to 10%", "reversibility": "reversible"},
        ]
    })
    
    assert response.status_code == 200
    decision = response.json()
    assert decision["selected_action"]["name"] == "Gradual rollout"


def test_filters_deadline_constrained_action(client):
    """Framework filters out flexible-timing actions when deadline exists."""
    response = client.post("/api/v1/decide", json={
        "tenant_id": "test",
        "goal": "Meet the deadline",
        "time_horizon": "immediate",
        "stakes": "high",
        "observations": [
            {"content": "Deadline is Friday", "source": "manager", "reliability": "high"}
        ],
        "candidate_actions": [
            {"name": "Research more", "description": "Flexible timing", "reversibility": "reversible", "time_sensitivity": "flexible"},
            {"name": "Act now", "description": "Immediate action", "reversibility": "reversible", "time_sensitivity": "immediate"},
        ]
    })
    
    assert response.status_code == 200
    decision = response.json()
    assert decision["selected_action"]["name"] == "Act now"


def test_warns_about_low_reliability(client):
    """Framework generates monitoring triggers for low-reliability info in high stakes."""
    response = client.post("/api/v1/decide", json={
        "tenant_id": "test",
        "goal": "Respond to opportunity",
        "time_horizon": "near",
        "stakes": "high",
        "observations": [
            {"content": "Competitor going bankrupt", "source": "social_media", "reliability": "low"}
        ],
        "candidate_actions": [
            {"name": "Proceed cautiously", "description": "Measured response", "reversibility": "reversible"}
        ]
    })
    
    assert response.status_code == 200
    decision = response.json()
    assert len(decision["monitoring"]) > 0


def test_handles_conflicting_observations(client):
    """Framework handles conflicting observations by choosing conservative option."""
    response = client.post("/api/v1/decide", json={
        "tenant_id": "test",
        "goal": "Plan inventory",
        "time_horizon": "near",
        "stakes": "medium",
        "observations": [
            {"content": "Demand will increase 20%", "source": "sales", "reliability": "medium"},
            {"content": "Demand will decrease 10%", "source": "market", "reliability": "medium"},
        ],
        "candidate_actions": [
            {"name": "Increase inventory", "description": "Stock up", "reversibility": "costly"},
            {"name": "Decrease inventory", "description": "Reduce stock", "reversibility": "costly"},
            {"name": "Maintain levels", "description": "Keep current", "reversibility": "reversible"},
        ]
    })
    
    assert response.status_code == 200
    decision = response.json()
    # With conflicting info, should prefer reversible option
    assert decision["selected_action"]["name"] == "Maintain levels"


def test_handles_single_action(client):
    """Framework handles edge case of single candidate action."""
    response = client.post("/api/v1/decide", json={
        "tenant_id": "test",
        "goal": "Comply with regulation",
        "time_horizon": "near",
        "stakes": "high",
        "observations": [
            {"content": "New regulation requires compliance", "source": "legal", "reliability": "high"}
        ],
        "candidate_actions": [
            {"name": "Implement compliance", "description": "Make changes", "reversibility": "costly"}
        ]
    })
    
    assert response.status_code == 200
    decision = response.json()
    assert decision["selected_action"]["name"] == "Implement compliance"
