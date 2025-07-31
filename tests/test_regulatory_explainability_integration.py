"""
Comprehensive tests for regulatory explainability integration across all models.

This test suite verifies that regulatory explainability is properly integrated
and functioning across all Bayesian risk typology models.
"""

import pytest
from datetime import datetime
from typing import Dict, Any, List

from src.core.regulatory_explainability import (
    RegulatoryExplainabilityEngine,
    EvidenceItem,
    EvidenceType,
    RegulatoryFramework
)

# Import all Bayesian models
from src.models.bayesian.spoofing.model import SpoofingModel
from src.models.bayesian.insider_dealing.model import InsiderDealingModel
from src.models.bayesian.market_cornering.model import MarketCorneringModel
from src.models.bayesian.circular_trading.model import CircularTradingModel
from src.models.bayesian.cross_desk_collusion.model import CrossDeskCollusionModel
from src.models.bayesian.commodity_manipulation.model import CommodityManipulationModel
from src.models.bayesian.economic_withholding.model import EconomicWithholdingModel
from src.models.bayesian.wash_trade_detection.model import WashTradeDetectionModel


class TestRegulatoryExplainabilityIntegration:
    """Test regulatory explainability integration across all models."""
    
    @pytest.fixture
    def sample_config(self):
        """Sample configuration for testing."""
        return {
            "regulatory_explainability": {
                "enabled": true,
                "frameworks": ["MAR_ARTICLE_8", "MAR_ARTICLE_12", "STOR_REQUIREMENTS"],
                "minimum_evidence_strength": 0.1,
                "minimum_reliability_score": 0.5
            }
        }
    
    @pytest.fixture
    def sample_evidence(self):
        """Sample evidence data for testing."""
        return {
            "order_pattern_anomaly": 0.8,
            "temporal_clustering": 0.7,
            "market_impact": 0.9,
            "communication_pattern": 0.6,
            "cross_account_correlation": 0.75
        }
    
    @pytest.fixture
    def sample_inference_result(self):
        """Sample inference result for testing."""
        return {
            "Risk": 0.85,
            "Confidence": 0.78
        }
    
    def test_spoofing_model_explainability_integration(self, sample_config, sample_evidence, sample_inference_result):
        """Test regulatory explainability integration in spoofing model."""
        model = SpoofingModel(config=sample_config)
        
        # Verify explainability engine is initialized
        assert hasattr(model, 'explainability_engine')
        assert isinstance(model.explainability_engine, RegulatoryExplainabilityEngine)
        
        # Test evidence generation
        evidence_items = model.generate_regulatory_explanation(
            evidence=sample_evidence,
            inference_result=sample_inference_result,
            account_id="TEST_ACC_001",
            timestamp=datetime.now().isoformat()
        )
        
        assert isinstance(evidence_items, list)
        assert len(evidence_items) > 0
        assert all(isinstance(item, EvidenceItem) for item in evidence_items)
        
        # Test regulatory framework mapping
        framework_mapping = model.get_regulatory_framework_mapping()
        assert isinstance(framework_mapping, dict)
        assert RegulatoryFramework.MAR_ARTICLE_12 in framework_mapping
        assert RegulatoryFramework.STOR_REQUIREMENTS in framework_mapping
    
    def test_insider_dealing_model_explainability_integration(self, sample_config, sample_evidence, sample_inference_result):
        """Test regulatory explainability integration in insider dealing model."""
        model = InsiderDealingModel(config=sample_config)
        
        # Verify explainability engine is initialized
        assert hasattr(model, 'explainability_engine')
        assert isinstance(model.explainability_engine, RegulatoryExplainabilityEngine)
        
        # Test evidence generation
        evidence_items = model.generate_regulatory_explanation(
            evidence=sample_evidence,
            inference_result=sample_inference_result,
            account_id="TEST_ACC_002",
            timestamp=datetime.now().isoformat()
        )
        
        assert isinstance(evidence_items, list)
        assert len(evidence_items) > 0
        
        # Test regulatory framework mapping
        framework_mapping = model.get_regulatory_framework_mapping()
        assert isinstance(framework_mapping, dict)
        assert RegulatoryFramework.MAR_ARTICLE_8 in framework_mapping
    
    def test_market_cornering_model_explainability_integration(self, sample_config, sample_evidence, sample_inference_result):
        """Test regulatory explainability integration in market cornering model."""
        model = MarketCorneringModel(config=sample_config)
        
        assert hasattr(model, 'explainability_engine')
        assert isinstance(model.explainability_engine, RegulatoryExplainabilityEngine)
        
        evidence_items = model.generate_regulatory_explanation(
            evidence=sample_evidence,
            inference_result=sample_inference_result,
            account_id="TEST_ACC_003",
            timestamp=datetime.now().isoformat()
        )
        
        assert isinstance(evidence_items, list)
        assert len(evidence_items) > 0
        
        framework_mapping = model.get_regulatory_framework_mapping()
        assert isinstance(framework_mapping, dict)
        assert RegulatoryFramework.MAR_ARTICLE_12 in framework_mapping
    
    def test_circular_trading_model_explainability_integration(self, sample_config, sample_evidence, sample_inference_result):
        """Test regulatory explainability integration in circular trading model."""
        model = CircularTradingModel(config=sample_config)
        
        assert hasattr(model, 'explainability_engine')
        assert isinstance(model.explainability_engine, RegulatoryExplainabilityEngine)
        
        evidence_items = model.generate_regulatory_explanation(
            evidence=sample_evidence,
            inference_result=sample_inference_result,
            account_id="TEST_ACC_004",
            timestamp=datetime.now().isoformat()
        )
        
        assert isinstance(evidence_items, list)
        assert len(evidence_items) > 0
        
        framework_mapping = model.get_regulatory_framework_mapping()
        assert isinstance(framework_mapping, dict)
        assert RegulatoryFramework.MAR_ARTICLE_12 in framework_mapping
    
    def test_cross_desk_collusion_model_explainability_integration(self, sample_config, sample_evidence, sample_inference_result):
        """Test regulatory explainability integration in cross desk collusion model."""
        model = CrossDeskCollusionModel(config=sample_config)
        
        assert hasattr(model, 'explainability_engine')
        assert isinstance(model.explainability_engine, RegulatoryExplainabilityEngine)
        
        evidence_items = model.generate_regulatory_explanation(
            evidence=sample_evidence,
            inference_result=sample_inference_result,
            account_id="TEST_ACC_005",
            timestamp=datetime.now().isoformat()
        )
        
        assert isinstance(evidence_items, list)
        assert len(evidence_items) > 0
        
        framework_mapping = model.get_regulatory_framework_mapping()
        assert isinstance(framework_mapping, dict)
        assert RegulatoryFramework.MAR_ARTICLE_8 in framework_mapping
    
    def test_commodity_manipulation_model_explainability_integration(self, sample_config, sample_evidence, sample_inference_result):
        """Test regulatory explainability integration in commodity manipulation model."""
        model = CommodityManipulationModel(config=sample_config)
        
        assert hasattr(model, 'explainability_engine')
        assert isinstance(model.explainability_engine, RegulatoryExplainabilityEngine)
        
        evidence_items = model.generate_regulatory_explanation(
            evidence=sample_evidence,
            inference_result=sample_inference_result,
            account_id="TEST_ACC_006",
            timestamp=datetime.now().isoformat()
        )
        
        assert isinstance(evidence_items, list)
        assert len(evidence_items) > 0
        
        framework_mapping = model.get_regulatory_framework_mapping()
        assert isinstance(framework_mapping, dict)
        assert RegulatoryFramework.MAR_ARTICLE_12 in framework_mapping
    
    def test_economic_withholding_model_explainability_integration(self, sample_config, sample_evidence, sample_inference_result):
        """Test regulatory explainability integration in economic withholding model."""
        model = EconomicWithholdingModel(config=sample_config)
        
        assert hasattr(model, 'explainability_engine')
        assert isinstance(model.explainability_engine, RegulatoryExplainabilityEngine)
        
        evidence_items = model.generate_regulatory_explanation(
            evidence=sample_evidence,
            inference_result=sample_inference_result,
            account_id="TEST_ACC_007",
            timestamp=datetime.now().isoformat()
        )
        
        assert isinstance(evidence_items, list)
        assert len(evidence_items) > 0
        
        framework_mapping = model.get_regulatory_framework_mapping()
        assert isinstance(framework_mapping, dict)
        assert RegulatoryFramework.STOR_REQUIREMENTS in framework_mapping
    
    def test_wash_trade_detection_model_explainability_integration(self, sample_config, sample_evidence, sample_inference_result):
        """Test regulatory explainability integration in wash trade detection model."""
        model = WashTradeDetectionModel(config=sample_config)
        
        # Note: Wash trade model may have different integration pattern
        # Check if it has explainability integration
        if hasattr(model, 'explainability_engine'):
            assert isinstance(model.explainability_engine, RegulatoryExplainabilityEngine)
        
        # Test if model supports regulatory explanation generation
        if hasattr(model, 'generate_regulatory_explanation'):
            evidence_items = model.generate_regulatory_explanation(
                evidence=sample_evidence,
                inference_result=sample_inference_result,
                account_id="TEST_ACC_008",
                timestamp=datetime.now().isoformat()
            )
            
            assert isinstance(evidence_items, list)
            assert len(evidence_items) > 0
    
    def test_all_models_have_explainability_integration(self, sample_config):
        """Test that all models have regulatory explainability integration."""
        model_classes = [
            SpoofingModel,
            InsiderDealingModel,
            MarketCorneringModel,
            CircularTradingModel,
            CrossDeskCollusionModel,
            CommodityManipulationModel,
            EconomicWithholdingModel,
            WashTradeDetectionModel
        ]
        
        for model_class in model_classes:
            model = model_class(config=sample_config)
            
            # Check for explainability engine
            assert hasattr(model, 'explainability_engine'), f"{model_class.__name__} missing explainability_engine"
            
            # Check for regulatory explanation method
            assert hasattr(model, 'generate_regulatory_explanation'), f"{model_class.__name__} missing generate_regulatory_explanation method"
            
            # Check for framework mapping method
            assert hasattr(model, 'get_regulatory_framework_mapping'), f"{model_class.__name__} missing get_regulatory_framework_mapping method"
    
    def test_evidence_item_structure(self, sample_config, sample_evidence, sample_inference_result):
        """Test that evidence items have correct structure across all models."""
        model = SpoofingModel(config=sample_config)
        
        evidence_items = model.generate_regulatory_explanation(
            evidence=sample_evidence,
            inference_result=sample_inference_result,
            account_id="TEST_ACC_STRUCTURE",
            timestamp=datetime.now().isoformat()
        )
        
        for evidence_item in evidence_items:
            # Check required fields
            assert hasattr(evidence_item, 'evidence_type')
            assert hasattr(evidence_item, 'account_id')
            assert hasattr(evidence_item, 'timestamp')
            assert hasattr(evidence_item, 'description')
            assert hasattr(evidence_item, 'strength')
            assert hasattr(evidence_item, 'reliability')
            assert hasattr(evidence_item, 'regulatory_relevance')
            assert hasattr(evidence_item, 'raw_data')
            
            # Check data types
            assert isinstance(evidence_item.evidence_type, EvidenceType)
            assert isinstance(evidence_item.account_id, str)
            assert isinstance(evidence_item.timestamp, datetime)
            assert isinstance(evidence_item.description, str)
            assert isinstance(evidence_item.strength, (int, float))
            assert isinstance(evidence_item.reliability, (int, float))
            assert isinstance(evidence_item.regulatory_relevance, dict)
            assert isinstance(evidence_item.raw_data, dict)
            
            # Check value ranges
            assert 0.0 <= evidence_item.strength <= 1.0
            assert 0.0 <= evidence_item.reliability <= 1.0
    
    def test_regulatory_framework_coverage(self, sample_config):
        """Test that all models cover appropriate regulatory frameworks."""
        expected_frameworks = {
            SpoofingModel: [RegulatoryFramework.MAR_ARTICLE_12, RegulatoryFramework.STOR_REQUIREMENTS],
            InsiderDealingModel: [RegulatoryFramework.MAR_ARTICLE_8, RegulatoryFramework.STOR_REQUIREMENTS],
            MarketCorneringModel: [RegulatoryFramework.MAR_ARTICLE_12, RegulatoryFramework.STOR_REQUIREMENTS],
            CircularTradingModel: [RegulatoryFramework.MAR_ARTICLE_12, RegulatoryFramework.STOR_REQUIREMENTS],
            CrossDeskCollusionModel: [RegulatoryFramework.MAR_ARTICLE_8, RegulatoryFramework.STOR_REQUIREMENTS],
            CommodityManipulationModel: [RegulatoryFramework.MAR_ARTICLE_12, RegulatoryFramework.STOR_REQUIREMENTS],
            EconomicWithholdingModel: [RegulatoryFramework.STOR_REQUIREMENTS]
        }
        
        for model_class, expected_frameworks_list in expected_frameworks.items():
            model = model_class(config=sample_config)
            framework_mapping = model.get_regulatory_framework_mapping()
            
            for framework in expected_frameworks_list:
                assert framework in framework_mapping, f"{model_class.__name__} missing {framework.value} framework"
    
    def test_performance_requirements(self, sample_config, sample_evidence, sample_inference_result):
        """Test that explainability generation meets performance requirements."""
        import time
        
        model = SpoofingModel(config=sample_config)
        
        # Test that explanation generation completes within reasonable time (< 1 second)
        start_time = time.time()
        
        evidence_items = model.generate_regulatory_explanation(
            evidence=sample_evidence,
            inference_result=sample_inference_result,
            account_id="TEST_ACC_PERF",
            timestamp=datetime.now().isoformat()
        )
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        assert execution_time < 1.0, f"Explainability generation took {execution_time:.2f} seconds, should be < 1.0 second"
        assert len(evidence_items) > 0, "Should generate at least one evidence item"


