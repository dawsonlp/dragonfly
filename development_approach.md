# Dragonfly Agent Framework - Development Approach

## Technical Decisions (ADR-Style)

### TD-1: Protocol Alignment with Mímir

**Decision**: Dragonfly will reuse Mímir's protocol conventions (envelope style, IDs, provenance expectations, tenant scoping) rather than inventing a parallel schema.

**Implication**: Core types should be representable as Mímir artifacts/relations/provenance events without lossy mapping.

**Boundary**: The core defines canonical types; the Mímir adapter translates to/from Mímir wire format.

### TD-2: Python Runtime

**Decision**: 
- Library compatibility baseline: Python ≥ 3.13
- Production/runtime target: Python 3.14

**Implication**: Use typing features aggressively (type aliases, `typing.Protocol`, `TypedDict`/dataclasses), and keep dependencies that lag Python versions out of the core.

### TD-3: Service Tooling Selection

**Decision**: Use:
- **FastAPI** for service boundary (HTTP)
- **httpx** for outbound calls (to Mímir, later tools)
- **LangGraph** for orchestration around the core (graph execution, state machine)

**Constraint**: These are service-layer dependencies only. The core must have zero dependency on FastAPI/httpx/langgraph.

### TD-4: Core Purity Rule

**Decision**: The core:
- Must be deterministic given inputs
- Must not perform I/O
- Must not call LLMs or tools
- Must not know about HTTP, databases, files, queues, or streaming

**Allowed**: The core may depend on:
- Standard library only
- Pydantic only if wanted for type validation (preference: keep pydantic out and use dataclasses + typing)

## Repository Structure

```
dragonfly/
├── pyproject.toml
├── requirements.md
├── design.md
├── development_approach.md
├── design_decisions.md
│
├── src/
│   └── dragonfly/
│       ├── __init__.py
│       │
│       ├── core/                    # Pure Python, stdlib only
│       │   ├── __init__.py
│       │   ├── types.py             # Situation, Assessment, Decision, etc.
│       │   ├── nodes.py             # Node Protocols + reference nodes
│       │   ├── synth.py             # Synthesis / robustness scoring
│       │   └── graph.py             # Pure graph spec (adjacency)
│       │
│       ├── adapters/
│       │   ├── __init__.py
│       │   └── mimir/
│       │       ├── __init__.py
│       │       ├── client.py        # httpx client
│       │       └── mapping.py       # core <-> mimir wire
│       │
│       └── service/
│           ├── __init__.py
│           ├── api/
│           │   ├── __init__.py
│           │   ├── main.py          # FastAPI app
│           │   ├── routes.py        # Endpoint definitions
│           │   └── deps.py          # Dependency injection
│           │
│           └── runtime/
│               ├── __init__.py
│               └── langgraph_runner.py  # Executes core graph
│
└── tests/
    ├── __init__.py
    ├── unit/
    │   ├── __init__.py
    │   └── core/
    │       ├── __init__.py
    │       ├── test_types.py
    │       ├── test_nodes.py
    │       ├── test_synth.py
    │       └── test_graph.py
    │
    └── integration/
        ├── __init__.py
        ├── test_mimir_adapter.py
        └── test_api.py
```

**Boundary Enforcement Rule**: `core/` must import nothing outside `core/` and stdlib. CI test should enforce this via import scanning.

## Phase 1: Shakeout Agent

Build a minimal agent to validate design decisions before full Dragonfly implementation.

### Minimal Agent: "Robust Choice from Constraints"

**Purpose**: Exercise the architecture without full complexity.

**Inputs**: Situation with goal, observations, and candidate_actions

**Processing**:
1. **ConstraintAgent** → emits hard constraints + failure modes
2. **StabilityAgent** → emits reversibility + minimax-regret heuristics  
3. **RealityCheckAgent** → emits contradictions / missing info

**Synthesis**: Chooses an action that:
- Violates zero hard constraints
- Maximizes "reversibility score"
- Minimizes worst-case regret proxy

