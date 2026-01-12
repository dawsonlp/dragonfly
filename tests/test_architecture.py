"""Architectural tests for the Dragonfly framework.

These tests verify architectural constraints and non-functional requirements.
"""

import ast
import sys
import time
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from dragonfly.service.api.main import app


def test_core_has_no_external_imports():
    """Core modules only import from stdlib and dragonfly.core.
    
    This verifies the pure-core architectural constraint.
    """
    core_path = Path("src/dragonfly/core")
    stdlib_modules = set(sys.stdlib_module_names)

    errors = []

    for py_file in core_path.glob("*.py"):
        if py_file.name == "__init__.py":
            continue

        tree = ast.parse(py_file.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module = alias.name.split(".")[0]
                    if module not in stdlib_modules and module != "dragonfly":
                        errors.append(f"{py_file.name}: imports '{alias.name}'")
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    module = node.module.split(".")[0]
                    if module not in stdlib_modules and module != "dragonfly":
                        errors.append(f"{py_file.name}: imports from '{node.module}'")

    assert not errors, f"Core import violations: {errors}"


def test_decision_latency_under_500ms():
    """Decisions complete in under 500ms (no LLM latency)."""
    client = TestClient(app)
    
    request = {
        "tenant_id": "test",
        "goal": "Performance test",
        "time_horizon": "near",
        "stakes": "medium",
        "observations": [
            {"content": "Test observation", "source": "test", "reliability": "high"}
        ],
        "candidate_actions": [
            {"name": "Option A", "description": "First", "reversibility": "reversible"},
            {"name": "Option B", "description": "Second", "reversibility": "irreversible"},
        ]
    }
    
    start = time.perf_counter()
    response = client.post("/api/v1/decide", json=request)
    elapsed = time.perf_counter() - start
    
    assert response.status_code == 200
    assert elapsed < 0.5, f"Decision took {elapsed:.3f}s, expected < 0.5s"
