# Phase 1 Example Scenarios

## Overview

This document provides concrete test scenarios for validating the Phase 1 shakeout agent. Each scenario includes:
- **Context**: Background for the decision
- **Input**: Situation with observations and candidate actions
- **Expected Behavior**: How agents should respond
- **Expected Output**: Decision and rationale

These scenarios are designed to exercise different aspects of the framework without requiring LLM integration.

---

## Scenario 1: Simple Reversible Choice

### Context

A straightforward decision where one action is clearly more reversible than another, with no hard constraints.

### Input

```python
situation = Situation(
    tenant_id="tenant-test",
    goal="Choose deployment strategy for new feature",
    time_horizon="near",
    stakes="medium",
    observations=[
        Observation(
            content="Feature is ready for deployment",
            source="ci_pipeline",
            reliability="high"
        ),
        Observation(
            content="No critical bugs reported",
            source="qa_team",
            reliability="high"
        )
    ],
    candidate_actions=[
        ActionSpec(
            name="Full rollout",
            description="Deploy to all users immediately",
            reversibility="costly"
        ),
        ActionSpec(
            name="Gradual rollout",
            description="Deploy to 10% of users, then expand",
            reversibility="reversible"
        ),
        ActionSpec(
            name="Cancel release",
            description="Hold the release for next sprint",
            reversibility="reversible"
        )
    ]
)
```

### Expected Agent Behavior

**ConstraintAgent**:
- No hard constraints (no deadline, no blocking issues)
- May note that full rollout is "costly" to reverse

**StabilityAgent**:
- Score "Gradual rollout" highest (reversible)
- Score "Cancel release" high (reversible)
- Score "Full rollout" lower (costly)

**RealityCheckAgent**:
- No contradictions in observations
- High reliability sources, no flags

### Expected Decision

```python
Decision(
    selected_action=ActionSpec(name="Gradual rollout", ...),
    robustness_basis="Passed all constraints. Gradual rollout selected for highest reversibility score.",
    monitoring=[],  # No high-severity warnings
    assessments_used=[...]
)
```

---

## Scenario 2: Hard Constraint Violation

### Context

A decision where a deadline creates a hard constraint that eliminates one of the options.

### Input

```python
situation = Situation(
    tenant_id="tenant-test",
    goal="Prepare quarterly report",
    time_horizon="immediate",
    stakes="high",
    observations=[
        Observation(
            content="Deadline is Friday 5pm, non-negotiable",
            source="manager",
            reliability="high"
        ),
        Observation(
            content="Current data is incomplete",
            source="data_team",
            reliability="medium"
        )
    ],
    candidate_actions=[
        ActionSpec(
            name="Submit with current data",
            description="Submit report using available data",
            reversibility="costly",
            time_sensitivity="immediate"
        ),
        ActionSpec(
            name="Wait for complete data",
            description="Delay submission until all data arrives",
            reversibility="reversible",
            time_sensitivity="flexible"
        ),
        ActionSpec(
            name="Request deadline extension",
            description="Ask for more time",
            reversibility="reversible",
            time_sensitivity="immediate"
        )
    ]
)
```

### Expected Agent Behavior

**ConstraintAgent**:
- HARD CONSTRAINT: "Wait for complete data" violates deadline
- Deadline keyword + flexible time_sensitivity triggers constraint
- May flag "Submit with current data" as having incomplete data risk

**StabilityAgent**:
- "Request deadline extension" is reversible
- "Submit with current data" is costly to reverse
- "Wait for complete data" is reversible but constrained

**RealityCheckAgent**:
- Flag incomplete data observation (medium reliability)
- Note uncertainty in decision basis

### Expected Decision

```python
Decision(
    selected_action=ActionSpec(name="Request deadline extension", ...),
    robustness_basis="'Wait for complete data' eliminated by deadline constraint. 'Request deadline extension' selected as most reversible surviving option.",
    monitoring=[
        MonitoringTrigger(
            condition="Monitor: Incomplete data may affect quality",
            action_on_trigger="alert"
        )
    ],
    assessments_used=[...]
)
```

---

## Scenario 3: High Stakes with Irreversible Option

### Context

A high-stakes situation where one option is irreversible, triggering stability warnings.

### Input

```python
situation = Situation(
    tenant_id="tenant-test",
    goal="Decide on vendor contract",
    time_horizon="long",
    stakes="high",
    observations=[
        Observation(
            content="Vendor A offers 30% cost reduction",
            source="sales_rep",
            reliability="medium"
        ),
        Observation(
            content="Contract has 5-year lock-in clause",
            source="legal_review",
            reliability="high"
        ),
        Observation(
            content="Current vendor is stable but expensive",
            source="operations",
            reliability="high"
        )
    ],
    candidate_actions=[
        ActionSpec(
            name="Sign with Vendor A",
            description="Accept new vendor's contract",
            reversibility="irreversible"
        ),
        ActionSpec(
            name="Stay with current vendor",
            description="Renew existing contract",
            reversibility="costly"
        ),
        ActionSpec(
            name="Negotiate shorter term",
            description="Ask Vendor A for 2-year contract",
            reversibility="reversible"
        )
    ]
)
```

