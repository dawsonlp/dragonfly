# Phase 1 Implementation Plan

## Overview

This document provides a step-by-step implementation guide for the Phase 1 shakeout agent. Each step follows the test-first development process established in the project guidelines.

## Prerequisites

Before starting implementation:

1. Python 3.13+ installed
2. Virtual environment created
3. Project structure initialized with `pyproject.toml`

## Step 0: Project Setup

### 0.1 Create pyproject.toml

```toml
[project]
name = "dragonfly"
version = "0.1.0"
description = "Multi-perspective decision-making agent framework"
requires-python = ">=3.13"
license = {text = "GPL-3.0-or-later"}

# Core has NO dependencies - stdlib only
dependencies = []

[project.optional-dependencies]
# Service layer dependencies
service = [
    "fastapi>=0.115.0",
    "uvicorn>=0.32.0",
    "httpx>=0.28.0",
    "langgraph>=0.2.0",
    "pydantic>=2.10.0",
]
# Development dependencies
dev = [
    "pytest>=8.3.0",
    "pytest-asyncio>=0.24.0",
    "pytest-cov>=6.0.0",
    "ruff>=0.8.0",
    "mypy>=1.13.0",
]

[build-system]
requires = ["setuptools>=75.0"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"

[tool.ruff]
line-length = 100
target-version = "py313"

[tool.mypy]
python_version = "3.13"
strict = true
```

### 0.2 Create Directory Structure

```bash
mkdir -p src/dragonfly/core
mkdir -p src/dragonfly/adapters/mimir
mkdir -p src/dragonfly/service/api
mkdir -p src/dragonfly/service/runtime
mkdir -p tests/unit/core
mkdir -p tests/integration
touch src/dragonfly/__init__.py
touch src/dragonfly/core/__init__.py
touch src/dragonfly/adapters/__init__.py
touch src/dragonfly/adapters/mimir/__init__.py
touch src/dragonfly/service/__init__.py
touch src/dragonfly/service/api/__init__.py
touch src/dragonfly/service/runtime/__init__.py
touch tests/__init__.py
touch tests/unit/__init__.py
touch tests/unit/core/__init__.py
touch tests/integration/__init__.py
```

### 0.3 Create Virtual Environment

```bash
python3.13 -m venv .venv
source .venv/bin/activate
pip install -e ".[service,dev]"
```

---

## Step 1: Core Types (`core/types.py`)

### 1.1 Design Summary

Define dataclasses for:
- `Observation` - a single observation about the world
- `ActionSpec` - a candidate action that could be taken
- `Situation` - complete context for a decision
- `Assessment` - output from an epistemic agent
- `MonitoringTrigger` - condition to watch for re-planning
- `Decision` - output of the synthesis process

### 1.2 Type Specifications

#### Enumerations (Literal types)

```python
# Reliability levels
Reliability = Literal["low", "medium", "high"]

# Time horizons
TimeHorizon = Literal["immediate", "near", "long"]

# Stakes levels
Stakes = Literal["low", "medium", "high"]

# Reversibility levels
Reversibility = Literal["reversible", "costly", "irreversible"]

# Time sensitivity (optional on ActionSpec)
TimeSensitivity = Literal["immediate", "near", "flexible"]

# Agent types (Phase 1 subset)
AgentType = Literal["constraint", "stability", "reality_check"]

# Confidence levels
Confidence = Literal["low", "medium", "high"]

# Severity levels
Severity = Literal["low", "medium", "high"]

# Monitoring trigger actions
TriggerAction = Literal["re_plan", "alert", "escalate"]
```

#### Observation

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | UUID | Yes | Unique identifier |
| content | str | Yes | What was observed |
| source | str | Yes | Where it came from |
| reliability | Reliability | Yes | low/medium/high |
| timestamp | datetime | Yes | When observed |

#### ActionSpec

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | UUID | Yes | Unique identifier |
| name | str | Yes | Action name |
| description | str | Yes | What the action does |
| reversibility | Reversibility | Yes | reversible/costly/irreversible |
| time_sensitivity | TimeSensitivity | No | immediate/near/flexible |

