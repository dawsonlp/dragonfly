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

*Future decisions will be logged here as development progresses.*