### Expected Agent Behavior

**ConstraintAgent**:
- Warning on "Sign with Vendor A": irreversible action in high-stakes situation
- No hard constraints (no deadline)

**StabilityAgent**:
- Strong warning on "Sign with Vendor A": irreversible + high stakes
- "Negotiate shorter term" scores highest (reversible)
- "Stay with current vendor" middle (costly but familiar)

**RealityCheckAgent**:
- Flag: sales_rep observation is medium reliability
- Potential conflict: cost reduction vs. lock-in risk

### Expected Decision

```python
Decision(
    selected_action=ActionSpec(name="Negotiate shorter term", ...),
    robustness_basis="'Sign with Vendor A' flagged as high-risk irreversible action in high-stakes situation. 'Negotiate shorter term' selected for reversibility.",
    monitoring=[
        MonitoringTrigger(
            condition="Monitor: Irreversible action in high-stakes situation",
            action_on_trigger="alert"
        ),
        MonitoringTrigger(
            condition="Monitor: Medium reliability source for cost reduction claim",
            action_on_trigger="alert"
        )
    ],
    assessments_used=[...]
)
```

---

## Scenario 4: Low-Reliability Information

### Context

A situation where observations come from unreliable sources, requiring caution.

### Input

```python
situation = Situation(
    tenant_id="tenant-test",
    goal="Respond to market opportunity",
    time_horizon="near",
    stakes="high",
    observations=[
        Observation(
            content="Competitor is going bankrupt",
            source="social_media_rumor",
            reliability="low"
        ),
        Observation(
            content="Market demand is increasing",
            source="internal_sales",
            reliability="high"
        )
    ],
    candidate_actions=[
        ActionSpec(
            name="Aggressive expansion",
            description="Double marketing spend immediately",
            reversibility="costly"
        ),
        ActionSpec(
            name="Measured increase",
            description="Increase spend by 20%, monitor results",
            reversibility="reversible"
        ),
        ActionSpec(
            name="Wait and see",
            description="Monitor situation before acting",
            reversibility="reversible"
        )
    ]
)
```

### Expected Agent Behavior

**ConstraintAgent**:
- No hard constraints

**StabilityAgent**:
- "Measured increase" and "Wait and see" score high (reversible)
- "Aggressive expansion" scores lower (costly)

**RealityCheckAgent**:
- HIGH SEVERITY WARNING: Low reliability source + high stakes
- Flag that competitor bankruptcy claim is unreliable
- Recommend verification before acting

### Expected Decision

```python
Decision(
    selected_action=ActionSpec(name="Measured increase", ...),
    robustness_basis="High-stakes decision with low-reliability information. 'Measured increase' provides upside exposure while remaining reversible.",
    monitoring=[
        MonitoringTrigger(
            condition="Monitor: Low reliability observation (social_media_rumor) informing high-stakes decision",
            action_on_trigger="alert"
        )
    ],
    assessments_used=[...]
)
```

---

## Scenario 5: Conflicting Observations

### Context

A situation where observations contradict each other.

### Input

```python
situation = Situation(
    tenant_id="tenant-test",
    goal="Plan inventory for next quarter",
    time_horizon="near",
    stakes="medium",
    observations=[
        Observation(
            content="Demand will increase 20% next quarter",
            source="sales_forecast",
            reliability="medium"
        ),
        Observation(
            content="Demand will decrease 10% next quarter",
            source="market_analysis",
            reliability="medium"
        ),
        Observation(
            content="Supply chain is stable",
            source="operations",
            reliability="high"
        )
    ],
    candidate_actions=[
        ActionSpec(
            name="Increase inventory 20%",
            description="Stock up to meet expected demand increase",
            reversibility="costly"
        ),
        ActionSpec(
            name="Decrease inventory 10%",
            description="Reduce stock to match expected demand drop",
            reversibility="costly"
        ),
        ActionSpec(
            name="Maintain current levels",
            description="Keep inventory stable, monitor demand",
            reversibility="reversible"
        )
    ]
)
```

### Expected Agent Behavior

**ConstraintAgent**:
- No hard constraints

**StabilityAgent**:
- "Maintain current levels" scores highest (reversible)
- Both increase/decrease options are costly

**RealityCheckAgent**:
- CONFLICT DETECTED: Demand increase vs. decrease predictions
- Both sources have same reliability, cannot resolve
- Recommend data gathering before committing

### Expected Decision

```python
Decision(
    selected_action=ActionSpec(name="Maintain current levels", ...),
    robustness_basis="Conflicting forecasts detected. 'Maintain current levels' preserves optionality while situation clarifies.",
    monitoring=[
        MonitoringTrigger(
            condition="Monitor: Conflicting observations about demand (sales_forecast vs market_analysis)",
            action_on_trigger="alert"
        )
    ],
    assessments_used=[...]
)
```

---

## Scenario 6: All Actions Constrained

### Context

An edge case where all candidate actions have hard constraint violations.

### Input

