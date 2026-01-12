# Dragonfly - Design Decisions Log

This document logs design decisions made during development, following the project's development process.

## 2026-01-11: Initial Architecture and Technical Stack

### Decision: Pure Core with Adapters Pattern

**Context**: Need an agent framework that is reusable across automation, chat, GUI, web, mobile, and MCP server contexts.

**Decision**: Implement a "pure core with adapters" architecture where:
- The core is deterministic, stdlib-only Python
- All I/O goes through port interfaces (Memory, Sense, Act)
- Service tooling (FastAPI, LangGraph, httpx) lives strictly in the service/adapter layers

**Rationale**: This allows the same decision logic to be deployed in any context without modification, and makes testing straightforward.

### Decision: Epistemic Agents, Not Voting Agents

**Context**: Traditional multi-agent systems often use voting or consensus mechanisms.

**Decision**: Agents represent epistemic functions (Constraint, Opportunity, Reality-Check, Social, Stability) that produce assessments, not votes. Synthesis asks "which actions survive disagreement?" not "which model wins?"

**Rationale**: This aligns with the Dragonfly Method's core insight - robust decision-making under uncertainty requires holding multiple perspectives without forcing premature coherence.

### Decision: Protocol Alignment with Mímir

**Context**: Need persistent storage for situations, assessments, and decisions with provenance tracking.

**Decision**: Align Dragonfly types with Mímir's protocol conventions (artifact structure, relations, provenance events, tenant scoping via X-Tenant-ID).

**Rationale**: Avoids parallel schema maintenance and enables seamless integration with existing Mímir infrastructure.

### Decision: Python 3.13+ with 3.14 Runtime Target

**Context**: Need modern typing features and language capabilities.

**Decision**: Library compatibility baseline Python ≥3.13, production runtime target Python 3.14.

**Rationale**: Enables aggressive use of modern typing (Protocol, TypedDict, type aliases) while maintaining reasonable compatibility.

### Decision: Tuning as Data, Not Code

**Context**: The Dragonfly Method's originator tuning is unavailable, but we know tuning exists and matters.

**Decision**: Expose tuning parameters as configurable "DragonflyProfile" artifacts stored in Mímir, adjustable per tenant/environment.

**Rationale**: Makes tuning explicit, observable, and evolvable through empirical observation rather than hidden in code.

### Decision: No Ontological Authority Invariant

**Context**: Agents could potentially make claims about "what is true" rather than "what constraints exist."

**Decision**: Encode an invariant rule: no agent may assert ontological authority. Agents may say "If X, then risk Y" but never "Reality is Z."

**Rationale**: This is the core epistemic commitment of the framework - preserving openness and refusing false certainty.

---

## 2026-01-11: Phase 1 Shakeout Planning

### Decision: Minimal Three-Agent Shakeout (PD-1)

**Context**: Need to validate the architecture before building the full framework.

**Decision**: Phase 1 implements only three agents (ConstraintAgent, StabilityAgent, RealityCheckAgent) with deterministic logic (no LLM).

**Rationale**: 
- Validates core architecture without LLM complexity
- Enables fast iteration (< 500ms decisions)
- LLM integration is a service-layer concern to be added later
- Sufficient to exercise constraint filtering and robustness scoring

### Decision: Dataclasses Over Pydantic in Core (PD-2)

**Context**: Need type validation in the core, but also need to maintain stdlib-only dependency.

**Decision**: Use stdlib `dataclasses` with `typing.Literal` for type constraints in core. Pydantic may be used in service layer for request/response validation.

**Rationale**:
- Keeps core dependency-free
- Pydantic adds unnecessary complexity for internal types
- Core types can be converted to/from Pydantic models at service boundaries
- Validates the "stdlib-only" constraint early

### Decision: UUID and Tenant ID Required from Start (PD-3)

**Context**: Future Mímir integration requires IDs and tenant isolation.

**Decision**: All Phase 1 types include `id` (UUID) and relevant types include `tenant_id` as required fields, even though Mímir integration is optional in Phase 1.

