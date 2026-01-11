# Dragonfly Agent Framework - Design

## Architecture Overview

The Dragonfly framework follows a pure core with adapters pattern. The core is a deterministic decision graph that knows nothing about I/O, while adapters handle all external interactions.

```
┌─────────────────────────────────────────────────────────────────┐
│                        Service Layer                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │   FastAPI   │  │ MCP Server  │  │   CLI / Automation      │  │
│  └──────┬──────┘  └──────┬──────┘  └───────────┬─────────────┘  │
│         │                │                      │                │
│         └────────────────┼──────────────────────┘                │
│                          │                                       │
│                  ┌───────┴────────┐                              │
│                  │ LangGraph      │                              │
│                  │ Runner         │                              │
│                  └───────┬────────┘                              │
└──────────────────────────┼──────────────────────────────────────┘
                           │
┌──────────────────────────┼──────────────────────────────────────┐
│                    CORE (Pure Python)                            │
│                          │                                       │
│    ┌─────────────────────┼─────────────────────┐                │
│    │              Agent Graph                   │                │
│    │                                            │                │
│    │  ┌───────────┐  ┌───────────┐  ┌────────┐ │                │
│    │  │Constraint │  │Opportunity│  │Reality │ │                │
│    │  │  Agent    │  │  Agent    │  │ Check  │ │                │
│    │  └─────┬─────┘  └─────┬─────┘  └────┬───┘ │                │
│    │        │              │             │      │                │
│    │  ┌─────┴──────┐  ┌────┴────┐        │      │                │
│    │  │ Context/   │  │Stability│        │      │                │
│    │  │ Social     │  │ Agent   │        │      │                │
│    │  └─────┬──────┘  └────┬────┘        │      │                │
│    │        │              │             │      │                │
│    │        └──────────────┼─────────────┘      │                │
│    │                       │                    │                │
│    │                ┌──────┴──────┐             │                │
│    │                │  Synthesis  │             │                │
│    │                └──────┬──────┘             │                │
│    │                       │                    │                │
│    └───────────────────────┼────────────────────┘                │
│                            │                                     │
└────────────────────────────┼─────────────────────────────────────┘
                             │
┌────────────────────────────┼─────────────────────────────────────┐
│                     Adapter Layer                                │
│                            │                                     │
│         ┌──────────────────┼─────────────────┐                  │
│         │                  │                 │                  │
│    ┌────┴────┐      ┌──────┴──────┐    ┌─────┴─────┐           │
│    │ Memory  │      │    Sense    │    │   Act     │           │
│    │  Port   │      │    Port     │    │   Port    │           │
│    │ (Mímir) │      │             │    │           │           │
│    └─────────┘      └─────────────┘    └───────────┘           │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

## Core Module Structure

```
dragonfly/
  core/                    # pure python, stdlib only
    __init__.py
    types.py               # Situation, Assessment, Decision, etc.
    nodes.py               # node Protocols + reference nodes
    synth.py               # synthesis / robustness scoring
    graph.py               # pure graph spec (adjacency), no langgraph
    tests/
  adapters/
    mimir/
      client.py            # httpx client
      mapping.py           # core <-> mimir wire
  service/
    api/
      main.py              # FastAPI
      routes.py
      deps.py
    runtime/
      langgraph_runner.py  # executes core graph via langgraph