```python
situation = Situation(
    tenant_id="tenant-test",
    goal="Resolve urgent production issue",
    time_horizon="immediate",
    stakes="high",
    observations=[
        Observation(
            content="Production is down, every minute costs $10,000",
            source="monitoring",
            reliability="high"
        ),
        Observation(
            content="Fix A requires restart, will cause 30-minute outage",
            source="engineering",
            reliability="high"
        ),
        Observation(
            content="Fix B has not been tested in production",
            source="engineering",
            reliability="high"
        )
    ],
    candidate_actions=[
        ActionSpec(
            name="Apply Fix A",
            description="Restart with known fix, 30-min outage",
            reversibility="costly"
        ),
        ActionSpec(
            name="Apply Fix B",
            description="Untested fix, may not work",
            reversibility="costly"
        ),
        ActionSpec(
            name="Do nothing",
            description="Wait for more information",
            reversibility="reversible",
            time_sensitivity="flexible"
        )
    ]
)
```

### Expected Agent Behavior

**ConstraintAgent**:
- "Do nothing" HARD CONSTRAINT: urgent situation + flexible time_sensitivity
- Other actions may have warnings but no hard constraints

**StabilityAgent**:
- All remaining options are "costly"
- May prefer Fix A (known behavior) over Fix B (unknown)

**RealityCheckAgent**:
- Flag untested nature of Fix B
- Note high cost of inaction

### Expected Decision

```python
Decision(
    selected_action=ActionSpec(name="Apply Fix A", ...),
    robustness_basis="'Do nothing' eliminated by urgency constraint. Between costly options, 'Apply Fix A' has more predictable outcomes.",
    monitoring=[
        MonitoringTrigger(
            condition="Monitor: Production restoration progress",
            action_on_trigger="alert"
        )
    ],
    assessments_used=[...]
)
```

---

## Scenario 7: Single Action Available

### Context

An edge case where only one action is provided.

### Input

```python
situation = Situation(
    tenant_id="tenant-test",
    goal="Respond to regulatory requirement",
    time_horizon="near",
    stakes="high",
    observations=[
        Observation(
            content="New regulation requires compliance by end of month",
            source="legal",
            reliability="high"
        )
    ],
    candidate_actions=[
        ActionSpec(
            name="Implement compliance changes",
            description="Make required system changes",
            reversibility="costly"
        )
    ]
)
```

### Expected Agent Behavior

**ConstraintAgent**:
- No hard constraints on the single action
- May note deadline awareness

**StabilityAgent**:
- Single action scored
- May note lack of alternatives

**RealityCheckAgent**:
- No contradictions
- May note limited options

### Expected Decision

```python
Decision(
    selected_action=ActionSpec(name="Implement compliance changes", ...),
    robustness_basis="Single candidate action with no hard constraint violations.",
    monitoring=[],
    assessments_used=[...]
)
```

---

## Scenario 8: Empty Observations

### Context

An edge case where no observations are provided.

### Input

```python
situation = Situation(
    tenant_id="tenant-test",
    goal="Make a decision",
    time_horizon="near",
    stakes="low",
    observations=[],
    candidate_actions=[
        ActionSpec(
            name="Option A",
            description="First option",
            reversibility="reversible"
        ),
        ActionSpec(
            name="Option B",
            description="Second option",
            reversibility="irreversible"
        )
    ]
)
```

### Expected Agent Behavior

**ConstraintAgent**:
- No observations to derive constraints from
- May return empty or minimal assessments

**StabilityAgent**:
- "Option A" scores higher (reversible)
- "Option B" scores lower (irreversible)

**RealityCheckAgent**:
- May flag lack of observations for decision-making
- Limited basis for assessment

### Expected Decision

```python
Decision(
    selected_action=ActionSpec(name="Option A", ...),
    robustness_basis="Limited observations. Selected most reversible option.",
    monitoring=[],
    assessments_used=[...]
)
```

---

## Using These Scenarios

### For Test Development

Each scenario can be converted into a test:

```python
def test_scenario_1_simple_reversible_choice():
    """Verify reversible option selected when no constraints."""
    situation = create_scenario_1_situation()
    
    decision = runner.run(situation)
    
    assert decision.selected_action.name == "Gradual rollout"
    assert "reversibility" in decision.robustness_basis.lower()
```

### For Manual Testing

Scenarios can be submitted to the API:

```bash
curl -X POST http://localhost:8000/decide \
  -H "Content-Type: application/json" \
  -d @scenario_1.json
```

### For Validation

Compare actual decisions against expected decisions to validate the framework behaves correctly.

---

## Scenario Coverage Matrix

| Scenario | Hard Constraint | Stability Warning | Reality Check | Edge Case |
|----------|-----------------|-------------------|---------------|-----------|
| 1: Simple | - | - | - | - |
| 2: Deadline | ✓ | - | ✓ | - |
| 3: High Stakes | - | ✓ | ✓ | - |
| 4: Low Reliability | - | - | ✓ | - |
| 5: Conflicts | - | - | ✓ | - |
| 6: All Constrained | ✓ | ✓ | ✓ | ✓ |
| 7: Single Action | - | - | - | ✓ |
| 8: No Observations | - | - | - | ✓ |

This coverage ensures all agent behaviors and edge cases are exercised.