#### Situation

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | UUID | Yes | Unique identifier |
| tenant_id | str | Yes | Tenant isolation |
| goal | str | Yes | What we're trying to accomplish |
| time_horizon | TimeHorizon | Yes | immediate/near/long |
| stakes | Stakes | Yes | low/medium/high |
| observations | list[Observation] | Yes | Current observations |
| candidate_actions | list[ActionSpec] | Yes | Possible actions |
| context | dict[str, Any] | No | Opaque bag for adapters |
| created_at | datetime | Yes | When created |

#### Assessment

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | UUID | Yes | Unique identifier |
| situation_id | UUID | Yes | Links to parent situation |
| agent_type | AgentType | Yes | Which agent produced this |
| claim | str | Yes | Short statement |
| support | list[UUID] | Yes | References to evidence/observation IDs |
| confidence | Confidence | Yes | low/medium/high |
| severity | Severity | Yes | If violated, how bad |
| reversibility | Reversibility | Yes | How reversible if wrong |
| action_id | UUID | No | If assessment is about a specific action |
| is_hard_constraint | bool | Yes | If True, violation vetoes action |
| recommended_tests | list[str] | No | What would resolve uncertainty |
| created_at | datetime | Yes | When created |

#### MonitoringTrigger

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| condition | str | Yes | What to watch for |
| action_on_trigger | TriggerAction | Yes | re_plan/alert/escalate |

#### Decision

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | UUID | Yes | Unique identifier |
| situation_id | UUID | Yes | Links to parent situation |
| tenant_id | str | Yes | Tenant isolation |
| selected_action | ActionSpec | Yes | The chosen action |
| alternatives_considered | list[ActionSpec] | Yes | Other actions evaluated |
| robustness_basis | str | Yes | Why this action was chosen |
| assessments_used | list[UUID] | Yes | IDs of assessments informing decision |
| monitoring | list[MonitoringTrigger] | Yes | Conditions to watch |
| created_at | datetime | Yes | When created |

### 1.3 Implementation Tasks

1. Write tests first in `tests/unit/core/test_types.py`:
   - Test each type can be instantiated
   - Test required fields raise errors when missing
   - Test enum values are validated
   - Test serialization to dict (for JSON)
   - Test deserialization from dict

2. Implement `src/dragonfly/core/types.py`:
   - Use `@dataclass` decorator
   - Use `typing.Literal` for enums
   - Use `uuid.uuid4()` for default IDs
   - Use `datetime.now(UTC)` for default timestamps
   - Implement `to_dict()` and `from_dict()` methods

### 1.4 Acceptance Criteria

- [ ] All types instantiate with required fields
- [ ] Default values work (id, created_at)
- [ ] Type validation works (Literal enums)
- [ ] Serialization round-trips correctly
- [ ] No imports outside core/ and stdlib

---

## Step 2: Node Protocol & Agents (`core/nodes.py`)

### 2.1 Design Summary

Define:
- `EpistemicNode` Protocol
- `ConstraintAgent` - identifies hard constraints and failure modes
- `StabilityAgent` - identifies minimax-regret and reversibility
- `RealityCheckAgent` - identifies contradictions and missing info

### 2.2 Protocol Specification

```python
@runtime_checkable
class EpistemicNode(Protocol):
    """Protocol for epistemic agents."""
    
    @property
    def agent_type(self) -> AgentType:
        """Return the agent type identifier."""
        ...
    
    def assess(self, situation: Situation) -> list[Assessment]:
        """Analyze situation and return assessments."""
        ...
```

### 2.3 Agent Specifications

#### ConstraintAgent

**Purpose**: Identify hard constraints, failure modes, and irreversibility warnings.

**Phase 1 Logic** (deterministic, no LLM):
- Scan observations for keywords indicating constraints (e.g., "must", "cannot", "required", "forbidden")
- Flag actions with `reversibility="irreversible"` when stakes are high
- Generate hard constraint assessments for violations

