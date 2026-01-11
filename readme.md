# Dragonfly Agent Framework

A multi-perspective decision-making agent framework designed to remain robust when no single model of reality can be trusted.

## Overview

Dragonfly implements the "Dragonfly Method" - a distributed epistemic stance-taking approach that:

- Integrates multiple concurrent perspectives without forcing premature coherence
- Uses heterogeneous epistemic agents (Constraint, Opportunity, Reality-Check, Social, Stability)
- Synthesizes decisions by asking "which actions survive disagreement?" rather than "which model is true?"
- Maintains continuous re-sensing rather than terminal decision states
- Optimizes for **survivability across models**, not optimality within one

## Core Philosophy

> "Prefer policies whose expected performance is stable across a wide set of plausible world models, rather than policies that optimize strongly for a narrow, possibly false model."

The framework embodies:
1. **No single model deserves ontological authority** - models are tools, not ground truth
2. **Decisions should not depend on fragile explanatory commitments**
3. **Actions should survive disagreement** rather than requiring consensus
4. **Robustness over optimality**

## Documentation

- **[Requirements](requirements.md)** - Functional and non-functional requirements
- **[Design](design.md)** - Architecture, types, protocols, and component design
- **[Development Approach](development_approach.md)** - Technical decisions, implementation order, and testing strategy

## Architecture

```
Service Layer (FastAPI, LangGraph)
         │
         ▼
    CORE (Pure Python, stdlib only)
         │
    ┌────┴────┐
    │  Agent  │
    │  Graph  │
    └────┬────┘
         │
    Adapter Layer (Mímir, Sense, Act ports)
```

**Key Design Principle**: The core is deterministic, performs no I/O, and knows nothing about HTTP, databases, LLMs, or external services. All external interactions go through adapter ports.

## Technology Stack

- **Python**: ≥3.13 (runtime target: 3.14)
- **FastAPI**: Service boundary
- **httpx**: Outbound HTTP calls
- **LangGraph**: Graph orchestration (service layer only)
- **Mímir**: Memory/artifact storage (via adapter)

## Project Status

**Phase 1**: Building a minimal "shakeout" agent to validate design decisions:
- ConstraintAgent, StabilityAgent, RealityCheckAgent
- Basic synthesis with constraint filtering and robustness scoring
- Core type definitions and protocols

## Getting Started

*Coming soon - currently in design/early implementation phase*

## Background

This framework emerged from discussions about:
- Human epistemic orientation and uncertainty tolerance
- Decision-making under deep uncertainty (DMDU)
- Robust decision-making (RDM) principles
- The need for agent architectures that refuse false certainty

The "Dragonfly" metaphor captures the key insight: dragonflies see in multiple directions simultaneously, integrate motion rather than static snapshots, and do not commit to a single focal point - adjusting continuously rather than converging prematurely.

## Attribution and Inspiration

### Dragonfly Thinking™

This project is inspired by the methodology and concepts developed by **Dragonfly Thinking™**, founded by **Anthea Roberts** (interdisciplinary professor at ANU, LSE, Columbia, and Harvard; author of "Six Faces of Globalization").

Dragonfly Thinking provides AI tools for strategic intelligence, helping decision-makers navigate complexity by understanding multiple perspectives, identifying connections that others miss, and building strategies that work across multiple futures.

- **Website**: [https://www.dragonflythinking.com](https://www.dragonflythinking.com)
- **Copyright**: © 2025 Dragonfly Thinking™
- **ABN**: 74 670 736 820

### Philip Tetlock's "Dragonfly Eyes"

The underlying concept of "dragonfly eyes" originates from political scientist **Philip Tetlock's** research on superforecasters, as documented in his book "Superforecasting: The Art and Science of Prediction." Tetlock discovered that the world's best forecasters "see through dragonfly eyes" - while experts get trapped in single perspectives, superforecasters seek out and integrate multiple viewpoints to build complete understanding.

### Disclaimer

This project is an independent implementation inspired by the publicly described concepts of the Dragonfly Method. It is:
- **Not affiliated with** Dragonfly Thinking™ or Anthea Roberts
- **Not endorsed by** Dragonfly Thinking™
- **Not a copy of** their proprietary platform or software

This is an open-source exploration of multi-perspective, robust decision-making concepts for agent architectures.

## License

This project is licensed under the **GNU General Public License v3.0** (GPL-3.0).

See the [LICENSE](LICENSE) file for the full license text.
