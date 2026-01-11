# Phase 1 Acceptance Criteria

## Overview

This document defines the acceptance criteria for Phase 1 of the Dragonfly Agent Framework. Phase 1 is complete when all criteria are met.

---

## AC-1: Core Types

### AC-1.1: All Types Implemented

**Criteria**: All Phase 1 types are defined as dataclasses in `core/types.py`.

**Verification**:
- [ ] `Observation` dataclass exists with all required fields
- [ ] `ActionSpec` dataclass exists with all required fields
- [ ] `Situation` dataclass exists with all required fields
- [ ] `Assessment` dataclass exists with all required fields
- [ ] `MonitoringTrigger` dataclass exists with all required fields
- [ ] `Decision` dataclass exists with all required fields

### AC-1.2: Type Aliases Defined

**Criteria**: All Literal type aliases are defined for constrained values.

**Verification**:
- [ ] `Reliability = Literal["low", "medium", "high"]`
- [ ] `TimeHorizon = Literal["immediate", "near", "long"]`
- [ ] `Stakes = Literal["low", "medium", "high"]`
- [ ] `Reversibility = Literal["reversible", "costly", "irreversible"]`
- [ ] `AgentType = Literal["constraint", "stability", "reality_check"]`
- [ ] `Confidence = Literal["low", "medium", "high"]`
- [ ] `Severity = Literal["low", "medium", "high"]`
- [ ] `TriggerAction = Literal["re_plan", "alert", "escalate"]`

### AC-1.3: Default Values

**Criteria**: Types have sensible defaults for auto-generated fields.

**Verification**:
- [ ] `id` defaults to `uuid4()` for all types with IDs
- [ ] `created_at` defaults to `datetime.now(UTC)` for timestamped types
- [ ] `context` defaults to empty dict `{}` in `Situation`
- [ ] `recommended_tests` defaults to empty list `[]` in `Assessment`

### AC-1.4: Serialization

**Criteria**: All types can be serialized to and from dictionaries.

**Verification**:
- [ ] `to_dict()` method works for all types
- [ ] `from_dict()` class method works for all types
- [ ] Round-trip serialization preserves all data
- [ ] UUID and datetime fields serialize to strings

---

## AC-2: Epistemic Agents

### AC-2.1: Protocol Defined

**Criteria**: `EpistemicNode` Protocol is defined with required interface.

**Verification**:
- [ ] `EpistemicNode` is a `typing.Protocol`
- [ ] `EpistemicNode` is marked `@runtime_checkable`
- [ ] Protocol defines `agent_type` property returning `AgentType`
- [ ] Protocol defines `assess(situation: Situation) -> list[Assessment]`

### AC-2.2: ConstraintAgent Implemented

**Criteria**: ConstraintAgent identifies hard constraints and failure modes.

**Verification**:
- [ ] Class implements `EpistemicNode` Protocol
- [ ] `agent_type` returns `"constraint"`
- [ ] `assess()` returns `list[Assessment]`
- [ ] Detects deadline constraints when observations mention deadlines
- [ ] Flags irreversible actions in high-stakes situations
- [ ] All returned assessments have `agent_type="constraint"`

### AC-2.3: StabilityAgent Implemented

**Criteria**: StabilityAgent identifies agency-preserving moves.

**Verification**:
- [ ] Class implements `EpistemicNode` Protocol
- [ ] `agent_type` returns `"stability"`
- [ ] `assess()` returns `list[Assessment]`
- [ ] Scores reversible actions higher
- [ ] Warns about irreversible actions
- [ ] All returned assessments have `agent_type="stability"`

### AC-2.4: RealityCheckAgent Implemented

**Criteria**: RealityCheckAgent identifies contradictions and missing info.

**Verification**:
- [ ] Class implements `EpistemicNode` Protocol
- [ ] `agent_type` returns `"reality_check"`
- [ ] `assess()` returns `list[Assessment]`
- [ ] Flags low-reliability observations in high-stakes situations
- [ ] Detects conflicting observations when present
- [ ] All returned assessments have `agent_type="reality_check"`

### AC-2.5: Deterministic Behavior

**Criteria**: All agents are deterministic (same input → same output).

**Verification**:
- [ ] No random number generation in agents
- [ ] No LLM calls in agents
- [ ] No external I/O in agents
- [ ] Running assess() twice with same situation returns identical assessments