**Example Rules**:
```
IF observation contains "deadline" AND action.time_sensitivity = "flexible"
THEN Assessment(is_hard_constraint=True, claim="Action may miss deadline")

IF action.reversibility = "irreversible" AND situation.stakes = "high"
THEN Assessment(is_hard_constraint=False, severity="high", claim="Irreversible action in high-stakes situation")
```

#### StabilityAgent

**Purpose**: Identify agency-preserving moves under uncertainty.

**Phase 1 Logic** (deterministic):
- Score actions by reversibility (reversible > costly > irreversible)
- Penalize actions that reduce future options
- Compute minimax-regret proxy based on reversibility

**Scoring**:
```
reversibility_score = {
    "reversible": 1.0,
    "costly": 0.5,
    "irreversible": 0.0
}
```

#### RealityCheckAgent

**Purpose**: Identify contradictions, disconfirmations, and missing information.

**Phase 1 Logic** (deterministic):
- Check for conflicting observations (same source, different claims)
- Flag low-reliability observations in high-stakes situations
- Identify when candidate actions reference entities not in observations

### 2.4 Implementation Tasks

1. Write tests first in `tests/unit/core/test_nodes.py`:
   - Test each agent returns valid assessments
   - Test constraint detection logic
   - Test stability scoring logic
   - Test reality check detection logic
   - Test Protocol compliance

2. Implement `src/dragonfly/core/nodes.py`:
   - Define `EpistemicNode` Protocol
   - Implement `ConstraintAgent` class
   - Implement `StabilityAgent` class
   - Implement `RealityCheckAgent` class

### 2.5 Acceptance Criteria

- [ ] All agents implement EpistemicNode Protocol
- [ ] Each agent returns list[Assessment]
- [ ] Assessments have correct agent_type
- [ ] Deterministic logic produces consistent results
- [ ] No imports outside core/ and stdlib

---

## Step 3: Synthesis Algorithm (`core/synth.py`)

### 3.1 Design Summary

Implement synthesis that:
1. Filters actions violating hard constraints
2. Scores remaining actions by robustness
3. Selects the best action
4. Generates monitoring triggers

### 3.2 Algorithm Specification

#### Phase 1: Filter by Hard Constraints

```
surviving_actions = []
for action in candidate_actions:
    violations = [a for a in assessments 
                  if a.action_id == action.id and a.is_hard_constraint]
    if not violations:
        surviving_actions.append(action)
```

#### Phase 2: Score by Robustness

```
def robustness_score(action, assessments) -> float:
    # Reversibility component (0-1)
    rev_score = {"reversible": 1.0, "costly": 0.5, "irreversible": 0.0}[action.reversibility]
    
    # Constraint warning component (0-1)
    warnings = [a for a in assessments 
                if a.action_id == action.id and not a.is_hard_constraint]
    warning_penalty = sum(severity_weight(w.severity) for w in warnings)
    constraint_score = max(0, 1.0 - warning_penalty)
    
    # Combined score
    return 0.6 * rev_score + 0.4 * constraint_score
```

#### Phase 3: Select Best Action

```
if not surviving_actions:
    # No action survives constraints - return most reversible with explanation
    return Decision(
        selected_action=most_reversible(candidate_actions),
        robustness_basis="No action passed all constraints; selected most reversible"
    )

best_action = max(surviving_actions, key=lambda a: robustness_score(a, assessments))
return Decision(
    selected_action=best_action,
    robustness_basis=f"Passed all constraints with robustness score {score}"
)
```

#### Phase 4: Generate Monitoring Triggers

```
triggers = []
for assessment in assessments:
    if assessment.severity == "high" and not assessment.is_hard_constraint:
        triggers.append(MonitoringTrigger(
            condition=f"Monitor: {assessment.claim}",
            action_on_trigger="alert"
        ))
```

### 3.3 Implementation Tasks

1. Write tests first in `tests/unit/core/test_synth.py`:
   - Test hard constraint filtering
   - Test robustness scoring
   - Test action selection
   - Test monitoring trigger generation
   - Test edge cases (no surviving actions, tied scores)

