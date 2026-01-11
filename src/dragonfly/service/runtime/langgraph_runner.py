"""LangGraph runner for the Dragonfly Agent Framework.

This module provides the service-layer orchestration that executes
the core decision graph using LangGraph for state management.
"""

from __future__ import annotations

from typing import TypedDict

from langgraph.graph import StateGraph, END

from dragonfly.core.nodes import (
    ConstraintAgent,
    RealityCheckAgent,
    StabilityAgent,
)
from dragonfly.core.synth import synthesize
from dragonfly.core.types import (
    Assessment,
    Decision,
    Situation,
)


class DragonflyState(TypedDict):
    """State container for the Dragonfly decision graph.

    Attributes:
        situation: The decision situation being processed
        assessments: Accumulated assessments from all agents
        decision: The final decision (set by synthesis node)
    """

    situation: Situation
    assessments: list[Assessment]
    decision: Decision | None


def _constraint_node(state: DragonflyState) -> dict:
    """Execute ConstraintAgent and add assessments to state."""
    agent = ConstraintAgent()
    new_assessments = agent.assess(state["situation"])
    return {"assessments": state["assessments"] + new_assessments}


def _stability_node(state: DragonflyState) -> dict:
    """Execute StabilityAgent and add assessments to state."""
    agent = StabilityAgent()
    new_assessments = agent.assess(state["situation"])
    return {"assessments": state["assessments"] + new_assessments}


def _reality_check_node(state: DragonflyState) -> dict:
    """Execute RealityCheckAgent and add assessments to state."""
    agent = RealityCheckAgent()
    new_assessments = agent.assess(state["situation"])
    return {"assessments": state["assessments"] + new_assessments}


def _synthesis_node(state: DragonflyState) -> dict:
    """Execute synthesis and produce decision."""
    decision = synthesize(state["situation"], state["assessments"])
    return {"decision": decision}


def _build_graph() -> StateGraph:
    """Build the LangGraph state graph for Phase 1.

    The graph structure:
    - START -> constraint, stability, reality_check (parallel-ish execution)
    - constraint -> synthesis
    - stability -> synthesis
    - reality_check -> synthesis
    - synthesis -> END
    """
    # Create the graph with our state type
    graph = StateGraph(DragonflyState)

    # Add nodes
    graph.add_node("constraint", _constraint_node)
    graph.add_node("stability", _stability_node)
    graph.add_node("reality_check", _reality_check_node)
    graph.add_node("synthesis", _synthesis_node)

    # Set entry point - start with all three agents
    graph.set_entry_point("constraint")

    # Add edges: each agent leads to synthesis
    # For Phase 1, we execute sequentially: constraint -> stability -> reality_check -> synthesis
    graph.add_edge("constraint", "stability")
    graph.add_edge("stability", "reality_check")
    graph.add_edge("reality_check", "synthesis")
    graph.add_edge("synthesis", END)

    return graph


class DragonflyRunner:
    """Runner that executes the Dragonfly decision graph.

    This class provides the main entry point for running decisions
    through the framework. It uses LangGraph for state management
    but hides implementation details from callers.
    """

    def __init__(self) -> None:
        """Initialize the runner with a compiled graph."""
        graph = _build_graph()
        self._app = graph.compile()

    def run(self, situation: Situation) -> Decision:
        """Execute the decision graph for a situation.

        Args:
            situation: The decision situation to process

        Returns:
            The Decision produced by synthesis

        Raises:
            ValueError: If no decision is produced
        """
        initial_state: DragonflyState = {
            "situation": situation,
            "assessments": [],
            "decision": None,
        }

        # Execute the graph
        result = self._app.invoke(initial_state)

        if result["decision"] is None:
            raise ValueError("Graph execution did not produce a decision")

        return result["decision"]


# Singleton runner instance
_runner: DragonflyRunner | None = None


def get_runner() -> DragonflyRunner:
    """Get or create the singleton runner instance."""
    global _runner
    if _runner is None:
        _runner = DragonflyRunner()
    return _runner