---

## AC-3: Synthesis Algorithm

### AC-3.1: Constraint Filtering

**Criteria**: Actions violating hard constraints are eliminated.

**Verification**:
- [ ] `filter_by_constraints()` function exists
- [ ] Actions with `is_hard_constraint=True` assessments are removed
- [ ] Actions with only soft constraints (warnings) pass through
- [ ] Empty constraint list returns all actions
- [ ] All actions constrained returns empty list

### AC-3.2: Robustness Scoring

**Criteria**: Actions are scored by robustness criteria.

**Verification**:
- [ ] `score_robustness()` function exists
- [ ] Score is in range [0.0, 1.0]
- [ ] Reversible actions score higher than irreversible
- [ ] Actions with warnings score lower than clean actions
- [ ] Scoring is deterministic

### AC-3.3: Action Selection

**Criteria**: Best action is selected based on robustness score.

**Verification**:
- [ ] `select_action()` function exists
- [ ] Highest scoring action is selected
- [ ] Tied scores are resolved deterministically (first wins)
- [ ] Single action case returns that action
- [ ] No surviving actions case is handled gracefully

### AC-3.4: Monitoring Generation

**Criteria**: Monitoring triggers are generated for high-severity warnings.

**Verification**:
- [ ] `generate_monitoring()` function exists
- [ ] High-severity assessments generate triggers
- [ ] Low-severity assessments do not generate triggers
- [ ] Hard constraints do not generate triggers (already filtered)
- [ ] Triggers have appropriate `action_on_trigger` values

### AC-3.5: Full Synthesis

**Criteria**: Complete synthesis produces valid Decision.

**Verification**:
- [ ] `synthesize()` function exists
- [ ] Returns `Decision` object
- [ ] Decision has `selected_action` populated
- [ ] Decision has `robustness_basis` explanation
- [ ] Decision has `assessments_used` list of assessment IDs
- [ ] Decision has `monitoring` triggers

---

## AC-4: Graph Specification

### AC-4.1: GraphSpec Defined

**Criteria**: Pure graph specification is defined.

**Verification**:
- [ ] `GraphSpec` dataclass exists
- [ ] `nodes: list[str]` field exists
- [ ] `adjacency: dict[str, list[str]]` field exists

### AC-4.2: Phase 1 Graph Defined

**Criteria**: Phase 1 graph is defined correctly.

**Verification**:
- [ ] `PHASE1_GRAPH` constant exists
- [ ] Has 4 nodes: constraint, stability, reality_check, synthesis
- [ ] All agent nodes point to synthesis
- [ ] Synthesis has no successors (terminal node)

---

## AC-5: LangGraph Runner

### AC-5.1: State Management

**Criteria**: Runner manages state correctly.

**Verification**:
- [ ] `DragonflyState` TypedDict is defined
- [ ] State contains `situation`, `assessments`, `decision` fields
- [ ] State is properly typed

### AC-5.2: Execution Flow

**Criteria**: Runner executes all agents and synthesis.

**Verification**:
- [ ] Runner executes all three agents
- [ ] Assessments from all agents are accumulated
- [ ] Synthesis is called with all assessments
- [ ] Decision is returned

### AC-5.3: Public Interface

**Criteria**: Runner has clean public interface.

**Verification**:
- [ ] `run(situation: Situation) -> Decision` method exists
- [ ] Method is the main entry point
- [ ] Internal LangGraph details are hidden

---

## AC-6: FastAPI Service

### AC-6.1: Endpoint Exists

**Criteria**: POST /decide endpoint is implemented.

**Verification**:
- [ ] `POST /decide` endpoint exists
- [ ] Accepts JSON body with situation data
- [ ] Returns JSON with decision data
- [ ] Uses appropriate HTTP status codes

### AC-6.2: Request Validation

**Criteria**: Invalid requests are rejected with 422.

**Verification**:
- [ ] Missing `tenant_id` returns 422
- [ ] Invalid `time_horizon` value returns 422
- [ ] Invalid `stakes` value returns 422
- [ ] Missing required fields return 422

### AC-6.3: Response Format

**Criteria**: Response contains all required fields.