class TestRegulatoryFrameworkCompliance:
    """Test compliance with specific regulatory frameworks."""
    
    def test_mar_article_8_compliance(self, sample_config):
        """Test MAR Article 8 (Insider Dealing) compliance."""
        model = InsiderDealingModel(config=sample_config)
        framework_mapping = model.get_regulatory_framework_mapping()
        
        mar_article_8 = framework_mapping[RegulatoryFramework.MAR_ARTICLE_8]
        
        # Check required fields for MAR Article 8
        assert "description" in mar_article_8
        assert "key_indicators" in mar_article_8
        assert "evidence_threshold" in mar_article_8
        assert "reporting_requirements" in mar_article_8
        
        # Check evidence threshold is appropriate for insider dealing
        assert mar_article_8["evidence_threshold"] >= 0.6
    
    def test_mar_article_12_compliance(self, sample_config):
        """Test MAR Article 12 (Market Manipulation) compliance."""
        model = SpoofingModel(config=sample_config)
        framework_mapping = model.get_regulatory_framework_mapping()
        
        mar_article_12 = framework_mapping[RegulatoryFramework.MAR_ARTICLE_12]
        
        # Check required fields for MAR Article 12
        assert "description" in mar_article_12
        assert "key_indicators" in mar_article_12
        assert "evidence_threshold" in mar_article_12
        assert "reporting_requirements" in mar_article_12
        
        # Check evidence threshold is appropriate for market manipulation
        assert mar_article_12["evidence_threshold"] >= 0.6
    
    def test_stor_compliance(self, sample_config):
        """Test STOR (Suspicious Transaction and Order Reporting) compliance."""
        model = EconomicWithholdingModel(config=sample_config)
        framework_mapping = model.get_regulatory_framework_mapping()
        
        stor_requirements = framework_mapping[RegulatoryFramework.STOR_REQUIREMENTS]
        
        # Check required fields for STOR
        assert "description" in stor_requirements
        assert "key_indicators" in stor_requirements
        assert "evidence_threshold" in stor_requirements
        assert "reporting_requirements" in stor_requirements
        
        # Check evidence threshold is appropriate for STOR reporting
        assert stor_requirements["evidence_threshold"] >= 0.5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])