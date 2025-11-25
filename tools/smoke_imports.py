#!/usr/bin/env python
"""
Smoke test for all module imports.

Ensures all top-level modules can be imported without errors.
"""
import sys
import os
import importlib

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


MODULES_TO_TEST = [
    "src",
    "src.data_context",
    "src.data_context.embeddings",
    "src.data_context.features",
    "src.data_context.feeds",
    "src.data_context.models",
    "src.data_context.snapshot",
    "src.data_context.splits",
    "src.agents",
    "src.agents.base",
    "src.agents.common",
    "src.agents.interfaces",
    "src.retrain",
    "src.qaqc_stage1",
    "src.qaqc_stage2",
    "src.strategy_opt",
    "src.exec_frontend",
    "src.quantum",
    "src.onchain",
    "src.telemetry",
    "src.evaluation",
]


def test_import(module_name):
    """Test if a module can be imported."""
    try:
        importlib.import_module(module_name)
        print(f"✓ {module_name}")
        return True
    except Exception as e:
        print(f"❌ {module_name}: {e}")
        return False


def main():
    """Run smoke import tests."""
    print("=" * 60)
    print("Running smoke import tests...")
    print("=" * 60)

    results = [test_import(module) for module in MODULES_TO_TEST]

    passed = sum(results)
    failed = len(results) - passed

    print("=" * 60)
    print(f"Results: {passed}/{len(results)} modules imported successfully")

    if failed > 0:
        print(f"❌ {failed} modules failed to import")
        return 1
    else:
        print("✓ All modules imported successfully")
        return 0


if __name__ == "__main__":
    sys.exit(main())