**Verification**:
- [ ] Response has `id` (UUID string)
- [ ] Response has `situation_id` (UUID string)
- [ ] Response has `selected_action` (ActionSpec)
- [ ] Response has `robustness_basis` (string)
- [ ] Response has `monitoring` (list)

### AC-6.4: Health Check

**Criteria**: Health check endpoint exists.

**Verification**:
- [ ] `GET /health` endpoint exists
- [ ] Returns 200 when service is healthy
- [ ] Returns appropriate response body

---

## AC-7: Architectural Constraints

### AC-7.1: Core Isolation

**Criteria**: Core imports nothing outside core and stdlib.

**Verification**:
- [ ] `core/types.py` has no external imports
- [ ] `core/nodes.py` has no external imports
- [ ] `core/synth.py` has no external imports
- [ ] `core/graph.py` has no external imports
- [ ] Import scan test passes

### AC-7.2: No I/O in Core

**Criteria**: Core performs no I/O operations.

**Verification**:
- [ ] No file operations in core
- [ ] No network calls in core
- [ ] No database access in core
- [ ] No LLM calls in core
- [ ] No subprocess calls in core

### AC-7.3: Determinism

**Criteria**: Core is deterministic given same inputs.

**Verification**:
- [ ] Same Situation produces same Decision
- [ ] No random state in core
- [ ] Timestamps are passed in, not generated (except defaults)

---

## AC-8: Testing Requirements

### AC-8.1: Unit Test Coverage

**Criteria**: Unit tests cover all core functionality.

**Verification**:
- [ ] `test_types.py` tests all type operations
- [ ] `test_nodes.py` tests all agents
- [ ] `test_synth.py` tests synthesis algorithm
- [ ] `test_graph.py` tests graph specification
- [ ] Coverage ≥ 85% for core module

### AC-8.2: Integration Tests

**Criteria**: Integration tests verify end-to-end flow.

**Verification**:
- [ ] LangGraph runner integration test passes
- [ ] FastAPI endpoint integration test passes
- [ ] End-to-end scenario test passes

### AC-8.3: Boundary Tests

**Criteria**: Boundary tests verify architectural constraints.

**Verification**:
- [ ] Import isolation test passes
- [ ] Core purity test passes

---

## AC-9: Performance

### AC-9.1: Response Time

**Criteria**: Decision is made within 500ms (no LLM).

**Verification**:
- [ ] Performance test shows < 500ms response
- [ ] No LLM calls slow down Phase 1
- [ ] Deterministic logic is fast

---

## AC-10: Documentation

### AC-10.1: Code Documentation

**Criteria**: Code is documented with docstrings.

**Verification**:
- [ ] All public classes have docstrings
- [ ] All public functions have docstrings
- [ ] Complex logic has inline comments

### AC-10.2: API Documentation

**Criteria**: API is documented.

**Verification**:
- [ ] FastAPI auto-generates OpenAPI docs
- [ ] Endpoint descriptions are clear
- [ ] Request/response schemas are documented

---

## Phase 1 Completion Checklist

### Required for Completion

- [ ] **AC-1**: Core Types - All implemented and tested
- [ ] **AC-2**: Epistemic Agents - All three implemented and tested
- [ ] **AC-3**: Synthesis Algorithm - Implemented and tested
- [ ] **AC-4**: Graph Specification - Defined and tested
- [ ] **AC-5**: LangGraph Runner - Working end-to-end
- [ ] **AC-6**: FastAPI Service - Endpoints working
- [ ] **AC-7**: Architectural Constraints - Verified by tests
- [ ] **AC-8**: Testing Requirements - All tests pass
- [ ] **AC-9**: Performance - Under 500ms threshold

### Optional for Phase 1

- [ ] Mímir adapter stub (can defer to Phase 2)
- [ ] Dragonfly Profile configuration (single default OK)
- [ ] Continuous re-sensing loop (single decision cycle OK)

---

## Sign-Off

Phase 1 is complete when:

1. All required acceptance criteria checkboxes are checked
2. All tests pass (`pytest` returns 0)
3. Coverage meets threshold (`pytest --cov-fail-under=85`)
4. Type checking passes (`mypy src/dragonfly/core/`)
5. Linting passes (`ruff check src/`)
6. Documentation is complete

**Phase 1 Completion Date**: _________________

**Sign-Off By**: _________________
