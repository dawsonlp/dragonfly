"""Integration tests for the FastAPI service."""

import pytest
from fastapi.testclient import TestClient

from dragonfly.service.api.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestHealthEndpoint:
    """Tests for health endpoint."""

    def test_health_returns_200(self, client):
        """Health endpoint returns 200."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200

    def test_health_returns_healthy_status(self, client):
        """Health endpoint returns healthy status."""
        response = client.get("/api/v1/health")
        assert response.json()["status"] == "healthy"


class TestRootEndpoint:
    """Tests for root endpoint."""

    def test_root_returns_200(self, client):
        """Root endpoint returns 200."""
        response = client.get("/")
        assert response.status_code == 200

    def test_root_returns_api_info(self, client):
        """Root endpoint returns API info."""
        response = client.get("/")
        data = response.json()
        assert data["name"] == "Dragonfly Agent Framework"
        assert data["version"] == "0.1.0"


class TestDecideEndpoint:
    """Tests for /decide endpoint."""

    def test_decide_returns_200(self, client):
        """Decide endpoint returns 200 for valid request."""
        request = {
            "tenant_id": "test-tenant",
            "goal": "Make a test decision",
            "time_horizon": "near",
            "stakes": "medium",
            "observations": [
                {
                    "content": "Test observation",
                    "source": "test",
                    "reliability": "high",
                }
            ],
            "candidate_actions": [
                {
                    "name": "Action A",
                    "description": "A reversible action",
                    "reversibility": "reversible",
                }
            ],
        }

        response = client.post("/api/v1/decide", json=request)
        assert response.status_code == 200

    def test_decide_returns_decision(self, client):
        """Decide endpoint returns a decision."""
        request = {
            "tenant_id": "test-tenant",
            "goal": "Test decision",
            "time_horizon": "near",
            "stakes": "low",
            "observations": [],
            "candidate_actions": [
                {
                    "name": "Only Action",
                    "description": "The only option",
                    "reversibility": "reversible",
                }
            ],
        }

        response = client.post("/api/v1/decide", json=request)
        data = response.json()

        assert "selected_action" in data
        assert data["selected_action"]["name"] == "Only Action"

    def test_decide_has_required_fields(self, client):
        """Decision response has all required fields."""
        request = {
            "tenant_id": "test-tenant",
            "goal": "Test",
            "time_horizon": "near",
            "stakes": "medium",
            "observations": [],
            "candidate_actions": [
                {
                    "name": "Test",
                    "description": "Test",
                    "reversibility": "reversible",
                }
            ],
        }

        response = client.post("/api/v1/decide", json=request)
        data = response.json()

        assert "id" in data
        assert "situation_id" in data
        assert "tenant_id" in data
        assert "selected_action" in data
        assert "alternatives_considered" in data
        assert "robustness_basis" in data
        assert "assessments_used" in data
        assert "monitoring" in data
        assert "created_at" in data

    def test_decide_selects_reversible_over_irreversible(self, client):
        """Decide selects reversible action over irreversible."""
        request = {
            "tenant_id": "test-tenant",
            "goal": "Choose wisely",
            "time_horizon": "near",
            "stakes": "medium",
            "observations": [],
            "candidate_actions": [
                {
                    "name": "Risky",
                    "description": "Irreversible choice",
                    "reversibility": "irreversible",
                },
                {
                    "name": "Safe",
                    "description": "Reversible choice",
                    "reversibility": "reversible",
                },
            ],
        }

        response = client.post("/api/v1/decide", json=request)
        data = response.json()

        assert data["selected_action"]["name"] == "Safe"

    def test_decide_respects_hard_constraints(self, client):
        """Decide respects hard constraints from agents."""
        request = {
            "tenant_id": "test-tenant",
            "goal": "Meet the deadline",
            "time_horizon": "immediate",
            "stakes": "high",
            "observations": [
                {
                    "content": "Deadline is Friday",
                    "source": "manager",
                    "reliability": "high",
                }
            ],
            "candidate_actions": [
                {
                    "name": "Research More",
                    "description": "Flexible timing",
                    "reversibility": "reversible",
                    "time_sensitivity": "flexible",
                },
                {
                    "name": "Act Now",
                    "description": "Immediate action",
                    "reversibility": "reversible",
                    "time_sensitivity": "immediate",
                },
            ],
        }

        response = client.post("/api/v1/decide", json=request)
        data = response.json()

        # Flexible action should be constrained, immediate selected
        assert data["selected_action"]["name"] == "Act Now"

    def test_decide_returns_monitoring_for_warnings(self, client):
        """Decide includes monitoring for high-severity warnings."""
        request = {
            "tenant_id": "test-tenant",
            "goal": "Decide with unreliable info",
            "time_horizon": "near",
            "stakes": "high",
            "observations": [
                {
                    "content": "Rumor from social media",
                    "source": "twitter",
                    "reliability": "low",
                }
            ],
            "candidate_actions": [
                {
                    "name": "Proceed",
                    "description": "Go ahead",
                    "reversibility": "reversible",
                }
            ],
        }

        response = client.post("/api/v1/decide", json=request)
        data = response.json()

        # Low reliability in high stakes should generate monitoring
        assert len(data["monitoring"]) >= 1

    def test_decide_preserves_tenant_id(self, client):
        """Decide preserves tenant_id in response."""
        request = {
            "tenant_id": "my-unique-tenant",
            "goal": "Test",
            "time_horizon": "near",
            "stakes": "low",
            "observations": [],
            "candidate_actions": [
                {
                    "name": "Test",
                    "description": "Test",
                    "reversibility": "reversible",
                }
            ],
        }

        response = client.post("/api/v1/decide", json=request)
        data = response.json()

        assert data["tenant_id"] == "my-unique-tenant"

    def test_decide_returns_400_for_empty_actions(self, client):
        """Decide returns 400 for empty candidate_actions."""
        request = {
            "tenant_id": "test-tenant",
            "goal": "Test",
            "time_horizon": "near",
            "stakes": "low",
            "observations": [],
            "candidate_actions": [],
        }

        response = client.post("/api/v1/decide", json=request)
        # Should fail due to no actions to select from
        assert response.status_code in (400, 500)

    def test_decide_accepts_context(self, client):
        """Decide accepts optional context field."""
        request = {
            "tenant_id": "test-tenant",
            "goal": "Test with context",
            "time_horizon": "near",
            "stakes": "low",
            "observations": [],
            "candidate_actions": [
                {
                    "name": "Test",
                    "description": "Test",
                    "reversibility": "reversible",
                }
            ],
            "context": {"custom_field": "custom_value"},
        }

        response = client.post("/api/v1/decide", json=request)
        assert response.status_code == 200
