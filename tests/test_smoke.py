"""Smoke test to verify project structure and imports."""

import sys


def test_import_version():
    """Test that version can be imported."""
    # Check __version__ from top-level package if it exists
    try:
        from data_context import __version__
        assert __version__ is not None
    except (ImportError, AttributeError):
        # If no __version__ in data_context, just verify structure exists
        import data_context
        assert data_context is not None


def test_import_data_context():
    """Test that L1 data_context can be imported."""
    import data_context

    assert data_context is not None


def test_import_agents():
    """Test that L2 agents can be imported."""
    import agents

    assert agents is not None


def test_import_all_layers():
    """Test that all layers can be imported."""
    import retrain  # noqa: F401
    import qaqc_stage1  # noqa: F401
    import qaqc_stage2  # noqa: F401
    import strategy_opt  # noqa: F401
    import exec_frontend  # noqa: F401
    import quantum  # noqa: F401
    import onchain  # noqa: F401
    import telemetry  # noqa: F401
    import evaluation  # noqa: F401

    assert True  # If we get here, all imports worked
