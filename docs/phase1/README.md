# Phase 1: Shakeout Agent Development Plan

## Purpose

Phase 1 implements a minimal "shakeout" agent to validate design decisions before building the full Dragonfly framework. The goal is to exercise the architecture with the smallest scope that proves the core concepts work.

## Scope Summary

**What Phase 1 Includes:**
- 3 epistemic agents: ConstraintAgent, StabilityAgent, RealityCheckAgent
- Core types: Situation, Observation, Assessment, Decision, ActionSpec
- Synthesis: constraint filtering + reversibility scoring + minimax-regret proxy
- Pure core with no I/O or external dependencies
- LangGraph runner (service layer)
- FastAPI endpoint (POST /decide)
- Optional Mímir stub for persistence

**What Phase 1 Excludes:**
- OpportunityAgent and ContextSocialAgent (full version)
- LLM integration (agents use deterministic logic)
- Production Mímir integration (stub only)
- Multiple Dragonfly Profiles (single default config)
- Continuous re-sensing loop (single decision cycle)

## Documents in This Directory

| Document | Purpose |
|----------|---------|
| [implementation-plan.md](implementation-plan.md) | Detailed step-by-step implementation guide |
| [test-plan.md](test-plan.md) | Testing strategy and test specifications |
| [acceptance-criteria.md](acceptance-criteria.md) | Definition of done for Phase 1 |
| [example-scenarios.md](example-scenarios.md) | Concrete test scenarios for validation |

## Success Metrics

Phase 1 is complete when:

1. **Core Isolation Verified**: `core/` imports nothing outside core + stdlib
2. **Type System Works**: All types serialize/deserialize correctly
3. **Agents Produce Valid Assessments**: Each agent returns well-formed assessments
4. **Synthesis Makes Robust Decisions**: Actions filtered by constraints, scored by robustness
5. **End-to-End Flow Works**: HTTP request → Decision response in < 500ms (no LLM)
6. **Design Validated**: Architecture proves sound for expansion

## Timeline Estimate

Assuming development proceeds step-by-step with test-first approach:

| Step | Estimate | Cumulative |
|------|----------|------------|
| Core Types | 2-3 hours | 3 hours |
| Node Protocol + Agents | 4-6 hours | 9 hours |
| Synthesis Algorithm | 3-4 hours | 13 hours |
| Graph Specification | 1-2 hours | 15 hours |
| LangGraph Runner | 3-4 hours | 19 hours |
| FastAPI Service | 2-3 hours | 22 hours |
| Integration Testing | 2-3 hours | 25 hours |
| Documentation | 1-2 hours | 27 hours |

**Total Estimate**: 25-30 hours of focused development time

## Key Design Decisions for Phase 1

### PD-1: No LLM in Shakeout

**Decision**: Phase 1 agents use deterministic logic (keyword matching, rule evaluation).

**Rationale**: Validates the architecture without LLM complexity. LLM integration is a service-layer concern that can be added later without changing the core.

### PD-2: Tenant ID Required from Start

**Decision**: All types include `tenant_id` as a required field.

**Rationale**: Forces multi-tenancy discipline early. Prevents future refactoring when adding Mímir integration.

### PD-3: UUID IDs Throughout

**Decision**: All entities have UUID IDs generated at creation.

**Rationale**: Enables:
- Mímir artifact correlation
- Provenance tracking
- Idempotent operations
- Reference integrity in assessments and decisions

### PD-4: Dataclasses Over Pydantic in Core

**Decision**: Use stdlib `dataclasses` in core, not Pydantic.

**Rationale**: 
- Keeps core dependency-free
- Pydantic can be used in service layer for request/response validation
- Core types can be converted to/from Pydantic models at boundaries

## Getting Started

1. Read [implementation-plan.md](implementation-plan.md) for the development sequence
2. Review [test-plan.md](test-plan.md) for test-first requirements
3. Check [acceptance-criteria.md](acceptance-criteria.md) for definition of done
4. Use [example-scenarios.md](example-scenarios.md) for concrete test cases

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Scope creep | Strict adherence to Phase 1 boundaries |
| Over-engineering | Keep agents simple (deterministic rules) |
| Architecture drift | CI import scanning enforces boundaries |
| Integration complexity | Stub Mímir, defer real integration |
