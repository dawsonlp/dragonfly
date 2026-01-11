# Dragonfly Agent Framework - Requirements

## Overview

Dragonfly is a multi-perspective decision-making agent framework designed to remain robust when no single model of reality can be trusted. It is based on the "Dragonfly Method" - a distributed epistemic stance-taking approach that integrates multiple perspectives without forcing premature coherence.

## Core Philosophy

The framework embodies these epistemic principles:

1. **No single model deserves ontological authority** - models are tools, not ground truth
2. **Decisions should not depend on fragile explanatory commitments**
3. **Optimize for survivability across models, not optimality within one**
4. **Actions should survive disagreement** rather than requiring consensus

## Functional Requirements

### FR-1: Multi-Perspective Sensing
- Support multiple concurrent perspectives on any decision situation
- Each perspective (agent) represents an epistemic function, not a belief
- Agents produce constraints and affordances, not votes or beliefs

### FR-2: Heterogeneous Epistemic Agents
The framework must support these core agent types:
- **Constraint Agent**: Identifies hard constraints, failure modes, irreversibility
- **Opportunity Agent**: Identifies options, upside paths, optionality-increasing moves
- **Reality-Check Agent**: Identifies contradictions, disconfirmations, missing information
- **Context/Social Agent**: Identifies coordination constraints, incentives, likely reactions
- **Stability Agent**: Identifies agency-preserving moves under model uncertainty (minimax regret)

### FR-3: Non-Voting Synthesis
- Agents do not vote and do not seek agreement
- System maintains a constraint field from all agent outputs
- Decision synthesis asks "which actions survive disagreement?" not "which model is true?"
- Eliminate actions that violate hard constraints from any agent
- Prefer actions that preserve optionality, remain acceptable across most agents, degrade gracefully

### FR-4: Continuous Re-Sensing
- No terminal decision state - agents continue sensing after action
- Constraints update as situation evolves
- Exit conditions are monitored
- Monitoring triggers can initiate re-planning

### FR-5: Robustness Scoring
Support multiple robustness criteria:
- **Maximin utility**: worst-case safety
- **Minimax regret**: performance stability
- **Satisficing**: acceptable across most models

### FR-6: Memory Integration
- Integration with Mímir as the memory/artifact service
- Store situations, assessments, and decisions as artifacts
- Maintain provenance trail for all decisions
- Support for tenant isolation (multi-tenancy)

## Non-Functional Requirements

### NFR-1: Reusability
The agent graph must be reusable in any scenario:
- Automation workflows
- Chat interfaces
- Legacy human interfaces (GUI, web app, mobile app)
- MCP server integration
- Headless/daemon operation

### NFR-2: Core Purity
The core must:
- Be deterministic given inputs
- Not perform I/O
- Not call LLMs or tools directly
- Not know about HTTP, databases, files, queues, or streaming
- Have zero dependency on FastAPI/httpx/langgraph
- Depend only on Python standard library (pydantic optional for validation)

### NFR-3: No Extraneous Elements
The Dragonfly core must NOT include:
- UI concepts (chat turns, streaming tokens, widgets)
- Transport (HTTP, WebSockets, MCP, queues)
- Tool execution (shell, browser, integrations)
- Orchestration/scheduling semantics (jobs, cron, retries)
- Identity/auth models (other than pass-through tenant/context token)
- LLM dependency (LLM is just one possible adapter)

### NFR-4: Explicit Tuning
Since originator tuning is unavailable, tuning must be:
- Exposed as data, not baked into code
- Stored as "Dragonfly Profile" artifacts in Mímir
- Adjustable per tenant/environment
- Evolvable empirically through observation

### NFR-5: Invariant Rule
No agent is allowed to assert ontological authority. Agents may say:
- "If X, then risk Y"
- "This action fails under model Z"

Agents may never say:
- "Reality is Z"
- "This is the true model"

## Tunable Parameters

These must be configurable, not hard-coded:
- `hard_constraint_threshold`: what severity/confidence can veto an action
- `regret_weight`: how much to punish worst-case regret vs average utility
- `reversibility_bias`: how strongly to prefer reversible actions under uncertainty
- `disagreement_tolerance`: how many conflicting assessments trigger "pause/gather data"
- `observation_trust`: default reliability of incoming signals
