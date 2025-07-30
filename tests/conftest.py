"""
Pytest Configuration and Shared Fixtures

This module provides shared test fixtures, configuration, and utilities
for the person-centric surveillance test suite.
"""

import pytest
import json
import tempfile
import os
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional
from unittest.mock import Mock, patch

# Import test data factory
from tests.test_person_centric_surveillance import TestDataFactory


@pytest.fixture(scope="session")
def test_config():
    """Provide test configuration for all tests"""
    return TestDataFactory.create_test_config()


@pytest.fixture(scope="session")
def temp_config_file(test_config):
    """Create a temporary configuration file for testing"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(test_config, f, indent=2)
        config_file_path = f.name
    
    yield config_file_path
    
    # Cleanup
    if os.path.exists(config_file_path):
        os.unlink(config_file_path)


@pytest.fixture
def sample_trade_data():
    """Provide sample trade data for testing"""
    return [
        TestDataFactory.create_sample_trade_data(
            trader_id=f"TRADER00{i}",
            timestamp=datetime.now(timezone.utc) - timedelta(hours=i),
            quantity=1000 * (i + 1),
            price=100 + i * 2
        )
        for i in range(5)
    ]


@pytest.fixture
def sample_person_profile():
    """Provide sample person profile for testing"""
    return TestDataFactory.create_sample_person_profile()


@pytest.fixture
def sample_communication_data():
    """Provide sample communication data for testing"""
    return [
        {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "trader_id": "TRADER001",
            "type": "email",
            "content_sensitivity": 0.7,
            "external_communication": False
        },
        {
            "timestamp": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat(),
            "trader_id": "TRADER002",
            "type": "phone",
            "content_sensitivity": 0.9,
            "external_communication": True
        }
    ]


@pytest.fixture
def sample_hr_data():
    """Provide sample HR data for testing"""
    return [
        {
            "employee_id": "EMP001",
            "full_name": "John Doe",
            "email": "john.doe@company.com",
            "desk": "EQUITY_DESK",
            "trading_accounts": ["TRADER001", "TRADER002"],
            "access_level": "STANDARD"
        },
        {
            "employee_id": "EMP002",
            "full_name": "Jane Smith",
            "email": "jane.smith@company.com",
            "desk": "DERIVATIVES_DESK",
            "trading_accounts": ["TRADER003"],
            "access_level": "CONFIDENTIAL"
        }
    ]


@pytest.fixture
def mock_surveillance_engine():
    """Provide a mock surveillance engine for testing"""
    engine = Mock()
    engine.process_surveillance_data.return_value = {
        "alerts": [],
        "person_profiles": [],
        "processing_metrics": {
            "total_trades_processed": 0,
            "total_persons_identified": 0,
            "processing_time_seconds": 1.5
        }
    }
    return engine


@pytest.fixture
def mock_entity_resolution_service():
    """Provide a mock entity resolution service for testing"""
    service = Mock()
    service.resolve_trading_data_person_id.return_value = ("PERSON001", 0.95)
    service.add_hr_data.return_value = "PERSON001"
    return service


@pytest.fixture
def mock_evidence_aggregator():
    """Provide a mock evidence aggregator for testing"""
    aggregator = Mock()
    aggregator.aggregate_person_evidence.return_value = {
        "trading_evidence": {"strength": 0.7},
        "communication_evidence": {"strength": 0.6},
        "cross_account_patterns": {"correlation": 0.8}
    }
    return aggregator


@pytest.fixture
def mock_cross_typology_engine():
    """Provide a mock cross-typology engine for testing"""
    engine = Mock()
    engine.analyze_cross_typology_signals.return_value = [
        TestDataFactory.create_sample_cross_typology_signal()
    ]
    engine.calculate_escalation_factors.return_value = {
        "escalation_score": 0.75,
        "risk_clustering": 0.8
    }
    return engine


@pytest.fixture
def high_risk_scenario_data():
    """Provide high-risk scenario data for testing STOR and regulatory compliance"""
    return {
        "trade_data": [
            TestDataFactory.create_sample_trade_data(
                trader_id="HIGHRISK001",
                timestamp=datetime.now(timezone.utc) - timedelta(minutes=i*10),
                instrument="CONFIDENTIAL_STOCK",
                quantity=50000,  # Large quantities
                price=100 + i * 5  # Significant price movements
            )
            for i in range(8)
        ],
        "communication_data": [
            {
                "timestamp": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
                "trader_id": "HIGHRISK001",
                "type": "phone",
                "content_sensitivity": 0.95,
                "external_communication": True,
                "pre_trade_timing": True,
                "suspicious_keywords": ["insider information", "confidential"]
            }
        ],
        "hr_data": [
            {
                "employee_id": "EMP_HIGHRISK",
                "full_name": "High Risk Trader",
                "email": "highrisk@company.com",
                "desk": "PROPRIETARY_TRADING",
                "trading_accounts": ["HIGHRISK001"],
                "access_level": "CONFIDENTIAL",
                "compliance_flags": ["INSIDER_ACCESS"]
            }
        ]
    }


@pytest.fixture
def low_risk_scenario_data():
    """Provide low-risk scenario data for testing"""
    return {
        "trade_data": [
            TestDataFactory.create_sample_trade_data(
                trader_id="LOWRISK001",
                timestamp=datetime.now(timezone.utc) - timedelta(hours=i),
                quantity=1000,  # Normal quantities
                price=100  # Stable price
            )
            for i in range(3)
        ],
        "communication_data": [
            {
                "timestamp": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat(),
                "trader_id": "LOWRISK001",
                "type": "email",
                "content_sensitivity": 0.2,
                "external_communication": False
            }
        ],
        "hr_data": [
            {
                "employee_id": "EMP_LOWRISK",
                "full_name": "Low Risk Trader",
                "email": "lowrisk@company.com",
                "desk": "MARKET_MAKING",
                "trading_accounts": ["LOWRISK001"],
                "access_level": "STANDARD"
            }
        ]
    }


@pytest.fixture
def cross_account_scenario_data():
    """Provide cross-account coordination scenario data for testing"""
    base_time = datetime.now(timezone.utc)
    
    return {
        "trade_data": [
            # Account 1 trades
            TestDataFactory.create_sample_trade_data(
                trader_id="COORD001",
                timestamp=base_time - timedelta(minutes=i*5),
                quantity=5000,
                price=100 + i
            )
            for i in range(5)
        ] + [
            # Account 2 trades (coordinated timing)
            TestDataFactory.create_sample_trade_data(
                trader_id="COORD002",
                timestamp=base_time - timedelta(minutes=i*5 + 2),  # 2 minutes after account 1
                quantity=4000,
                price=100 + i
            )
            for i in range(5)
        ],
        "communication_data": [
            {
                "timestamp": (base_time - timedelta(minutes=30)).isoformat(),
                "trader_id": "COORD001",
                "type": "phone",
                "content_sensitivity": 0.8,
                "external_communication": False,
                "internal_recipient": "COORD002"
            }
        ],
        "hr_data": [
            {
                "employee_id": "EMP_COORD",
                "full_name": "Coordinated Trader",
                "email": "coord@company.com",
                "desk": "ARBITRAGE_DESK",
                "trading_accounts": ["COORD001", "COORD002"],
                "access_level": "STANDARD"
            }
        ]
    }


@pytest.fixture
def performance_test_data():
    """Provide large dataset for performance testing"""
    num_trades = 1000
    num_traders = 50
    
    return {
        "trade_data": [
            TestDataFactory.create_sample_trade_data(
                trader_id=f"PERF_TRADER{i % num_traders:03d}",
                timestamp=datetime.now(timezone.utc) - timedelta(minutes=i),
                quantity=1000 + (i % 5000),
                price=100 + (i % 50)
            )
            for i in range(num_trades)
        ],
        "communication_data": [
            {
                "timestamp": (datetime.now(timezone.utc) - timedelta(hours=i)).isoformat(),
                "trader_id": f"PERF_TRADER{i:03d}",
                "type": "email",
                "content_sensitivity": 0.3 + (i % 5) * 0.1,
                "external_communication": i % 10 == 0
            }
            for i in range(num_traders)
        ]
    }


# Test utilities
class TestUtils:
    """Utility functions for testing"""
    
    @staticmethod
    def assert_valid_probability(value: float, field_name: str = "probability"):
        """Assert that a value is a valid probability (0.0 to 1.0)"""
        assert isinstance(value, (int, float)), f"{field_name} should be numeric"
        assert 0.0 <= value <= 1.0, f"{field_name} should be between 0.0 and 1.0, got {value}"
    
    @staticmethod
    def assert_valid_timestamp(timestamp: Any, field_name: str = "timestamp"):
        """Assert that a timestamp is valid"""
        if isinstance(timestamp, str):
            # Try to parse ISO format
            try:
                datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            except ValueError:
                pytest.fail(f"{field_name} should be valid ISO format timestamp")
        elif isinstance(timestamp, datetime):
            # Already a datetime object
            pass
        else:
            pytest.fail(f"{field_name} should be datetime or ISO string")
    
    @staticmethod
    def assert_alert_structure(alert: Dict[str, Any]):
        """Assert that an alert has the required structure"""
        required_fields = [
            "alert_id", "person_id", "person_name", "risk_typology",
            "probability_score", "confidence_score", "severity",
            "involved_accounts", "timestamp"
        ]
        
        for field in required_fields:
            assert field in alert, f"Alert should have {field} field"
        
        TestUtils.assert_valid_probability(alert["probability_score"], "probability_score")
        TestUtils.assert_valid_probability(alert["confidence_score"], "confidence_score")
        TestUtils.assert_valid_timestamp(alert["timestamp"], "timestamp")
        
        assert isinstance(alert["involved_accounts"], list), "involved_accounts should be a list"
        assert len(alert["involved_accounts"]) > 0, "involved_accounts should not be empty"
    
    @staticmethod
    def assert_person_profile_structure(profile: Dict[str, Any]):
        """Assert that a person profile has the required structure"""
        required_fields = [
            "person_id", "person_name", "linked_accounts", "identity_confidence"
        ]
        
        for field in required_fields:
            assert field in profile, f"Person profile should have {field} field"
        
        TestUtils.assert_valid_probability(profile["identity_confidence"], "identity_confidence")
        assert isinstance(profile["linked_accounts"], list), "linked_accounts should be a list"
    
    @staticmethod
    def assert_processing_metrics_structure(metrics: Dict[str, Any]):
        """Assert that processing metrics have the required structure"""
        expected_fields = [
            "total_trades_processed", "total_persons_identified", "processing_time_seconds"
        ]
        
        for field in expected_fields:
            if field in metrics:
                assert isinstance(metrics[field], (int, float)), f"{field} should be numeric"
                if "time" in field:
                    assert metrics[field] >= 0, f"{field} should be non-negative"


@pytest.fixture
def test_utils():
    """Provide test utilities"""
    return TestUtils


# Performance test configuration
@pytest.fixture
def performance_config():
    """Configuration for performance tests"""
    return {
        "max_processing_time_seconds": 30,  # Maximum allowed processing time
        "max_memory_mb": 500,  # Maximum memory usage in MB
        "min_throughput_trades_per_second": 100,  # Minimum throughput requirement
    }


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "e2e: mark test as an end-to-end test"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as a performance test"
    )
    config.addinivalue_line(
        "markers", "regulatory: mark test as a regulatory compliance test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test names"""
    for item in items:
        # Add markers based on test file names
        if "test_person_centric_surveillance" in str(item.fspath):
            if "TestEntityResolution" in str(item.cls):
                item.add_marker(pytest.mark.unit)
            elif "TestIntegrationScenarios" in str(item.cls):
                item.add_marker(pytest.mark.integration)
            elif "TestEndToEndScenarios" in str(item.cls):
                item.add_marker(pytest.mark.e2e)
            elif "TestPerformanceAndStress" in str(item.cls):
                item.add_marker(pytest.mark.performance)
                item.add_marker(pytest.mark.slow)
        
        elif "test_regulatory_compliance" in str(item.fspath):
            item.add_marker(pytest.mark.regulatory)
            if "TestSTORCompliance" in str(item.cls):
                item.add_marker(pytest.mark.integration)
        
        # Mark slow tests
        if any(keyword in item.name.lower() for keyword in ["large_dataset", "performance", "stress"]):
            item.add_marker(pytest.mark.slow)