**Rationale**:
- Forces multi-tenancy discipline early
- Enables provenance tracking from the start
- Prevents costly refactoring when adding Mímir
- IDs enable assessment→decision linkage

### Decision: Strict Core Import Boundary Enforcement (PD-4)

**Context**: The "pure core" architecture requires enforcing that core imports nothing from service layer.

**Decision**: Implement CI import scanning that fails if `core/` imports anything outside `core/` and stdlib.

**Rationale**:
- Technical debt prevention
- Ensures portability of core
- Makes boundary violations obvious immediately
- Validates architectural decisions continuously

### Decision: Test-First with 85% Coverage Target (PD-5)

**Context**: Need confidence that Phase 1 validates the design correctly.

**Decision**: All Phase 1 development follows test-first approach with 85% minimum coverage for core module.

**Rationale**:
- Tests document expected behavior
- Enables safe refactoring as design evolves
- Coverage threshold prevents gaps
- Unit tests serve as executable specification

### Decision: Eight Concrete Validation Scenarios (PD-6)

**Context**: Need concrete test cases that exercise all agent behaviors and edge cases.

**Decision**: Define 8 scenarios covering: simple choice, hard constraints, high stakes, low reliability, conflicts, all-constrained, single action, and empty observations.

**Rationale**:
- Comprehensive coverage of behaviors
- Provides acceptance test suite
- Documents expected framework behavior
- Serves as integration test cases

---

## 2026-01-11: Testing Philosophy Refinement

### Decision: Functional Tests Over Unit Tests (PD-7)

**Context**: Initial Phase 1 implementation had 119 unit tests covering types, nodes, synth, graph, and runner. Many tested implementation details rather than user-visible behavior.

**Decision**: Replace granular unit tests with minimal functional tests:
- 5 functional tests (user-visible decision behaviors)
- 1 architectural test (core import isolation)
- 1 non-functional test (performance < 500ms)

**Rationale**:
- Lines of code are a liability, including test code
- Tests that verify implementation details create rigidity without value
- Modern tracing makes debugging failures straightforward
- Tests should verify user-visible behaviors, not internal APIs
- 7 tests now cover what 119 tests previously covered, with less maintenance burden

**Supersedes**: PD-5 (Test-First with 85% Coverage Target). Coverage percentage is not the goal; verifying actual user behaviors is.

### Decision: Accept Pragmatic Impurity in Core (PD-8)

**Context**: Core uses `datetime.now(UTC)` and `uuid4()` as defaults in dataclasses. These are technically I/O operations.

**Decision**: Accept these as "pragmatic impurity" since they:
- Don't affect user-visible behavior
- Don't require external dependencies
- Don't require mocks for testing (we don't test internal values)
- Are stdlib-only

**Rationale**: 
- Pure functional programming is a means, not an end
- The goal is testable, portable code - achieved
- Adding explicit timestamp/ID parameters would add complexity without user benefit
- Tests verify behavior, not implementation details

### Decision: Requirements-Driven Testing (PD-9)

**Context**: Code coverage metrics can drive test creation that serves the metric rather than verification of user needs. Conversely, comprehensive requirement-based testing surfaces code that may not be necessary.

**Decision**: Tests encode requirements. Code coverage is treated as a signal about code health, not test health.

When a test suite verifies all requirements and edge cases, coverage analysis can reveal:
- Code that serves no verified requirement (candidate for removal)
- Requirements that lack test coverage (candidate for test addition)
- Defensive code that should make its purpose explicit

**Guidance**:
1. Write tests that verify user-visible behaviors and documented requirements
2. Use coverage to identify code that tests don't exercise, then ask: "What requirement does this serve?"
3. Prefer deleting unnecessary code over writing tests for unneeded code
4. When code exists for exceptional conditions, consider whether that condition is testable; if not, document the rationale

**Rationale**: Tests are code, and code is a liability. Tests that exist to satisfy coverage metrics add maintenance burden without adding confidence. Coverage serves best as a tool for identifying code of questionable necessity.

---

*Future decisions will be logged here as development progresses.*