2. Implement `src/dragonfly/core/synth.py`:
   - `filter_by_constraints(actions, assessments) -> list[ActionSpec]`
   - `score_robustness(action, assessments) -> float`
   - `select_action(actions, assessments) -> ActionSpec`
   - `generate_monitoring(assessments) -> list[MonitoringTrigger]`
   - `synthesize(situation, assessments) -> Decision`

### 3.4 Acceptance Criteria

- [ ] Hard constraints filter correctly
- [ ] Robustness scores calculate correctly
- [ ] Best action selected consistently
- [ ] Monitoring triggers generated for high-severity warnings
- [ ] No imports outside core/ and stdlib

---

## Step 4: Graph Specification (`core/graph.py`)

### 4.1 Design Summary

Define the pure graph structure as adjacency, independent of any execution framework.

### 4.2 Graph Specification

```python
@dataclass
class GraphSpec:
    """Pure specification of agent graph."""
    nodes: list[str]  # Node names in execution order
    adjacency: dict[str, list[str]]  # node -> successors
    
# Phase 1 graph
PHASE1_GRAPH = GraphSpec(
    nodes=["constraint", "stability", "reality_check", "synthesis"],
    adjacency={
        "constraint": ["synthesis"],
        "stability": ["synthesis"],
        "reality_check": ["synthesis"],
        "synthesis": [],  # terminal
    }
)
```

### 4.3 Implementation Tasks

1. Write tests first in `tests/unit/core/test_graph.py`:
   - Test graph spec creation
   - Test node ordering
   - Test adjacency relationships

2. Implement `src/dragonfly/core/graph.py`:
   - Define `GraphSpec` dataclass
   - Define `PHASE1_GRAPH` constant
   - Utility functions for graph traversal (if needed)

### 4.4 Acceptance Criteria

- [ ] Graph spec defines node order
- [ ] Adjacency relationships correct
- [ ] No imports outside core/ and stdlib

---

## Step 5: LangGraph Runner (`service/runtime/langgraph_runner.py`)

### 5.1 Design Summary

The runner is a service-layer component that:
- Wraps core nodes in LangGraph-compatible nodes
- Manages state passing between nodes
- Collects assessments and calls synthesis
- Returns the final Decision

### 5.2 State Schema

```python
class DragonflyState(TypedDict):
    situation: Situation
    assessments: list[Assessment]
    decision: Decision | None
```

### 5.3 Implementation Tasks

1. Write tests first in `tests/unit/service/test_langgraph_runner.py`:
   - Test runner executes all nodes
   - Test state accumulates assessments
   - Test synthesis produces decision
   - Test end-to-end flow

2. Implement `src/dragonfly/service/runtime/langgraph_runner.py`:
   - Define `DragonflyState` TypedDict
   - Create node wrappers for each agent
   - Build LangGraph graph
   - Implement `run(situation) -> Decision`

### 5.4 Acceptance Criteria

- [ ] All agents executed in order
- [ ] Assessments accumulated correctly
- [ ] Synthesis called with all assessments
- [ ] Decision returned

---

## Step 6: FastAPI Service (`service/api/`)

### 6.1 Design Summary

Create a minimal HTTP API with:
- `POST /decide` - Submit situation, get decision
- Health check endpoint
- Request/response validation with Pydantic

### 6.2 API Specification

#### POST /decide

**Request Body**:
```json
{
  "tenant_id": "string",
  "goal": "string",
  "time_horizon": "immediate|near|long",
  "stakes": "low|medium|high",
  "observations": [
    {
      "content": "string",
      "source": "string",
      "reliability": "low|medium|high"
    }
  ],
  "candidate_actions": [
    {
      "name": "string",
      "description": "string",
      "reversibility": "reversible|costly|irreversible"
    }
  ]
}
```

**Response Body**:
```json
{
  "id": "uuid",
  "situation_id": "uuid",
  "selected_action": {
    "id": "uuid",
    "name": "string",
    "description": "string",
    "reversibility": "string"
  },
  "robustness_basis": "string",
  "monitoring": [
    {
      "condition": "string",
      "action_on_trigger": "string"
    }
  ]
}
```

