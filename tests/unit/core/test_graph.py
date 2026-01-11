"""Unit tests for graph specification."""

import pytest

from dragonfly.core.graph import GraphSpec, PHASE1_GRAPH


class TestGraphSpec:
    """Tests for GraphSpec dataclass."""

    def test_graph_spec_creation(self):
        """GraphSpec creates with nodes and adjacency."""
        graph = GraphSpec(
            nodes=["a", "b", "c"],
            adjacency={
                "a": ["c"],
                "b": ["c"],
                "c": [],
            }
        )
        
        assert graph.nodes == ["a", "b", "c"]
        assert graph.adjacency == {"a": ["c"], "b": ["c"], "c": []}

    def test_graph_spec_nodes_are_ordered(self):
        """Nodes maintain their order."""
        graph = GraphSpec(
            nodes=["first", "second", "third"],
            adjacency={"first": [], "second": [], "third": []}
        )
        
        assert graph.nodes[0] == "first"
        assert graph.nodes[1] == "second"
        assert graph.nodes[2] == "third"


class TestPhase1Graph:
    """Tests for the PHASE1_GRAPH constant."""

    def test_phase1_graph_has_four_nodes(self):
        """PHASE1_GRAPH has 4 nodes."""
        assert len(PHASE1_GRAPH.nodes) == 4

    def test_phase1_graph_has_required_nodes(self):
        """PHASE1_GRAPH contains required node names."""
        assert "constraint" in PHASE1_GRAPH.nodes
        assert "stability" in PHASE1_GRAPH.nodes
        assert "reality_check" in PHASE1_GRAPH.nodes
        assert "synthesis" in PHASE1_GRAPH.nodes

    def test_all_agents_point_to_synthesis(self):
        """All agent nodes point to synthesis."""
        assert PHASE1_GRAPH.adjacency["constraint"] == ["synthesis"]
        assert PHASE1_GRAPH.adjacency["stability"] == ["synthesis"]
        assert PHASE1_GRAPH.adjacency["reality_check"] == ["synthesis"]

    def test_synthesis_is_terminal(self):
        """Synthesis node has no successors (terminal)."""
        assert PHASE1_GRAPH.adjacency["synthesis"] == []

    def test_phase1_graph_is_valid(self):
        """PHASE1_GRAPH is structurally valid."""
        # All nodes in adjacency are defined
        for node in PHASE1_GRAPH.adjacency:
            assert node in PHASE1_GRAPH.nodes
        
        # All adjacency targets are defined nodes
        for node, successors in PHASE1_GRAPH.adjacency.items():
            for successor in successors:
                assert successor in PHASE1_GRAPH.nodes