```

**Boundary Rule**: `core/` must import nothing outside `core/` and stdlib. CI should enforce this.

## Core Types (Protocol Aligned with Mímir)

### Input Types

**Observation**: A single observation about the world
- `id` (uuid)
- `content` - what was observed
- `source` - where it came from
- `reliability` - low | medium | high
- `timestamp`

**ActionSpec**: A candidate action that could be taken
- `id` (uuid)
- `name`
- `description`
- `reversibility` - reversible | costly | irreversible
- `time_sensitivity` - immediate | near | flexible (optional)

**Situation**: The complete context for a decision
- `id` (uuid)
- `tenant_id` - for multi-tenancy
- `goal` - what we're trying to accomplish
- `time_horizon` - immediate | near | long
- `stakes` - low | medium | high
- `observations` - list of Observation
- `candidate_actions` - list of ActionSpec
- `candidate_models` - optional list of model hypotheses
- `context` - opaque bag for adapters
- `created_at`

### Assessment Type

**Assessment**: Output from an epistemic agent
- `id` (uuid)
- `situation_id` - links to parent situation
- `agent_type` - constraint | opportunity | reality_check | social | stability
- `claim` - short statement
- `support` - references to evidence/observation IDs
- `confidence` - low | medium | high
- `severity` - low | medium | high (if violated, how bad)
- `reversibility` - reversible | costly | irreversible
- `recommended_tests` - what observation would resolve this
- `created_at`

### Output Types

**MonitoringTrigger**: A condition to watch that could trigger re-planning
- `condition`
- `action_on_trigger` - re_plan | alert | escalate

**Decision**: The output of the synthesis process
- `id` (uuid)
- `situation_id` - links to parent situation
- `tenant_id`
- `selected_action` - ActionSpec
- `alternatives_considered` - list of ActionSpec
- `robustness_basis` - explanation of why this action was chosen
- `assessments_used` - IDs of assessments that informed this
- `monitoring` - list of MonitoringTrigger
- `provenance_links` - pointers into memory
- `created_at`

## Agent Graph Definition

### Node Protocol

All epistemic nodes must implement:
- `agent_type` property returning the type identifier
- `assess(situation, memory_snapshot?) -> list[Assessment]` method

### Core Nodes

1. **ConstraintAgent**
   - Input: Situation
   - Process: Identify hard constraints, failure modes, irreversibility warnings
   - Output: Assessments with agent_type="constraint"

2. **OpportunityAgent**
   - Input: Situation
   - Process: Identify options, upside paths, optionality-increasing moves
   - Output: Assessments with agent_type="opportunity"

3. **RealityCheckAgent**
   - Input: Situation
   - Process: Identify contradictions, disconfirmations, missing information
   - Output: Assessments with agent_type="reality_check"

4. **ContextSocialAgent**
   - Input: Situation
   - Process: Identify coordination constraints, incentives, likely reactions
   - Output: Assessments with agent_type="social"

5. **StabilityAgent**
   - Input: Situation
   - Process: Identify agency-preserving moves under uncertainty (minimax regret)
   - Output: Assessments with agent_type="stability"

### Graph Flow

```
Situation ──┬──► ConstraintAgent ────────┐
            ├──► OpportunityAgent ───────┤
            ├──► RealityCheckAgent ──────┼──► Synthesis ──► Decision
            ├──► ContextSocialAgent ─────┤
            └──► StabilityAgent ─────────┘
                                         │
                                         ▼
                                    Memory Port
                                         │
                                         ▼
                                     Situation (feedback loop)
```

## Synthesis Algorithm

The synthesis node does not ask "which model is true?" It asks "which actions survive disagreement?"

### Decision Rule (Conceptual)

1. **Filter**: Eliminate actions that violate hard constraints from any agent
2. **Score**: For remaining actions, calculate:
   - Reversibility score (prefer reversible)
   - Constraint satisfaction (fewer warnings = better)
   - Opportunity alignment (more upside = better)
   - Stability score (minimax regret)
3. **Select**: Choose action that:
   - Passes all hard constraints
   - Maximizes reversibility under uncertainty
   - Minimizes worst-case regret
4. **Monitor**: Define triggers for re-planning

### Robustness Scoring Approaches

- **Maximin score**: Worst-case safety - maximize minimum utility across scenarios
- **Minimax regret score**: Performance stability - minimize maximum regret relative to optimal
- **Satisficing score**: Acceptable across models - does action exceed threshold for most assessments?

## Port Interfaces

The core interacts with the outside world only through ports.

### Memory Port (Mímir Interface)

Operations:
- `search(query, filters) -> list[artifact_id]` - Search for artifacts matching query
- `get(artifact_id) -> artifact` - Retrieve an artifact by ID
- `put(artifact) -> artifact_id` - Store an artifact, return its ID
- `relate(from_id, relation_type, to_id) -> relation_id` - Create a relation between artifacts
- `provenance(event) -> event_id` - Record a provenance event

### Sense Port

Operations:
- `observe(query) -> list[Observation]` - Gather observations relevant to query

### Act Port

Operations:
- `execute(action) -> result` - Execute an action and return result

**Key Rule**: The core never calls these ports directly. It declares dependencies, and the runtime injects implementations.

## Mímir Artifact Mapping

| Dragonfly Type | Mímir Artifact Type | Relations |
|----------------|---------------------|-----------|
| Situation | `situation` or `context_snapshot` | - |
| Assessment | `assessment` | `derived_from` → Situation |
| Decision | `decision` | `based_on` → Situation, `used` → Assessment |
| MonitoringTrigger | `tripwire` or `watch` | `monitors` → Decision |
| Profile (tuning) | `dragonfly_profile` | `applies_to` → tenant |

All Mímir calls include `X-Tenant-ID` header for isolation.

## Dragonfly Profile (Tuning Configuration)

Tunable parameters for a tenant/environment:
- `id`
- `tenant_id`
- `hard_constraint_threshold` - severity/confidence that can veto
- `regret_weight` - worst-case vs average utility
- `reversibility_bias` - preference for reversible actions
- `disagreement_tolerance` - conflicting assessments before pause
- `observation_trust` - default reliability of signals
- `created_at`
- `updated_at`

Profiles are stored as Mímir artifacts and loaded at runtime.
