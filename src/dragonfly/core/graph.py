"""Graph specification for the Dragonfly Agent Framework.

This module defines the pure graph structure as adjacency,
independent of any execution framework (like LangGraph).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class GraphSpec:
    """Pure specification of an agent graph.

    This dataclass defines the structure of a decision graph
    without any execution semantics. It can be used by different
    runners (LangGraph, custom, etc.) to execute the graph.

    Attributes:
        nodes: List of node names in suggested execution order
        adjacency: Mapping from node name to list of successor node names
    """

    nodes: list[str]
    adjacency: dict[str, list[str]]


# Phase 1 graph: 3 agents feeding into synthesis
PHASE1_GRAPH = GraphSpec(
    nodes=["constraint", "stability", "reality_check", "synthesis"],
    adjacency={
        "constraint": ["synthesis"],
        "stability": ["synthesis"],
        "reality_check": ["synthesis"],
        "synthesis": [],  # Terminal node
    },
)
