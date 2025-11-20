"""Smoke test to verify project structure and imports."""
import pytest


def test_import_src():
    """Test that main src package can be imported."""
    import src
    assert hasattr(src, '__version__')


def test_import_data_context():
    """Test that L1 data_context can be imported."""
    import src.data_context
    assert src.data_context is not None


def test_import_agents():
    """Test that L2 agents can be imported."""
    import src.agents
    assert src.agents is not None


def test_import_all_layers():
    """Test that all layers can be imported."""
    import src.retrain
    import src.qaqc_stage1
    import src.qaqc_stage2
    import src.strategy_opt
    import src.exec_frontend
    import src.quantum
    import src.onchain
    import src.telemetry
    import src.evaluation
    
    assert True  # If we get here, all imports worked
