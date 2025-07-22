"""
Example enhanced test demonstrating the new testing infrastructure.
This test showcases how to use fixtures, utilities, and assertions.
"""

import pytest
from tests.utils import (
    create_test_scenario,
    validate_api_response,
    assert_risk_score_valid,
    assert_alert_fields_present,
    MockDataFactory,
    MockEngineFactory
)


@pytest.mark.unit
class TestEnhancedTestInfrastructure:
    """Test class demonstrating enhanced testing infrastructure."""
    
    def test_basic_fixture_usage(self, sample_trade_data, sample_trader_info):
        """Test using basic fixtures from conftest.py."""
        # Test that fixtures are loaded correctly
        assert "trades" in sample_trade_data
        assert len(sample_trade_data["trades"]) > 0
        
        # Test trader info fixture
        assert "id" in sample_trader_info
        assert "role" in sample_trader_info
        assert sample_trader_info["access_level"] in ["low", "medium", "high"]
    
    def test_scenario_creation(self):
        """Test creating scenarios with test helpers."""
        # Create insider dealing scenario
        insider_scenario = create_test_scenario(
            "insider_dealing",
            instrument="TEST_STOCK",
            volume=100000,
            trader_id="test_exec"
        )
        
        assert "trades" in insider_scenario
        assert "trader_info" in insider_scenario
        assert "material_events" in insider_scenario
        assert insider_scenario["trader_info"]["role"] == "executive"
        assert insider_scenario["trader_info"]["access_level"] == "high"
        
        # Create spoofing scenario
        spoofing_scenario = create_test_scenario(
            "spoofing",
            instrument="COMMODITY_TEST",
            trader_id="test_trader"
        )
        
        assert "orders" in spoofing_scenario
        assert "trader_info" in spoofing_scenario
        assert len(spoofing_scenario["orders"]) >= 3  # Multiple orders for spoofing
    
    def test_mock_factories(self):
        """Test using mock factories for data generation."""
        # Test trade factory
        mock_trade = MockDataFactory.create_mock_trade(
            trade_id="factory_trade_001",
            volume=50000,
            price=100.0
        )
        
        assert mock_trade["id"] == "factory_trade_001"
        assert mock_trade["volume"] == 50000
        assert mock_trade["price"] == 100.0
        assert "timestamp" in mock_trade
        
        # Test trader factory
        mock_trader = MockDataFactory.create_mock_trader(
            trader_id="factory_trader",
            role="executive",
            access_level="high"
        )
        
        assert mock_trader["id"] == "factory_trader"
        assert mock_trader["role"] == "executive"
        assert mock_trader["access_level"] == "high"
    
    def test_engine_mocks(self):
        """Test using engine mock factories."""
        # Test mock data processor
        mock_processor = MockEngineFactory.create_mock_data_processor()
        result = mock_processor.process({"test": "data"})
        
        assert "trades" in result
        assert "trader_info" in result
        assert "timeframe" in result
        
        # Test mock Bayesian engine
        mock_engine = MockEngineFactory.create_mock_bayesian_engine()
        insider_result = mock_engine.analyze_insider_dealing({})
        
        assert "overall_score" in insider_result
        assert "risk_level" in insider_result
        assert "evidence_factors" in insider_result
        
        # Validate the mock result using custom assertions
        assert_risk_score_valid(insider_result)
    
    def test_custom_assertions(self):
        """Test using custom assertion functions."""
        # Test risk score validation
        valid_risk_score = {
            "overall_score": 0.6,
            "risk_level": "MEDIUM",
            "evidence_factors": {
                "MaterialInfo": 0.7,
                "TradingActivity": 0.5
            }
        }
        
        # This should pass
        assert_risk_score_valid(valid_risk_score)
        
        # Test alert validation
        valid_alert = {
            "id": "test_alert_001",
            "timestamp": "2024-01-15T10:00:00Z",
            "type": "INSIDER_DEALING",
            "severity": "HIGH",
            "risk_score": 0.8,
            "description": "Test alert",
            "trader_id": "test_trader"
        }
        
        # This should pass
        assert_alert_fields_present(valid_alert)
    
    def test_high_risk_scenario_fixture(self, high_risk_scenario):
        """Test using the high risk scenario fixture."""
        assert "trades" in high_risk_scenario
        assert "trader_info" in high_risk_scenario
        assert "material_events" in high_risk_scenario
        
        # Verify it's actually high risk
        trader = high_risk_scenario["trader_info"]
        assert trader["role"] == "executive"
        assert trader["access_level"] == "high"
        
        # Verify material event timing (after trade)
        trade_time = high_risk_scenario["trades"][0]["timestamp"]
        event_time = high_risk_scenario["material_events"][0]["timestamp"]
        assert event_time > trade_time  # Event after trade = suspicious timing
    
    def test_spoofing_scenario_fixture(self, spoofing_scenario):
        """Test using the spoofing scenario fixture."""
        assert "orders" in spoofing_scenario
        assert "trader_info" in spoofing_scenario
        
        orders = spoofing_scenario["orders"]
        
        # Check for typical spoofing pattern
        cancelled_orders = [o for o in orders if o["status"] == "cancelled"]
        filled_orders = [o for o in orders if o["status"] == "filled"]
        
        assert len(cancelled_orders) > 0, "Should have cancelled orders"
        assert len(filled_orders) > 0, "Should have some filled orders"
        
        # Check for layered orders (multiple large orders)
        large_orders = [o for o in cancelled_orders if o["volume"] >= 100000]
        assert len(large_orders) >= 2, "Should have multiple large cancelled orders"
    
    def test_configuration_integration(self, app_config):
        """Test integration with the configuration system."""
        assert app_config is not None
        assert app_config.environment == "testing"
        
        # Test configuration access
        risk_thresholds = app_config.get_risk_thresholds()
        assert "insider_dealing" in risk_thresholds
        assert "spoofing" in risk_thresholds
        
        # Verify testing environment has appropriate settings
        assert app_config.is_testing()
        assert not app_config.is_production()
    
    def test_complete_analysis_data_fixture(self, complete_analysis_data):
        """Test using the complete analysis data fixture."""
        assert "trades" in complete_analysis_data
        assert "orders" in complete_analysis_data
        assert "trader_info" in complete_analysis_data
        assert "material_events" in complete_analysis_data
        assert "market_data" in complete_analysis_data
        
        # Verify data consistency
        trades = complete_analysis_data["trades"]
        trader_info = complete_analysis_data["trader_info"]
        
        # All trades should be from the same trader
        for trade in trades:
            assert trade["trader_id"] == trader_info["id"]
    
    def test_mock_api_response_validation(self):
        """Test API response validation with mock data."""
        from tests.utils.mock_factories import MockResponseFactory
        
        # Create mock analysis response
        mock_response = MockResponseFactory.create_analysis_response(
            include_alerts=True,
            include_rationale=True
        )
        
        # Validate using test helper
        assert validate_api_response(mock_response)
        
        # Test individual components
        assert "analysis_id" in mock_response
        assert "risk_scores" in mock_response
        assert "alerts" in mock_response
        assert "regulatory_rationales" in mock_response
        
        # Validate risk scores
        for risk_type in ["insider_dealing", "spoofing"]:
            risk_score = mock_response["risk_scores"][risk_type]
            assert_risk_score_valid(risk_score)
        
        # Validate alerts
        for alert in mock_response["alerts"]:
            assert_alert_fields_present(alert)
    
    def test_performance_data_fixture(self, large_dataset):
        """Test using the large dataset fixture for performance scenarios."""
        assert "trades" in large_dataset
        assert len(large_dataset["trades"]) >= 1000
        
        # Verify data diversity
        instruments = set(trade["instrument"] for trade in large_dataset["trades"])
        traders = set(trade["trader_id"] for trade in large_dataset["trades"])
        
        assert len(instruments) >= 10, "Should have multiple instruments"
        assert len(traders) >= 5, "Should have multiple traders"
    
    @pytest.mark.mock
    def test_with_mock_marker(self, mock_bayesian_engine):
        """Test using pytest markers for test organization."""
        # This test is marked as 'mock' for filtering
        result = mock_bayesian_engine.analyze_insider_dealing({})
        assert_risk_score_valid(result)
    
    def test_temporary_directory_fixture(self, temp_dir):
        """Test using temporary directory fixture."""
        assert temp_dir.exists()
        assert temp_dir.is_dir()
        
        # Create a test file
        test_file = temp_dir / "test_output.txt"
        test_file.write_text("Test data")
        
        assert test_file.exists()
        assert test_file.read_text() == "Test data"
        
        # Directory will be cleaned up automatically after test