### 6.3 Implementation Tasks

1. Write tests first in `tests/integration/test_api.py`:
   - Test POST /decide returns valid decision
   - Test validation errors return 422
   - Test health check returns 200

2. Implement:
   - `src/dragonfly/service/api/schemas.py` - Pydantic models
   - `src/dragonfly/service/api/routes.py` - Route definitions
   - `src/dragonfly/service/api/deps.py` - Dependency injection
   - `src/dragonfly/service/api/main.py` - FastAPI app

### 6.4 Acceptance Criteria

- [ ] POST /decide accepts valid situations
- [ ] Response contains valid decision
- [ ] Invalid requests return 422
- [ ] Response time < 500ms (no LLM)

---

## Step 7: Mímir Adapter (Stub)

### 7.1 Design Summary

Create a stub adapter that can be used for testing without a real Mímir instance.

### 7.2 Implementation Tasks

1. Define port interfaces in `src/dragonfly/core/ports.py`:
   - `MemoryPort` Protocol with search, get, put, relate, provenance

2. Implement stub in `src/dragonfly/adapters/mimir/stub.py`:
   - In-memory implementation of MemoryPort
   - Store artifacts in dict

3. Write tests in `tests/unit/adapters/test_mimir_stub.py`:
   - Test CRUD operations
   - Test relation creation
   - Test provenance recording

### 7.3 Acceptance Criteria

- [ ] Stub implements MemoryPort Protocol
- [ ] CRUD operations work in-memory
- [ ] Can be injected into service layer

---

## Verification Steps

After completing all steps, verify:

### 1. Core Isolation Test

Create `tests/unit/core/test_imports.py`:

```python
import ast
import importlib.util
from pathlib import Path

def test_core_has_no_external_imports():
    """Verify core/ only imports from core/ and stdlib."""
    core_path = Path("src/dragonfly/core")
    stdlib_modules = set(sys.stdlib_module_names)
    
    for py_file in core_path.glob("*.py"):
        tree = ast.parse(py_file.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module = alias.name.split('.')[0]
                    assert module in stdlib_modules or module == "dragonfly"
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    module = node.module.split('.')[0]
                    assert module in stdlib_modules or module == "dragonfly"
```

### 2. End-to-End Test

Run the full pipeline with a test scenario:

```python
def test_end_to_end():
    situation = create_test_situation()
    decision = runner.run(situation)
    
    assert decision.selected_action is not None
    assert decision.robustness_basis != ""
    assert decision.situation_id == situation.id
```

### 3. Performance Test

```python
import time

def test_decision_under_500ms():
    situation = create_test_situation()
    start = time.perf_counter()
    decision = runner.run(situation)
    elapsed = time.perf_counter() - start
    
    assert elapsed < 0.5, f"Decision took {elapsed:.2f}s"
```

---

## Development Workflow

For each step:

1. **Create branch**: `git checkout -b step-N-description`
2. **Write tests first**: Implement tests before code
3. **Run tests** (expect failures): `pytest tests/unit/core/test_X.py -v`
4. **Implement code**: Write minimal code to pass tests
5. **Run tests** (expect success): `pytest tests/unit/core/test_X.py -v`
6. **Run type checker**: `mypy src/dragonfly/core/`
7. **Run linter**: `ruff check src/dragonfly/core/`
8. **Commit**: `git commit -m "Step N: description"`
9. **Merge**: `git checkout main && git merge step-N-description`
10. **Push**: `git push origin main`

---

## Next Steps After Phase 1

Once Phase 1 is complete and validated:

1. **Add LLM-powered agents**: Replace deterministic logic with LLM calls
2. **Add OpportunityAgent**: Identify options and upside paths
3. **Add ContextSocialAgent**: Identify coordination constraints
4. **Integrate real Mímir**: Replace stub with httpx client
5. **Add Dragonfly Profiles**: Configurable tuning parameters
6. **Add continuous re-sensing**: Monitoring loop