**Outputs**: Decision with selected_action, rationale, and monitoring_triggers

### What This Validates

- Protocol structure correctness
- Assessment typing
- Synthesis mechanics
- Mímir persistence (optional in phase 1)
- Core isolation from service layer

### Small Enough To Iterate

The shakeout agent is small enough that pieces can be replaced without sunk cost as the design evolves.

## Implementation Order

### Step 1: Core Types (`core/types.py`)
- Dataclasses for Situation, Observation, Assessment, Decision, ActionSpec
- Include IDs early (uuid) to force discipline and enable later Mímir integration
- All types include tenant_id as required field

### Step 2: Node Protocol & Initial Nodes (`core/nodes.py`)
- Protocol definition for EpistemicNode
- Implement 2-3 nodes with deterministic logic (no LLM):
  - ConstraintAgent
  - StabilityAgent
  - RealityCheckAgent

### Step 3: Synthesis Algorithm (`core/synth.py`)
- Constraint filtering (eliminate actions violating hard constraints)
- Robustness scoring (reversibility, minimax regret proxy)
- Decision selection

### Step 4: Graph Specification (`core/graph.py`)
- Pure adjacency definition
- Node execution ordering
- No LangGraph dependency in core

### Step 5: LangGraph Runner (`service/runtime/langgraph_runner.py`)
- Glue layer: run node set, collect assessments, call synthesis
- LangGraph state management
- Tracing/logging (service concern)

### Step 6: FastAPI Service (`service/api/`)
- POST /decide endpoint
- Takes Situation-like payload, returns Decision
- Dependency injection for ports

### Step 7: Mímir Adapter (optional early, but stub it)
- adapters/mimir/client.py - httpx wrapper
- adapters/mimir/mapping.py - core ↔ Mímir artifact translation
- Tenant header handling (X-Tenant-ID)
- Write artifacts for Situation/Assessments/Decision with provenance links

## LangGraph Integration Pattern

LangGraph sits in the service layer, not in core.

### How It Works

1. **Core defines nodes as callables** that take a Situation and optional memory_snapshot, returning a list of Assessments

2. **Service layer wraps them in LangGraph nodes** and handles:
   - State passing
   - Retries/timeouts (service concern)
   - Tracing/logging (service concern)

3. **LangGraph state** contains:
   - situation
   - assessments (aggregated)
   - decision
   - mimir_refs (if enabled)

4. **Core never sees the state container** - it only receives typed inputs and returns typed outputs.

## Port Design Pattern

The core never calls outward. It can only:

1. **Request information** via a SensePort (pull-based)
2. **Emit desired actions** via an ActPort (declarative)
3. **Read/write** via MemoryPort

This keeps it deployable in:
- Synchronous requests (web)
- Async workers (automation)
- Interactive chat
- MCP tools

Without rewriting the core.

## Testing Strategy

### Unit Tests (Fast, Isolated)
- Test core types serialization/deserialization
- Test individual nodes with mock situations
- Test synthesis with mock assessments
- Test graph composition

### Integration Tests
- Test Mímir adapter against real/mock Mímir
- Test FastAPI endpoints end-to-end
- Test LangGraph runner with full pipeline

### Boundary Tests
- **Import scan test**: Verify `core/` imports nothing outside core + stdlib
- Run in CI to prevent boundary violations

## Development Process

Following the project's established development process:

1. **Clarify requirements and design** with the user
2. **Document design** in design documents
3. **Implement test** first
4. **Implement code**
5. **Test**
6. **Document current design**
7. **Add and commit** correct files to GitHub

## Next Steps

1. Create pyproject.toml with dependencies split by layer
2. Implement core/types.py 
3. Write tests for types
4. Implement shakeout nodes (ConstraintAgent, StabilityAgent, RealityCheckAgent)
5. Write tests for nodes
6. Implement synthesis
7. Wire up with LangGraph runner
8. Create FastAPI endpoint
9. Test end-to-end
10. Add Mímir persistence
