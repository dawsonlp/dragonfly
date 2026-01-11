# Phase 1 Test Plan

## Overview

This document defines the testing strategy for Phase 1 of the Dragonfly Agent Framework. All tests follow the test-first development approach: write tests before implementation.

## Test Categories

| Category | Location | Purpose | Speed |
|----------|----------|---------|-------|
| Unit Tests | `tests/unit/` | Test individual components in isolation | Fast (<1s) |
| Integration Tests | `tests/integration/` | Test component interactions | Medium (<5s) |
| Boundary Tests | `tests/unit/core/` | Verify architectural constraints | Fast |

## Test Infrastructure

### Dependencies

```toml
[project.optional-dependencies]
dev = [
    "pytest>=8.3.0",
    "pytest-asyncio>=0.24.0",
    "pytest-cov>=6.0.0",
]
```

### Configuration (pyproject.toml)

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
markers = [
    "unit: Unit tests (fast, isolated)",
    "integration: Integration tests (may use real services)",
    "boundary: Architectural boundary tests",
]
```

### Running Tests

```bash
# All tests
pytest

# Unit tests only
pytest tests/unit/ -v

# Integration tests only
pytest tests/integration/ -v

# With coverage
pytest --cov=src/dragonfly --cov-report=html

# Specific module
pytest tests/unit/core/test_types.py -v
```

---

## Unit Tests

### UT-1: Core Types (`tests/unit/core/test_types.py`)

#### UT-1.1: Observation

| Test ID | Description | Expected Result |
|---------|-------------|-----------------|
| UT-1.1.1 | Create Observation with all required fields | Observation created successfully |
| UT-1.1.2 | Create Observation without content | Raises TypeError |
| UT-1.1.3 | Create Observation with invalid reliability | Raises ValueError |
| UT-1.1.4 | Observation has auto-generated UUID | id is valid UUID |
| UT-1.1.5 | Observation has auto-generated timestamp | timestamp is datetime |
| UT-1.1.6 | Observation serializes to dict | dict contains all fields |
| UT-1.1.7 | Observation deserializes from dict | Observation matches original |

```python
def test_observation_creation():
    obs = Observation(
        content="Market is volatile",
        source="analyst_report",
        reliability="high"
    )
    assert obs.content == "Market is volatile"
    assert obs.source == "analyst_report"
    assert obs.reliability == "high"
    assert isinstance(obs.id, UUID)
    assert isinstance(obs.timestamp, datetime)

def test_observation_missing_content():
    with pytest.raises(TypeError):
        Observation(source="test", reliability="high")

def test_observation_invalid_reliability():
    with pytest.raises(ValueError):
        Observation(content="test", source="test", reliability="invalid")
```

#### UT-1.2: ActionSpec

| Test ID | Description | Expected Result |
|---------|-------------|-----------------|
| UT-1.2.1 | Create ActionSpec with required fields | ActionSpec created |
| UT-1.2.2 | Create ActionSpec with optional time_sensitivity | ActionSpec created with field |
| UT-1.2.3 | ActionSpec without time_sensitivity | time_sensitivity is None |
| UT-1.2.4 | ActionSpec with invalid reversibility | Raises ValueError |
| UT-1.2.5 | ActionSpec serializes correctly | dict contains all fields |

```python
def test_action_spec_creation():
    action = ActionSpec(
        name="Wait",
        description="Wait for more information",
        reversibility="reversible"
    )
    assert action.name == "Wait"
    assert action.reversibility == "reversible"
    assert action.time_sensitivity is None

def test_action_spec_with_time_sensitivity():
    action = ActionSpec(
        name="Act now",
        description="Take immediate action",
        reversibility="irreversible",
        time_sensitivity="immediate"
    )
    assert action.time_sensitivity == "immediate"
```

#### UT-1.3: Situation

| Test ID | Description | Expected Result |
|---------|-------------|-----------------|
| UT-1.3.1 | Create Situation with all required fields | Situation created |
| UT-1.3.2 | Situation requires tenant_id | Raises TypeError without |
| UT-1.3.3 | Situation contains observations list | List accessible |
| UT-1.3.4 | Situation contains candidate_actions list | List accessible |
| UT-1.3.5 | Situation context is optional | Defaults to empty dict |
| UT-1.3.6 | Situation serializes with nested objects | Full dict structure |

```python
def test_situation_creation():
    obs = Observation(content="test", source="test", reliability="medium")
    action = ActionSpec(name="test", description="test", reversibility="reversible")
    
    situation = Situation(
        tenant_id="tenant-1",
        goal="Make a decision",
        time_horizon="near",
        stakes="medium",
        observations=[obs],
        candidate_actions=[action]
    )
    
    assert situation.tenant_id == "tenant-1"
    assert len(situation.observations) == 1
    assert len(situation.candidate_actions) == 1
