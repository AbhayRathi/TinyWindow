"""M0 Scaffolding: Basic structure validation tests."""


def test_src_packages_importable():
    """Verify all src packages can be imported."""
    import src.core
    import src.data_ingestion
    import src.market_agents
    import src.optimization
    import src.encryption

    assert src.core is not None
    assert src.data_ingestion is not None
    assert src.market_agents is not None
    assert src.optimization is not None
    assert src.encryption is not None


def test_placeholder_classes_exist():
    """Verify placeholder classes are defined."""
    from src.core import TradingEngine, Config
    from src.data_ingestion import DataIngestionManager
    from src.market_agents import MarketAgentManager, MarketAgent
    from src.optimization import RealTimeOptimizer
    from src.encryption import QuantumEncryption

    assert TradingEngine is not None
    assert Config is not None
    assert DataIngestionManager is not None
    assert MarketAgentManager is not None
    assert MarketAgent is not None
    assert RealTimeOptimizer is not None
    assert QuantumEncryption is not None


def test_directory_structure():
    """Verify TDD directory structure exists."""
    import os

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Check TDD directories exist
    tdd_dirs = [
        'data_context', 'agents', 'retrain', 'qaqc_stage1', 'qaqc_stage2',
        'strategy_opt', 'exec_frontend', 'quantum', 'onchain', 'telemetry', 'evaluation'
    ]

    for dir_name in tdd_dirs:
        dir_path = os.path.join(base_dir, dir_name)
        assert os.path.isdir(dir_path), f"Directory {dir_name} should exist"
