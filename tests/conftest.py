"""
Shared test configuration and fixtures for Kor.ai Surveillance Platform tests.
"""

import pytest
import sys
import os
from pathlib import Path

# Add src directory to Python path for imports
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

# Test configuration
@pytest.fixture(scope="session")
def test_config():
    """Shared test configuration."""
    return {
        "test_data_dir": Path(__file__).parent / "fixtures",
        "log_level": "DEBUG",
        "timeout": 30,
        "max_retries": 3
    }

@pytest.fixture(scope="session")
def sample_trade_data():
    """Sample trade data for testing."""
    return {
        "trades": [
            {
                "id": "trade_001",
                "timestamp": "2024-01-15T10:30:00Z",
                "instrument": "ENERGY_CORP",
                "volume": 100000,
                "price": 50.25,
                "side": "buy",
                "trader_id": "exec_trader_001"
            }
        ],
        "trader_info": {
            "id": "exec_trader_001",
            "role": "executive",
            "access_level": "high"
        }
    }

@pytest.fixture(scope="session")
def sample_material_events():
    """Sample material events for testing."""
    return [
        {
            "id": "event_001",
            "timestamp": "2024-01-16T09:00:00Z",
            "type": "earnings_announcement",
            "instruments_affected": ["ENERGY_CORP"]
        }
    ]