```

#### UT-1.4: Assessment

| Test ID | Description | Expected Result |
|---------|-------------|-----------------|
| UT-1.4.1 | Create Assessment with required fields | Assessment created |
| UT-1.4.2 | Assessment requires situation_id | Raises TypeError without |
| UT-1.4.3 | Assessment action_id is optional | None when not provided |
| UT-1.4.4 | Assessment is_hard_constraint is required | Raises TypeError without |
| UT-1.4.5 | Assessment recommended_tests is optional | Empty list when not provided |

```python
def test_assessment_creation():
    situation_id = uuid4()
    
    assessment = Assessment(
        situation_id=situation_id,
        agent_type="constraint",
        claim="Action violates budget constraint",
        support=[],
        confidence="high",
        severity="high",
        reversibility="irreversible",
        is_hard_constraint=True
    )
    
    assert assessment.situation_id == situation_id
    assert assessment.agent_type == "constraint"
    assert assessment.is_hard_constraint is True
```

#### UT-1.5: Decision

| Test ID | Description | Expected Result |
|---------|-------------|-----------------|
| UT-1.5.1 | Create Decision with required fields | Decision created |
| UT-1.5.2 | Decision requires selected_action | Raises TypeError without |
| UT-1.5.3 | Decision contains monitoring list | List accessible |
| UT-1.5.4 | Decision serializes completely | Full dict with nested objects |

---

### UT-2: Node Protocol & Agents (`tests/unit/core/test_nodes.py`)

#### UT-2.1: Protocol Compliance

| Test ID | Description | Expected Result |
|---------|-------------|-----------------|
| UT-2.1.1 | ConstraintAgent implements EpistemicNode | isinstance check passes |
| UT-2.1.2 | StabilityAgent implements EpistemicNode | isinstance check passes |
| UT-2.1.3 | RealityCheckAgent implements EpistemicNode | isinstance check passes |

```python
def test_constraint_agent_implements_protocol():
    agent = ConstraintAgent()
    assert isinstance(agent, EpistemicNode)
    assert agent.agent_type == "constraint"

def test_stability_agent_implements_protocol():
    agent = StabilityAgent()
    assert isinstance(agent, EpistemicNode)
    assert agent.agent_type == "stability"
```

#### UT-2.2: ConstraintAgent

| Test ID | Description | Expected Result |
|---------|-------------|-----------------|
| UT-2.2.1 | assess() returns list[Assessment] | List of Assessment objects |
| UT-2.2.2 | Detects deadline constraint | Hard constraint assessment |
| UT-2.2.3 | Detects irreversible action in high stakes | Warning assessment |
| UT-2.2.4 | No constraints in simple situation | Empty or informational assessments |
| UT-2.2.5 | All assessments have agent_type="constraint" | Correct type on all |

```python
def test_constraint_agent_detects_deadline():
    """Deadline observation should flag flexible actions."""
    obs = Observation(
        content="Deadline is Friday",
        source="manager",
        reliability="high"
    )
    action = ActionSpec(
        name="Research more",
        description="Gather more information",
        reversibility="reversible",
        time_sensitivity="flexible"
    )
    situation = create_situation(observations=[obs], actions=[action])
    
    agent = ConstraintAgent()
    assessments = agent.assess(situation)
    
    hard_constraints = [a for a in assessments if a.is_hard_constraint]
    assert len(hard_constraints) >= 1
    assert any("deadline" in a.claim.lower() for a in hard_constraints)
