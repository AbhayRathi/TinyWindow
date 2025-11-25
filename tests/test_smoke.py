"""Smoke test to verify project structure and imports."""


def test_import_src():
    """Test that main src package can be imported."""
    import src

    assert hasattr(src, "__version__")


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
    import src.retrain  # noqa: F401
    import src.qaqc_stage1  # noqa: F401
    import src.qaqc_stage2  # noqa: F401
    import src.strategy_opt  # noqa: F401
    import src.exec_frontend  # noqa: F401
    import src.quantum  # noqa: F401
    import src.onchain  # noqa: F401
    import src.telemetry  # noqa: F401
    import src.evaluation  # noqa: F401

    assert True  # If we get here, all imports worked
