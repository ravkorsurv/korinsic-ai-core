"""
Mock factories for generating test objects and responses.
"""

from typing import Dict, Any, List, Optional
from unittest.mock import Mock, MagicMock
from datetime import datetime, timedelta


class MockDataFactory:
    """Factory for creating mock data objects."""
    
    @staticmethod
    def create_mock_trade(trade_id: str = "test_trade_001", **kwargs) -> Dict[str, Any]:
        """Create a mock trade object."""
        defaults = {
            "id": trade_id,
            "timestamp": datetime.now().isoformat() + "Z",
            "instrument": "TEST_STOCK",
            "volume": 10000,
            "price": 50.0,
            "side": "buy",
            "trader_id": "test_trader",
            "execution_venue": "NYSE",
            "order_type": "market"
        }
        defaults.update(kwargs)
        return defaults
    
    @staticmethod
    def create_mock_order(order_id: str = "test_order_001", **kwargs) -> Dict[str, Any]:
        """Create a mock order object."""
        defaults = {
            "id": order_id,
            "timestamp": datetime.now().isoformat() + "Z",
            "instrument": "TEST_STOCK", 
            "volume": 10000,
            "price": 50.0,
            "side": "buy",
            "status": "filled",
            "trader_id": "test_trader",
            "order_type": "limit"
        }
        defaults.update(kwargs)
        return defaults
    
    @staticmethod
    def create_mock_trader(trader_id: str = "test_trader", **kwargs) -> Dict[str, Any]:
        """Create a mock trader object."""
        defaults = {
            "id": trader_id,
            "name": "Test Trader",
            "role": "trader",
            "access_level": "medium",
            "department": "trading",
            "hire_date": "2020-01-01",
            "clearance_level": "standard"
        }
        defaults.update(kwargs)
        return defaults
    
    @staticmethod
    def create_mock_material_event(event_id: str = "test_event_001", **kwargs) -> Dict[str, Any]:
        """Create a mock material event object."""
        defaults = {
            "id": event_id,
            "timestamp": datetime.now().isoformat() + "Z",
            "type": "earnings_announcement",
            "description": "Test earnings announcement",
            "instruments_affected": ["TEST_STOCK"],
            "expected_impact": 0.05,
            "materiality_score": 0.8,
            "public_release": datetime.now().isoformat() + "Z"
        }
        defaults.update(kwargs)
        return defaults
    
    @staticmethod
    def create_mock_market_data(**kwargs) -> Dict[str, Any]:
        """Create mock market data."""
        defaults = {
            "volatility": 0.02,
            "liquidity": 0.8,
            "price_movement": 0.01,
            "volume": 1000000,
            "bid_ask_spread": 0.01,
            "market_cap": 10000000000,
            "average_volume": 800000
        }
        defaults.update(kwargs)
        return defaults


class MockEngineFactory:
    """Factory for creating mock engine components."""
    
    @staticmethod
    def create_mock_data_processor() -> Mock:
        """Create a mock data processor."""
        mock = Mock()
        mock.process.return_value = {
            "trades": [],
            "orders": [],
            "trader_info": {},
            "material_events": [],
            "market_data": {},
            "timeframe": "intraday",
            "instruments": []
        }
        return mock
    
    @staticmethod
    def create_mock_bayesian_engine() -> Mock:
        """Create a mock Bayesian engine."""
        mock = Mock()
        
        # Default return values for risk calculation methods
        default_insider_result = {
            "overall_score": 0.3,
            "risk_level": "LOW",
            "evidence_factors": {
                "MaterialInfo": 0.2,
                "TradingActivity": 0.3,
                "Timing": 0.1,
                "PriceImpact": 0.2
            },
            "model_type": "standard",
            "high_nodes": [],
            "critical_nodes": []
        }
        
        default_spoofing_result = {
            "overall_score": 0.2,
            "risk_level": "LOW",
            "evidence_factors": {
                "OrderPattern": 0.1,
                "CancellationRate": 0.2,
                "PriceMovement": 0.1,
                "VolumeRatio": 0.15
            },
            "model_type": "standard",
            "high_nodes": [],
            "critical_nodes": []
        }
        
        mock.analyze_insider_dealing.return_value = default_insider_result
        mock.analyze_insider_dealing_with_latent_intent = mock.analyze_insider_dealing
        mock.analyze_spoofing.return_value = default_spoofing_result
        mock.get_models_info.return_value = {
            "models": ["insider_dealing", "spoofing"],
            "version": "1.0.0"
        }
        
        return mock
    
    @staticmethod
    def create_mock_alert_generator() -> Mock:
        """Create a mock alert generator.""" 
        mock = Mock()
        
        default_alert = {
            "id": "test_alert_001",
            "timestamp": datetime.now().isoformat() + "Z",
            "type": "INSIDER_DEALING",
            "severity": "MEDIUM",
            "risk_score": 0.6,
            "description": "Test alert description",
            "trader_id": "test_trader",
            "instrument": "TEST_STOCK"
        }
        
        mock.generate_alerts.return_value = [default_alert]
        mock.get_historical_alerts.return_value = []
        
        return mock
    
    @staticmethod
    def create_mock_risk_calculator() -> Mock:
        """Create a mock risk calculator."""
        mock = Mock()
        mock.calculate_overall_risk.return_value = 0.4
        return mock