```

#### UT-2.3: StabilityAgent

| Test ID | Description | Expected Result |
|---------|-------------|-----------------|
| UT-2.3.1 | assess() returns list[Assessment] | List of Assessment objects |
| UT-2.3.2 | Scores reversible actions higher | Assessment indicates preference |
| UT-2.3.3 | Warns about irreversible actions | Assessment with severity |
| UT-2.3.4 | All assessments have agent_type="stability" | Correct type on all |

```python
def test_stability_agent_prefers_reversible():
    """Reversible actions should be scored higher."""
    reversible = ActionSpec(name="A", description="Reversible", reversibility="reversible")
    irreversible = ActionSpec(name="B", description="Irreversible", reversibility="irreversible")
    
    situation = create_situation(actions=[reversible, irreversible])
    
    agent = StabilityAgent()
    assessments = agent.assess(situation)
    
    # Should warn about irreversible action
    warnings = [a for a in assessments if a.action_id == irreversible.id]
    assert len(warnings) >= 1
```

#### UT-2.4: RealityCheckAgent

| Test ID | Description | Expected Result |
|---------|-------------|-----------------|
| UT-2.4.1 | assess() returns list[Assessment] | List of Assessment objects |
| UT-2.4.2 | Flags low-reliability in high-stakes | Warning assessment |
| UT-2.4.3 | Flags conflicting observations | Warning assessment |
| UT-2.4.4 | All assessments have agent_type="reality_check" | Correct type on all |

```python
def test_reality_check_flags_low_reliability():
    """Low reliability observation in high stakes should be flagged."""
    obs = Observation(
        content="Market will go up",
        source="social_media",
        reliability="low"
    )
    situation = create_situation(observations=[obs], stakes="high")
    
    agent = RealityCheckAgent()
    assessments = agent.assess(situation)
    
    warnings = [a for a in assessments if a.severity in ("medium", "high")]
    assert len(warnings) >= 1
```

---

### UT-3: Synthesis Algorithm (`tests/unit/core/test_synth.py`)

#### UT-3.1: Constraint Filtering

| Test ID | Description | Expected Result |
|---------|-------------|-----------------|
| UT-3.1.1 | filter_by_constraints removes violated actions | Only valid actions remain |
| UT-3.1.2 | Actions without violations pass through | All pass |
| UT-3.1.3 | All actions violated returns empty | Empty list |
| UT-3.1.4 | Non-hard constraints don't filter | Actions pass |

```python
def test_filter_removes_violated_actions():
    action_a = ActionSpec(name="A", description="A", reversibility="reversible")
    action_b = ActionSpec(name="B", description="B", reversibility="reversible")
    
    assessments = [
        Assessment(
            situation_id=uuid4(),
            agent_type="constraint",
            claim="Action A violates constraint",
            action_id=action_a.id,
            is_hard_constraint=True,
            support=[], confidence="high", severity="high", reversibility="irreversible"
        )
    ]
    
    surviving = filter_by_constraints([action_a, action_b], assessments)
    
    assert action_a not in surviving
    assert action_b in surviving
```

#### UT-3.2: Robustness Scoring

| Test ID | Description | Expected Result |
|---------|-------------|-----------------|
| UT-3.2.1 | Reversible action scores higher than irreversible | Higher score |
| UT-3.2.2 | Action with warnings scores lower | Lower than clean |
| UT-3.2.3 | Score is between 0 and 1 | 0 <= score <= 1 |

```python
def test_robustness_score_prefers_reversible():
    reversible = ActionSpec(name="A", description="A", reversibility="reversible")
    irreversible = ActionSpec(name="B", description="B", reversibility="irreversible")
    
    score_a = score_robustness(reversible, [])
    score_b = score_robustness(irreversible, [])
    
    assert score_a > score_b
```

#### UT-3.3: Action Selection

| Test ID | Description | Expected Result |
|---------|-------------|-----------------|
| UT-3.3.1 | Selects highest scoring action | Best action returned |
| UT-3.3.2 | Tied scores selects first | Deterministic selection |
| UT-3.3.3 | Single action returns that action | Same action |

```python
def test_select_action_chooses_best():
    actions = [
        ActionSpec(name="A", description="A", reversibility="irreversible"),
        ActionSpec(name="B", description="B", reversibility="reversible"),
        ActionSpec(name="C", description="C", reversibility="costly"),
    ]
    
    selected = select_action(actions, [])
    
    assert selected.name == "B"  # Reversible has highest score
