"""Boundary tests for core import isolation.

Verifies that core/ only imports from stdlib and dragonfly.core.
This is critical for maintaining the pure core architecture.
"""

import ast
import sys
from pathlib import Path

import pytest


def test_core_has_no_external_imports():
    """Verify core/ only imports from core/ and stdlib."""
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
                        errors.append(
                            f"{py_file.name}: imports external module '{alias.name}'"
                        )
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    module = node.module.split(".")[0]
                    if module not in stdlib_modules and module != "dragonfly":
                        errors.append(
                            f"{py_file.name}: imports from external module '{node.module}'"
                        )

    if errors:
        error_msg = "Core import violations:\n" + "\n".join(f"  - {e}" for e in errors)
        pytest.fail(error_msg)


def test_core_does_not_import_service_layer():
    """Verify core/ does not import from service/."""
    core_path = Path("src/dragonfly/core")

    errors = []

    for py_file in core_path.glob("*.py"):
        if py_file.name == "__init__.py":
            continue

        tree = ast.parse(py_file.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.module and "service" in node.module:
                    errors.append(
                        f"{py_file.name}: imports from service layer '{node.module}'"
                    )

    if errors:
        error_msg = "Core -> Service import violations:\n" + "\n".join(
            f"  - {e}" for e in errors
        )
        pytest.fail(error_msg)


def test_core_does_not_import_adapters():
    """Verify core/ does not import from adapters/."""
    core_path = Path("src/dragonfly/core")

    errors = []

    for py_file in core_path.glob("*.py"):
        if py_file.name == "__init__.py":
            continue

        tree = ast.parse(py_file.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.module and "adapter" in node.module:
                    errors.append(
                        f"{py_file.name}: imports from adapters '{node.module}'"
                    )

    if errors:
        error_msg = "Core -> Adapters import violations:\n" + "\n".join(
            f"  - {e}" for e in errors
        )
        pytest.fail(error_msg)


def test_all_core_modules_importable():
    """Verify all core modules can be imported."""
    from dragonfly.core import types
    from dragonfly.core import nodes
    from dragonfly.core import synth
    from dragonfly.core import graph

    assert types is not None
    assert nodes is not None
    assert synth is not None
    assert graph is not None