class MockResponseFactory:
    """Factory for creating mock API responses."""
    
    @staticmethod
    def create_analysis_response(include_alerts: bool = True, 
                               include_rationale: bool = False) -> Dict[str, Any]:
        """Create a mock analysis API response."""
        response = {
            "timestamp": datetime.now().isoformat() + "Z",
            "analysis_id": "analysis_123456789",
            "risk_scores": {
                "insider_dealing": {
                    "overall_score": 0.3,
                    "risk_level": "LOW",
                    "evidence_factors": {},
                    "model_type": "standard"
                },
                "spoofing": {
                    "overall_score": 0.2,
                    "risk_level": "LOW", 
                    "evidence_factors": {},
                    "model_type": "standard"
                },
                "overall_risk": 0.25
            },
            "alerts": [],
            "regulatory_rationales": [],
            "processed_data_summary": {
                "trades_analyzed": 1,
                "timeframe": "intraday",
                "instruments": ["TEST_STOCK"]
            }
        }
        
        if include_alerts:
            response["alerts"] = [
                {
                    "id": "alert_123",
                    "type": "INSIDER_DEALING",
                    "severity": "MEDIUM",
                    "risk_score": 0.6,
                    "description": "Suspicious trading pattern detected",
                    "timestamp": datetime.now().isoformat() + "Z",
                    "trader_id": "trader_001"
                }
            ]
        
        if include_rationale:
            response["regulatory_rationales"] = [
                {
                    "alert_id": "alert_123",
                    "deterministic_narrative": "Test regulatory rationale",
                    "inference_paths": [],
                    "voi_analysis": {},
                    "sensitivity_report": {},
                    "regulatory_frameworks": [],
                    "audit_trail": {}
                }
            ]
        
        return response
    
    @staticmethod
    def create_simulation_response(scenario_type: str = "insider_dealing") -> Dict[str, Any]:
        """Create a mock simulation API response."""
        return {
            "scenario_type": scenario_type,
            "parameters": {"num_trades": 10, "seed": 42},
            "risk_score": {
                "overall_score": 0.7,
                "risk_level": "HIGH",
                "evidence_factors": {},
                "model_type": "simulation"
            },
            "simulated_data": {
                "trades": [MockDataFactory.create_mock_trade()],
                "trader_info": MockDataFactory.create_mock_trader(),
                "market_data": MockDataFactory.create_mock_market_data()
            },
            "timestamp": datetime.now().isoformat() + "Z"
        }
    
    @staticmethod
    def create_models_info_response() -> Dict[str, Any]:
        """Create a mock models info API response."""
        return {
            "models": {
                "insider_dealing": {
                    "version": "1.0.0",
                    "nodes": 4,
                    "last_updated": datetime.now().isoformat() + "Z"
                },
                "spoofing": {
                    "version": "1.0.0", 
                    "nodes": 4,
                    "last_updated": datetime.now().isoformat() + "Z"
                }
            },
            "engine_version": "1.0.0",
            "timestamp": datetime.now().isoformat() + "Z"
        }
    
    @staticmethod
    def create_error_response(error_message: str = "Test error", 
                            status_code: int = 500) -> Dict[str, Any]:
        """Create a mock error response."""
        return {
            "error": error_message,
            "status_code": status_code,
            "timestamp": datetime.now().isoformat() + "Z"
        }


class MockDatabaseFactory:
    """Factory for creating mock database objects."""
    
    @staticmethod
    def create_mock_session() -> Mock:
        """Create a mock database session."""
        session = Mock()
        session.query.return_value = session
        session.filter.return_value = session
        session.filter_by.return_value = session
        session.order_by.return_value = session
        session.limit.return_value = session
        session.offset.return_value = session
        session.all.return_value = []
        session.first.return_value = None
        session.count.return_value = 0
        session.add.return_value = None
        session.commit.return_value = None
        session.rollback.return_value = None
        session.close.return_value = None
        return session
    
    @staticmethod
    def create_mock_alert_record(**kwargs) -> Mock:
        """Create a mock alert database record."""
        defaults = {
            "id": "alert_123",
            "trader_id": "test_trader",
            "alert_type": "INSIDER_DEALING",
            "risk_score": 0.6,
            "severity": "MEDIUM",
            "status": "OPEN",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        defaults.update(kwargs)
        
        mock_record = Mock()
        for key, value in defaults.items():
            setattr(mock_record, key, value)
        
        return mock_record