```

#### UT-3.4: Monitoring Trigger Generation

| Test ID | Description | Expected Result |
|---------|-------------|-----------------|
| UT-3.4.1 | High severity assessments create triggers | Triggers generated |
| UT-3.4.2 | Low severity don't create triggers | No triggers |
| UT-3.4.3 | Hard constraints don't create triggers | Only warnings do |

```python
def test_monitoring_from_high_severity():
    assessment = Assessment(
        situation_id=uuid4(),
        agent_type="stability",
        claim="Market may shift",
        is_hard_constraint=False,
        severity="high",
        support=[], confidence="medium", reversibility="reversible"
    )
    
    triggers = generate_monitoring([assessment])
    
    assert len(triggers) >= 1
    assert "Market" in triggers[0].condition
```

#### UT-3.5: Full Synthesis

| Test ID | Description | Expected Result |
|---------|-------------|-----------------|
| UT-3.5.1 | synthesize returns Decision | Valid Decision object |
| UT-3.5.2 | Decision has selected_action | ActionSpec present |
| UT-3.5.3 | Decision has robustness_basis | Non-empty string |
| UT-3.5.4 | Decision has assessments_used | List of UUIDs |

```python
def test_synthesize_returns_decision():
    situation = create_test_situation()
    assessments = [
        create_assessment(situation.id, "constraint"),
        create_assessment(situation.id, "stability"),
    ]
    
    decision = synthesize(situation, assessments)
    
    assert isinstance(decision, Decision)
    assert decision.selected_action is not None
    assert decision.robustness_basis != ""
    assert decision.situation_id == situation.id
```

---

### UT-4: Graph Specification (`tests/unit/core/test_graph.py`)

| Test ID | Description | Expected Result |
|---------|-------------|-----------------|
| UT-4.1 | GraphSpec creates with nodes and adjacency | Valid GraphSpec |
| UT-4.2 | PHASE1_GRAPH has 4 nodes | constraint, stability, reality_check, synthesis |
| UT-4.3 | All agents point to synthesis | Adjacency correct |
| UT-4.4 | Synthesis is terminal | Empty successor list |

```python
def test_phase1_graph_structure():
    graph = PHASE1_GRAPH
    
    assert len(graph.nodes) == 4
    assert "synthesis" in graph.nodes
    assert graph.adjacency["constraint"] == ["synthesis"]
    assert graph.adjacency["synthesis"] == []
```

---

## Boundary Tests

### BT-1: Core Import Isolation (`tests/unit/core/test_imports.py`)

| Test ID | Description | Expected Result |
|---------|-------------|-----------------|
| BT-1.1 | core/types.py has no external imports | Only stdlib + dragonfly.core |
| BT-1.2 | core/nodes.py has no external imports | Only stdlib + dragonfly.core |
| BT-1.3 | core/synth.py has no external imports | Only stdlib + dragonfly.core |
| BT-1.4 | core/graph.py has no external imports | Only stdlib + dragonfly.core |

```python
import ast
import sys
from pathlib import Path

