# Dragonfly - Design Principles

This document describes the design principles and best practices followed in the Dragonfly Agent Framework.

## Architecture

### Pure Core with Adapters

The framework uses a "pure core with adapters" architecture:
- **Core** is deterministic, stdlib-only Python
- All I/O goes through port interfaces (Memory, Sense, Act)
- Service tooling (FastAPI, LangGraph, httpx) lives strictly in the service/adapter layers

This allows the same decision logic to be deployed in any context without modification.

### Epistemic Agents, Not Voting Agents

Agents represent epistemic functions (Constraint, Opportunity, Reality-Check, Social, Stability) that produce assessments, not votes. Synthesis asks "which actions survive disagreement?" not "which model wins?"

This aligns with the Dragonfly Method's core insight: robust decision-making under uncertainty requires holding multiple perspectives without forcing premature coherence.

### No Ontological Authority

No agent may assert ontological authority. Agents may say "If X, then risk Y" but not "Reality is Z." This is the core epistemic commitment of the framework—preserving openness and refusing false certainty.

## Technical Decisions

### Python 3.13+ with 3.14 Runtime Target

Library compatibility baseline Python ≥3.13, production runtime target Python 3.14. This enables aggressive use of modern typing (Protocol, TypedDict, type aliases).

### Dataclasses in Core, Pydantic at Boundaries

Core uses stdlib `dataclasses` with `typing.Literal` for type constraints. Pydantic may be used in service layer for request/response validation, converting at boundaries.

### UUID and Tenant ID from Start

All types include `id` (UUID) and relevant types include `tenant_id` as required fields. This forces multi-tenancy discipline early and enables provenance tracking.

### Strict Core Import Boundary

Core imports only from stdlib and `dragonfly.core`. This is enforced by automated testing to ensure portability.

### Pragmatic Impurity Accepted

Core uses `datetime.now(UTC)` and `uuid4()` as defaults in dataclasses. These are accepted as "pragmatic impurity" since they don't affect user-visible behavior and don't require external dependencies.

## Testing Philosophy

### Requirements-Driven Testing

Tests encode requirements. Code coverage is treated as a signal about code health, not test health.

When a test suite verifies all requirements and edge cases, coverage analysis can reveal:
- Code that serves no verified requirement (candidate for removal)
- Requirements that lack test coverage (candidate for test addition)
- Defensive code that should make its purpose explicit

**Guidance**:
1. Write tests that verify user-visible behaviors and documented requirements
2. Use coverage to identify code that tests don't exercise, then ask: "What requirement does this serve?"
3. Prefer deleting unnecessary code over writing tests for unneeded code
4. When code exists for exceptional conditions, consider whether that condition is testable; if not, document the rationale

### Functional Tests Over Unit Tests

Tests verify user-visible behaviors, not implementation details. This reduces maintenance burden and prevents tests from creating rigidity in the codebase.

The current test suite consists of:
- **Functional tests**: Verify decision behaviors (reversibility preference, constraint filtering, warnings)
- **Architectural tests**: Verify core import isolation
- **Non-functional tests**: Verify performance requirements

## Protocol Alignment

### Mímir Integration

Dragonfly types align with Mímir's protocol conventions (artifact structure, relations, provenance events, tenant scoping via X-Tenant-ID). This avoids parallel schema maintenance.

### Tuning as Data

Tuning parameters are exposed as configurable artifacts (stored in Mímir), adjustable per tenant/environment. This makes tuning explicit, observable, and evolvable through empirical observation rather than hidden in code.