def test_core_imports():
    """Verify core/ only imports from stdlib and dragonfly.core."""
    core_path = Path("src/dragonfly/core")
    stdlib_modules = set(sys.stdlib_module_names)
    
    for py_file in core_path.glob("*.py"):
        if py_file.name == "__init__.py":
            continue
            
        tree = ast.parse(py_file.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module = alias.name.split('.')[0]
                    assert module in stdlib_modules or module == "dragonfly", \
                        f"{py_file.name} imports external module: {module}"
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    module = node.module.split('.')[0]
                    assert module in stdlib_modules or module == "dragonfly", \
                        f"{py_file.name} imports from external module: {module}"
```

---

## Integration Tests

### IT-1: LangGraph Runner (`tests/integration/test_langgraph_runner.py`)

| Test ID | Description | Expected Result |
|---------|-------------|-----------------|
| IT-1.1 | Runner executes all agents | All assessments collected |
| IT-1.2 | Runner calls synthesis | Decision returned |
| IT-1.3 | State propagates correctly | Assessments accumulate |
| IT-1.4 | Runner handles empty observations | Still produces decision |

```python
def test_runner_executes_all_agents():
    situation = create_test_situation()
    
    decision = runner.run(situation)
    
    # Decision should reference assessments from all agents
    assert decision is not None
    assert decision.selected_action is not None
```

### IT-2: FastAPI Service (`tests/integration/test_api.py`)

| Test ID | Description | Expected Result |
|---------|-------------|-----------------|
| IT-2.1 | POST /decide returns 200 | Valid response |
| IT-2.2 | Response contains decision fields | All required fields |
| IT-2.3 | Invalid request returns 422 | Validation error |
| IT-2.4 | Missing tenant_id returns 422 | Required field error |
| IT-2.5 | Health check returns 200 | Service healthy |

```python
from fastapi.testclient import TestClient
from dragonfly.service.api.main import app

client = TestClient(app)

def test_decide_endpoint():
    response = client.post("/decide", json={
        "tenant_id": "test-tenant",
        "goal": "Test decision",
        "time_horizon": "near",
        "stakes": "medium",
        "observations": [
            {"content": "Test observation", "source": "test", "reliability": "medium"}
        ],
        "candidate_actions": [
            {"name": "Action A", "description": "Test action", "reversibility": "reversible"}
        ]
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "selected_action" in data
    assert "robustness_basis" in data

def test_decide_missing_tenant():
    response = client.post("/decide", json={
        "goal": "Test",
        "time_horizon": "near",
        "stakes": "medium",
        "observations": [],
        "candidate_actions": []
    })
    
    assert response.status_code == 422
```

### IT-3: Performance Test (`tests/integration/test_performance.py`)

| Test ID | Description | Expected Result |
|---------|-------------|-----------------|
| IT-3.1 | Decision in < 500ms | Elapsed time < 0.5s |
| IT-3.2 | 10 concurrent requests complete | All succeed |

```python
import time

def test_decision_under_500ms():
    situation = create_test_situation()
    
    start = time.perf_counter()
    decision = runner.run(situation)
    elapsed = time.perf_counter() - start
    
    assert elapsed < 0.5, f"Decision took {elapsed:.3f}s, expected < 0.5s"
```

---

## Test Fixtures

### Common Fixtures (`tests/conftest.py`)

```python
import pytest
from uuid import uuid4
from datetime import datetime, UTC
from dragonfly.core.types import (
    Observation, ActionSpec, Situation, Assessment
)

@pytest.fixture
def sample_observation():
    return Observation(
        content="Market conditions are favorable",
        source="analyst",
        reliability="medium"
    )

@pytest.fixture
def sample_action():
    return ActionSpec(
        name="Proceed",
        description="Proceed with the plan",
        reversibility="reversible"
    )

@pytest.fixture
def sample_situation(sample_observation, sample_action):
    return Situation(
        tenant_id="test-tenant",
        goal="Make a strategic decision",
        time_horizon="near",
        stakes="medium",
        observations=[sample_observation],
        candidate_actions=[sample_action]
    )

def create_situation(
    observations=None,
    actions=None,
    stakes="medium",
    time_horizon="near"
):
    """Factory for test situations."""
    return Situation(
        tenant_id="test-tenant",
        goal="Test goal",
        time_horizon=time_horizon,
        stakes=stakes,
        observations=observations or [],
        candidate_actions=actions or []
    )

def create_assessment(situation_id, agent_type, **kwargs):
    """Factory for test assessments."""
    defaults = {
        "claim": f"Test {agent_type} assessment",
        "support": [],
        "confidence": "medium",
        "severity": "medium",
        "reversibility": "reversible",
        "is_hard_constraint": False
    }
    defaults.update(kwargs)
    return Assessment(
        situation_id=situation_id,
        agent_type=agent_type,
        **defaults
    )
```

---

## Test Coverage Requirements

| Module | Minimum Coverage |
|--------|-----------------|
| core/types.py | 90% |
| core/nodes.py | 85% |
| core/synth.py | 90% |
| core/graph.py | 95% |
| service/runtime/ | 80% |
| service/api/ | 80% |

### Running Coverage

```bash
pytest --cov=src/dragonfly --cov-report=html --cov-fail-under=85
```

---

## CI Integration

### GitHub Actions Workflow

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.13'
      - run: pip install -e ".[dev]"
      - run: pytest --cov=src/dragonfly --cov-fail-under=85
      - run: mypy src/dragonfly/core/
```

---

## Test Maintenance

### Adding New Tests

1. Follow naming convention: `test_<function>_<scenario>`
2. Use fixtures for common setup
3. One assertion per test when possible
4. Document expected behavior in docstring

### Test Review Checklist

- [ ] Test name describes what is being tested
- [ ] Test has clear assertion
- [ ] Test is independent (no order dependency)
- [ ] Test is fast (< 1s for unit tests)
- [ ] Test uses fixtures appropriately
