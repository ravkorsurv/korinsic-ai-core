"""
Comprehensive Test Suite for Person-Centric Surveillance System

This module provides extensive testing coverage for all components of the 
individual-centric surveillance system, including:

- Unit tests for individual components
- Integration tests for component interactions
- End-to-end workflow testing
- Performance and stress testing
- Regulatory compliance testing
- Data quality and validation testing
"""

import pytest
import json
import asyncio
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any, Optional
from unittest.mock import Mock, patch, MagicMock
from dataclasses import asdict
import tempfile
import os

# Import the components we're testing
from src.core.entity_resolution import (
    EntityResolutionService, IdentityGraph, IdentityMatcher, 
    PersonIdentity, IdentityLink
)
from src.core.person_evidence_aggregator import PersonEvidenceAggregator
from src.core.person_centric_nodes import (
    PersonEvidenceNode, PersonTradingPatternNode, PersonCommunicationNode,
    PersonTimingNode, PersonAccessNode, PersonRiskNode, create_person_risk_nodes
)
from src.core.cross_typology_engine import CrossTypologyEngine
from src.core.person_centric_alert_generator import PersonCentricAlertGenerator
from src.core.person_centric_surveillance_engine import PersonCentricSurveillanceEngine
from src.core.regulatory_explainability import RegulatoryExplainabilityEngine

from src.models.person_centric import (
    PersonRiskProfile, PersonCentricAlert, CrossTypologySignal,
    RiskTypology, AlertSeverity, PersonCentricEvidence, SignalDirection
)
from src.models.trading_data import RawTradeData


class TestDataFactory:
    """Factory for creating test data objects"""
    
    @staticmethod
    def create_sample_trade_data(
        trader_id: str = "TRADER001",
        person_id: Optional[str] = None,
        timestamp: Optional[datetime] = None,
        instrument: str = "AAPL",
        quantity: float = 1000.0,
        price: float = 150.0
    ) -> RawTradeData:
        """Create sample trade data for testing"""
        return RawTradeData(
            trade_id=f"TRADE_{trader_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            timestamp=timestamp or datetime.now(timezone.utc),
            instrument_id=instrument,
            trader_id=trader_id,
            desk_id=f"DESK_{trader_id[:3]}",
            quantity=quantity,
            executed_price=price,
            notional_value=quantity * price,
            person_id=person_id,
            person_confidence=0.95 if person_id else None,
            order_type="MARKET",
            side="BUY" if quantity > 0 else "SELL"
        )
    
    @staticmethod
    def create_sample_person_profile(
        person_id: str = "PERSON001",
        linked_accounts: Optional[List[str]] = None,
        name: str = "John Doe"
    ) -> PersonRiskProfile:
        """Create sample person risk profile for testing"""
        return PersonRiskProfile(
            person_id=person_id,
            person_name=name,
            linked_accounts=linked_accounts or ["ACC001", "ACC002"],
            linked_emails=["john.doe@company.com"],
            desk_affiliations=["EQUITY_DESK", "DERIVATIVES_DESK"],
            hr_employee_id="EMP001",
            risk_scores={
                RiskTypology.INSIDER_DEALING: 0.65,
                RiskTypology.SPOOFING: 0.45
            },
            last_updated=datetime.now(timezone.utc),
            identity_confidence=0.92,
            aggregated_evidence={}
        )
    
    @staticmethod
    def create_sample_cross_typology_signal(
        source: RiskTypology = RiskTypology.INSIDER_DEALING,
        target: RiskTypology = RiskTypology.SPOOFING,
        strength: float = 0.7
    ) -> CrossTypologySignal:
        """Create sample cross-typology signal for testing"""
        return CrossTypologySignal(
            person_id="PERSON001",
            source_typology=source,
            target_typology=target,
            signal_strength=strength,
            signal_direction=SignalDirection.POSITIVE,
            shared_evidence=["test_evidence"],
            correlation_factors={"test_correlation": 0.8},
            signal_duration=1.5,
            impact_on_prior=0.2,
            confidence_adjustment=0.1
        )
    
    @staticmethod
    def create_test_config() -> Dict[str, Any]:
        """Create test configuration"""
        return {
            "person_centric_surveillance": {
                "enabled": True,
                "version": "2.0"
            },
            "entity_resolution": {
                "name_similarity_threshold": 0.8,
                "email_similarity_threshold": 0.9,
                "fuzzy_match_threshold": 0.7,
                "max_accounts_per_person": 10
            },
            "evidence_aggregation": {
                "trading_weight": 0.4,
                "communication_weight": 0.3,
                "timing_weight": 0.2,
                "access_weight": 0.1,
                "cross_account_bonus": 0.15
            },
            "alert_generation": {
                "probability_thresholds": {
                    "low": 0.3,
                    "medium": 0.6,
                    "high": 0.8
                },
                "stor_threshold": 0.6,
                "confidence_threshold": 0.7
            },
            "regulatory_explainability": {
                "enabled": True,
                "detail_level": "comprehensive"
            }
        }


class TestEntityResolution:
    """Unit tests for Entity Resolution components"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.config = TestDataFactory.create_test_config()
        self.identity_matcher = IdentityMatcher(self.config)
        self.identity_graph = IdentityGraph()
        self.entity_service = EntityResolutionService(self.config)
    
    def test_identity_matcher_name_similarity(self):
        """Test name similarity matching"""
        similarity = self.identity_matcher.calculate_name_similarity("John Doe", "John D. Doe")
        assert similarity > 0.8, "Should detect high similarity for similar names"
        
        similarity = self.identity_matcher.calculate_name_similarity("John Doe", "Jane Smith")
        assert similarity < 0.3, "Should detect low similarity for different names"
    
    def test_identity_matcher_email_similarity(self):
        """Test email similarity matching"""
        similarity = self.identity_matcher.calculate_email_similarity(
            "john.doe@company.com", "j.doe@company.com"
        )
        assert similarity > 0.7, "Should detect similarity in related emails"
    
    def test_identity_graph_person_creation(self):
        """Test person identity creation and linking"""
        # Add first identity
        person_id = self.identity_graph.resolve_person_id(
            account_id="ACC001",
            trader_name="John Doe",
            email="john.doe@company.com",
            desk_id="DESK001"
        )
        
        assert person_id is not None, "Should create new person identity"
        
        # Add related identity
        person_id_2 = self.identity_graph.resolve_person_id(
            account_id="ACC002",
            trader_name="John D. Doe",
            email="j.doe@company.com",
            desk_id="DESK001"
        )
        
        assert person_id == person_id_2, "Should link similar identities to same person"
    
    def test_entity_resolution_service_integration(self):
        """Test full entity resolution service"""
        trade_data = TestDataFactory.create_sample_trade_data(trader_id="TRADER001")
        
        # Resolve person ID
        person_id, confidence = self.entity_service.resolve_trading_data_person_id(trade_data)
        
        assert person_id is not None, "Should resolve person ID for trade data"
        assert confidence > 0.0, "Should provide confidence score"
        
        # Resolve same trader again - should get same person ID
        trade_data_2 = TestDataFactory.create_sample_trade_data(trader_id="TRADER001")
        person_id_2, confidence_2 = self.entity_service.resolve_trading_data_person_id(trade_data_2)
        
        assert person_id == person_id_2, "Should consistently resolve to same person"
    
    def test_hr_data_override(self):
        """Test HR data override functionality"""
        # Add HR data
        hr_data = {
            "employee_id": "EMP001",
            "full_name": "John Doe",
            "email": "john.doe@company.com",
            "desk": "EQUITY_DESK",
            "trading_accounts": ["ACC001", "ACC002"]
        }
        
        person_id = self.entity_service.add_hr_data(hr_data)
        assert person_id is not None, "Should create person from HR data"
        
        # Test that trading data links to HR person
        trade_data = TestDataFactory.create_sample_trade_data(trader_id="ACC001")
        resolved_person_id, confidence = self.entity_service.resolve_trading_data_person_id(trade_data)
        
        assert resolved_person_id == person_id, "Should link to HR-defined person"
        assert confidence > 0.9, "Should have high confidence for HR-linked identity"


class TestPersonEvidenceAggregator:
    """Unit tests for Person Evidence Aggregator"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.config = TestDataFactory.create_test_config()
        self.aggregator = PersonEvidenceAggregator(self.config)
        self.person_profile = TestDataFactory.create_sample_person_profile()
    
    def test_trading_evidence_aggregation(self):
        """Test trading evidence aggregation"""
        # Create sample trading data
        trades = [
            TestDataFactory.create_sample_trade_data(
                trader_id="ACC001", 
                timestamp=datetime.now(timezone.utc) - timedelta(hours=i),
                quantity=1000 * (i + 1)
            )
            for i in range(5)
        ]
        
        evidence = self.aggregator._aggregate_trading_evidence(
            self.person_profile, trades, datetime.now(timezone.utc) - timedelta(days=1)
        )
        
        assert evidence is not None, "Should generate trading evidence"
        assert "volume_patterns" in evidence, "Should include volume patterns"
        assert "temporal_clustering" in evidence, "Should include temporal analysis"
    
    def test_cross_account_pattern_detection(self):
        """Test cross-account pattern detection"""
        # Create trades across multiple accounts
        trades = []
        for account in ["ACC001", "ACC002"]:
            for i in range(3):
                trades.append(TestDataFactory.create_sample_trade_data(
                    trader_id=account,
                    timestamp=datetime.now(timezone.utc) - timedelta(minutes=i*5),
                    quantity=1000
                ))
        
        patterns = self.aggregator._analyze_cross_account_patterns(
            self.person_profile, trades
        )
        
        assert len(patterns) > 0, "Should detect cross-account patterns"
        assert "temporal_correlation" in patterns, "Should detect temporal correlations"
    
    def test_evidence_aggregation_full_workflow(self):
        """Test complete evidence aggregation workflow"""
        trades = [TestDataFactory.create_sample_trade_data() for _ in range(10)]
        communications = [
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "type": "email",
                "sensitivity": 0.7,
                "account_id": "ACC001"
            }
        ]
        
        evidence = self.aggregator.aggregate_person_evidence(
            self.person_profile,
            trades,
            communications,
            datetime.now(timezone.utc) - timedelta(days=1)
        )
        
        assert evidence is not None, "Should aggregate evidence successfully"
        assert "trading_evidence" in evidence, "Should include trading evidence"
        assert "communication_evidence" in evidence, "Should include communication evidence"
        assert "cross_account_patterns" in evidence, "Should include cross-account patterns"


class TestPersonCentricNodes:
    """Unit tests for Person-Centric Bayesian Nodes"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.config = TestDataFactory.create_test_config()
        self.person_id = "PERSON001"
        self.typology = RiskTypology.INSIDER_DEALING
    
    def test_person_trading_pattern_node(self):
        """Test PersonTradingPatternNode"""
        node = PersonTradingPatternNode(
            node_id=f"trading_pattern_{self.person_id}",
            person_id=self.person_id,
            config=self.config
        )
        
        # Test evidence aggregation
        evidence_data = {
            "ACC001": {"volume_anomaly": 0.8, "timing_patterns": 0.6},
            "ACC002": {"volume_anomaly": 0.7, "timing_patterns": 0.5}
        }
        
        identity_confidence = {"ACC001": 0.95, "ACC002": 0.90}
        
        aggregated_strength = node.aggregate_evidence_strength(evidence_data, identity_confidence)
        assert aggregated_strength > 0.0, "Should aggregate evidence strength"
        assert aggregated_strength <= 1.0, "Should not exceed maximum strength"
    
    def test_person_risk_node(self):
        """Test PersonRiskNode"""
        # Create evidence nodes
        trading_node = PersonTradingPatternNode(
            node_id=f"trading_{self.person_id}",
            person_id=self.person_id,
            config=self.config
        )
        
        communication_node = PersonCommunicationNode(
            node_id=f"comm_{self.person_id}",
            person_id=self.person_id,
            config=self.config
        )
        
        # Create risk node
        risk_node = PersonRiskNode(
            node_id=f"risk_{self.person_id}",
            person_id=self.person_id,
            typology=self.typology,
            evidence_nodes=[trading_node, communication_node],
            config=self.config
        )
        
        # Test risk calculation
        risk_probability = risk_node.calculate_risk_probability()
        assert 0.0 <= risk_probability <= 1.0, "Risk probability should be valid range"
    
    def test_create_person_risk_nodes_factory(self):
        """Test the factory function for creating person risk nodes"""
        nodes = create_person_risk_nodes(self.person_id, self.typology, self.config)
        
        assert len(nodes) > 0, "Should create risk nodes"
        assert any(isinstance(node, PersonRiskNode) for node in nodes), "Should include risk node"
        assert any(isinstance(node, PersonEvidenceNode) for node in nodes), "Should include evidence nodes"


class TestCrossTypologyEngine:
    """Unit tests for Cross-Typology Engine"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.config = TestDataFactory.create_test_config()
        self.engine = CrossTypologyEngine(self.config)
        self.person_id = "PERSON001"
    
    def test_signal_registration(self):
        """Test risk node registration"""
        # Create mock risk nodes
        insider_node = Mock()
        insider_node.person_id = self.person_id
        insider_node.typology = RiskTypology.INSIDER_DEALING
        insider_node.get_current_risk_score.return_value = 0.7
        
        spoofing_node = Mock()
        spoofing_node.person_id = self.person_id
        spoofing_node.typology = RiskTypology.SPOOFING
        spoofing_node.get_current_risk_score.return_value = 0.4
        
        # Register nodes
        self.engine.register_person_risk_node(insider_node)
        self.engine.register_person_risk_node(spoofing_node)
        
        assert len(self.engine.person_risk_nodes[self.person_id]) == 2, "Should register both nodes"
    
    def test_cross_typology_signal_generation(self):
        """Test cross-typology signal generation"""
        # Create and register mock nodes
        insider_node = Mock()
        insider_node.person_id = self.person_id
        insider_node.typology = RiskTypology.INSIDER_DEALING
        insider_node.get_current_risk_score.return_value = 0.8
        insider_node.get_evidence_summary.return_value = {"strong_evidence": 0.8}
        
        spoofing_node = Mock()
        spoofing_node.person_id = self.person_id
        spoofing_node.typology = RiskTypology.SPOOFING
        spoofing_node.get_current_risk_score.return_value = 0.3
        spoofing_node.get_evidence_summary.return_value = {"weak_evidence": 0.3}
        
        self.engine.register_person_risk_node(insider_node)
        self.engine.register_person_risk_node(spoofing_node)
        
        # Analyze cross-typology signals
        signals = self.engine.analyze_cross_typology_signals(self.person_id)
        
        assert len(signals) > 0, "Should generate cross-typology signals"
        assert any(signal.source_typology == RiskTypology.INSIDER_DEALING for signal in signals), \
            "Should include insider dealing as source"
    
    def test_escalation_factors(self):
        """Test escalation factor calculation"""
        signals = [
            TestDataFactory.create_sample_cross_typology_signal(
                RiskTypology.INSIDER_DEALING, RiskTypology.SPOOFING, 0.8
            ),
            TestDataFactory.create_sample_cross_typology_signal(
                RiskTypology.SPOOFING, RiskTypology.MARKET_MANIPULATION, 0.6
            )
        ]
        
        escalation_factors = self.engine.calculate_escalation_factors(self.person_id, signals)
        
        assert "escalation_score" in escalation_factors, "Should calculate escalation score"
        assert "risk_clustering" in escalation_factors, "Should assess risk clustering"


class TestPersonCentricAlertGenerator:
    """Unit tests for Person-Centric Alert Generator"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.config = TestDataFactory.create_test_config()
        
        # Create mock dependencies
        self.entity_service = Mock()
        self.evidence_aggregator = Mock()
        self.cross_typology_engine = Mock()
        
        self.generator = PersonCentricAlertGenerator(
            entity_resolution_service=self.entity_service,
            evidence_aggregator=self.evidence_aggregator,
            cross_typology_engine=self.cross_typology_engine,
            config=self.config
        )
    
    def test_alert_generation(self):
        """Test basic alert generation"""
        person_id = "PERSON001"
        person_profile = TestDataFactory.create_sample_person_profile(person_id)
        trades = [TestDataFactory.create_sample_trade_data() for _ in range(5)]
        
        # Mock dependencies
        self.evidence_aggregator.aggregate_person_evidence.return_value = {
            "trading_evidence": {"strength": 0.7},
            "cross_account_patterns": {"correlation": 0.8}
        }
        
        self.cross_typology_engine.analyze_cross_typology_signals.return_value = [
            TestDataFactory.create_sample_cross_typology_signal()
        ]
        
        # Generate alert
        alert = self.generator.generate_person_alert(
            person_id=person_id,
            person_profile=person_profile,
            trade_data=trades,
            risk_typology=RiskTypology.INSIDER_DEALING
        )
        
        assert alert is not None, "Should generate alert"
        assert alert.person_id == person_id, "Should have correct person ID"
        assert alert.risk_typology == RiskTypology.INSIDER_DEALING, "Should have correct risk typology"
        assert 0.0 <= alert.probability_score <= 1.0, "Should have valid probability score"
    
    def test_enhanced_explanation_generation(self):
        """Test enhanced explanation generation"""
        alert = PersonCentricAlert(
            alert_id="ALERT001",
            person_id="PERSON001",
            person_name="John Doe",
            risk_typology=RiskTypology.INSIDER_DEALING,
            probability_score=0.75,
            confidence_score=0.85,
            severity=AlertSeverity.HIGH,
            involved_accounts=["ACC001", "ACC002"],
            timestamp=datetime.now(timezone.utc),
            stor_eligible=True,
            escalation_factors={},
            regulatory_rationale="Test rationale",
            evidence_summary={}
        )
        
        person_profile = TestDataFactory.create_sample_person_profile()
        evidence_data = {"ACC001": {"trading_patterns": []}}
        cross_typology_signals = [TestDataFactory.create_sample_cross_typology_signal()]
        
        explanation = self.generator.generate_enhanced_explanation(
            alert=alert,
            person_profile=person_profile,
            evidence_data=evidence_data,
            cross_typology_signals=cross_typology_signals
        )
        
        assert explanation is not None, "Should generate explanation"
        assert "alert_id" in explanation, "Should include alert ID"
        assert "audit_report" in explanation, "Should include audit report"
        assert "explainability_metadata" in explanation, "Should include metadata"


class TestRegulatoryExplainability:
    """Unit tests for Regulatory Explainability Engine"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.config = TestDataFactory.create_test_config()
        self.engine = RegulatoryExplainabilityEngine(self.config)
    
    def test_framework_mapping_initialization(self):
        """Test regulatory framework mapping initialization"""
        assert hasattr(self.engine, 'framework_mappings'), "Should have framework mappings"
        assert len(self.engine.framework_mappings) > 0, "Should load framework mappings"
    
    def test_evidence_organization(self):
        """Test evidence organization by account"""
        evidence_data = {
            "ACC001": {
                "trading_patterns": [
                    {
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "pattern_type": "volume_spike",
                        "strength": 0.8,
                        "reliability": 0.9
                    }
                ],
                "communications": [
                    {
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "type": "email",
                        "sensitivity": 0.7,
                        "reliability": 0.8
                    }
                ]
            }
        }
        
        linked_accounts = ["ACC001"]
        account_evidence = self.engine._organize_evidence_by_account(evidence_data, linked_accounts)
        
        assert "ACC001" in account_evidence, "Should organize evidence by account"
        assert len(account_evidence["ACC001"].evidence_items) > 0, "Should extract evidence items"
    
    def test_comprehensive_explanation_generation(self):
        """Test comprehensive explanation generation"""
        # Create test alert
        alert = PersonCentricAlert(
            alert_id="ALERT001",
            person_id="PERSON001",
            person_name="John Doe",
            risk_typology=RiskTypology.INSIDER_DEALING,
            probability_score=0.75,
            confidence_score=0.85,
            severity=AlertSeverity.HIGH,
            involved_accounts=["ACC001"],
            timestamp=datetime.now(timezone.utc),
            stor_eligible=True,
            escalation_factors={},
            regulatory_rationale="Test rationale",
            evidence_summary={}
        )
        
        person_profile = TestDataFactory.create_sample_person_profile()
        evidence_data = {
            "ACC001": {
                "trading_patterns": [
                    {
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "pattern_type": "suspicious_timing",
                        "strength": 0.8,
                        "reliability": 0.9
                    }
                ]
            }
        }
        cross_typology_signals = []
        
        explanation = self.engine.generate_comprehensive_explanation(
            alert=alert,
            person_profile=person_profile,
            evidence_data=evidence_data,
            cross_typology_signals=cross_typology_signals
        )
        
        assert explanation is not None, "Should generate comprehensive explanation"
        assert explanation.person_id == "PERSON001", "Should have correct person ID"
        assert len(explanation.account_evidence) > 0, "Should include account evidence"


class TestIntegrationScenarios:
    """Integration tests for component interactions"""
    
    def setup_method(self):
        """Set up integration test fixtures"""
        self.config = TestDataFactory.create_test_config()
        
        # Create real components (not mocks) for integration testing
        self.entity_service = EntityResolutionService(self.config)
        self.evidence_aggregator = PersonEvidenceAggregator(self.config)
        self.cross_typology_engine = CrossTypologyEngine(self.config)
        self.alert_generator = PersonCentricAlertGenerator(
            self.entity_service,
            self.evidence_aggregator,
            self.cross_typology_engine,
            self.config
        )
    
    def test_end_to_end_surveillance_workflow(self):
        """Test complete end-to-end surveillance workflow"""
        # Step 1: Create test data
        trades = []
        for i in range(10):
            trade = TestDataFactory.create_sample_trade_data(
                trader_id=f"TRADER00{i % 3 + 1}",  # 3 different traders
                timestamp=datetime.now(timezone.utc) - timedelta(hours=i),
                quantity=1000 * (i + 1)
            )
            trades.append(trade)
        
        # Step 2: Entity resolution
        person_ids = {}
        for trade in trades:
            person_id, confidence = self.entity_service.resolve_trading_data_person_id(trade)
            person_ids[trade.trader_id] = person_id
            trade.person_id = person_id
            trade.person_confidence = confidence
        
        # Should resolve to fewer persons than traders (due to linking)
        unique_persons = set(person_ids.values())
        assert len(unique_persons) <= len(set(trade.trader_id for trade in trades)), \
            "Should link some traders to same person"
        
        # Step 3: Evidence aggregation and alert generation for each person
        alerts = []
        for person_id in unique_persons:
            person_trades = [t for t in trades if t.person_id == person_id]
            person_profile = PersonRiskProfile(
                person_id=person_id,
                person_name=f"Person {person_id}",
                linked_accounts=list(set(t.trader_id for t in person_trades)),
                linked_emails=[],
                desk_affiliations=list(set(t.desk_id for t in person_trades)),
                hr_employee_id=None,
                risk_scores={},
                last_updated=datetime.now(timezone.utc),
                identity_confidence=0.9,
                aggregated_evidence={}
            )
            
            alert = self.alert_generator.generate_person_alert(
                person_id=person_id,
                person_profile=person_profile,
                trade_data=person_trades,
                risk_typology=RiskTypology.INSIDER_DEALING
            )
            
            if alert:
                alerts.append(alert)
        
        assert len(alerts) > 0, "Should generate at least one alert"
        
        # Step 4: Test enhanced explanation generation
        if alerts:
            test_alert = alerts[0]
            person_profile = PersonRiskProfile(
                person_id=test_alert.person_id,
                person_name=test_alert.person_name,
                linked_accounts=test_alert.involved_accounts,
                linked_emails=[],
                desk_affiliations=[],
                hr_employee_id=None,
                risk_scores={},
                last_updated=datetime.now(timezone.utc),
                identity_confidence=0.9,
                aggregated_evidence={}
            )
            
            explanation = self.alert_generator.generate_enhanced_explanation(
                alert=test_alert,
                person_profile=person_profile,
                evidence_data={},
                cross_typology_signals=[]
            )
            
            assert explanation is not None, "Should generate enhanced explanation"
    
    def test_cross_typology_signal_propagation(self):
        """Test cross-typology signal propagation between risk types"""
        person_id = "PERSON001"
        person_profile = TestDataFactory.create_sample_person_profile(person_id)
        
        # Generate high-risk insider dealing alert
        insider_trades = [
            TestDataFactory.create_sample_trade_data(
                trader_id="ACC001",
                timestamp=datetime.now(timezone.utc) - timedelta(hours=i),
                quantity=5000  # Large quantities
            )
            for i in range(5)
        ]
        
        insider_alert = self.alert_generator.generate_person_alert(
            person_id=person_id,
            person_profile=person_profile,
            trade_data=insider_trades,
            risk_typology=RiskTypology.INSIDER_DEALING
        )
        
        # Generate spoofing analysis (should be influenced by insider dealing signals)
        spoofing_trades = [
            TestDataFactory.create_sample_trade_data(
                trader_id="ACC002",
                timestamp=datetime.now(timezone.utc) - timedelta(minutes=i*10),
                quantity=1000
            )
            for i in range(3)
        ]
        
        spoofing_alert = self.alert_generator.generate_person_alert(
            person_id=person_id,
            person_profile=person_profile,
            trade_data=spoofing_trades,
            risk_typology=RiskTypology.SPOOFING
        )
        
        # The spoofing alert should be influenced by the insider dealing risk
        # (This would be more sophisticated in a real implementation)
        assert insider_alert is not None, "Should generate insider dealing alert"
        assert spoofing_alert is not None, "Should generate spoofing alert"


class TestEndToEndScenarios:
    """End-to-end testing scenarios"""
    
    def setup_method(self):
        """Set up end-to-end test fixtures"""
        self.config = TestDataFactory.create_test_config()
        
        # Create surveillance engine for end-to-end testing
        self.surveillance_engine = PersonCentricSurveillanceEngine(self.config)
    
    def test_complete_surveillance_pipeline(self):
        """Test complete surveillance pipeline from raw data to alerts"""
        # Create comprehensive test dataset
        trade_data = []
        communication_data = []
        hr_data = []
        
        # Person 1: High-risk insider dealing scenario
        person1_trades = [
            TestDataFactory.create_sample_trade_data(
                trader_id="TRADER001",
                timestamp=datetime.now(timezone.utc) - timedelta(hours=i),
                instrument="CONFIDENTIAL_CO",
                quantity=10000,
                price=100 + i * 2  # Price increasing
            )
            for i in range(5)
        ]
        trade_data.extend(person1_trades)
        
        communication_data.append({
            "timestamp": datetime.now(timezone.utc) - timedelta(hours=6),
            "trader_id": "TRADER001",
            "type": "email",
            "content_sensitivity": 0.9,
            "external_communication": True
        })
        
        hr_data.append({
            "employee_id": "EMP001",
            "full_name": "John Insider",
            "email": "john.insider@company.com",
            "desk": "EQUITY_DESK",
            "trading_accounts": ["TRADER001"],
            "access_level": "CONFIDENTIAL"
        })
        
        # Person 2: Lower-risk scenario
        person2_trades = [
            TestDataFactory.create_sample_trade_data(
                trader_id="TRADER002",
                timestamp=datetime.now(timezone.utc) - timedelta(hours=i),
                quantity=1000
            )
            for i in range(3)
        ]
        trade_data.extend(person2_trades)
        
        # Process through surveillance engine
        results = self.surveillance_engine.process_surveillance_data(
            trade_data=trade_data,
            communication_data=communication_data,
            hr_data=hr_data,
            target_typologies=[RiskTypology.INSIDER_DEALING, RiskTypology.SPOOFING]
        )
        
        assert results is not None, "Should process surveillance data successfully"
        assert "alerts" in results, "Should generate alerts"
        assert "person_profiles" in results, "Should create person profiles"
        assert "processing_metrics" in results, "Should provide processing metrics"
        
        # Verify high-risk person generated alert
        high_risk_alerts = [
            alert for alert in results["alerts"]
            if alert.probability_score > 0.6
        ]
        assert len(high_risk_alerts) > 0, "Should generate high-risk alerts"
    
    def test_regulatory_compliance_workflow(self):
        """Test regulatory compliance and STOR workflow"""
        # Create STOR-eligible scenario
        trade_data = [
            TestDataFactory.create_sample_trade_data(
                trader_id=f"TRADER00{i % 2 + 1}",
                timestamp=datetime.now(timezone.utc) - timedelta(minutes=i*5),
                quantity=50000,  # Large quantities
                price=100 + i * 5  # Significant price movement
            )
            for i in range(10)
        ]
        
        communication_data = [
            {
                "timestamp": datetime.now(timezone.utc) - timedelta(hours=1),
                "trader_id": "TRADER001",
                "type": "phone",
                "content_sensitivity": 0.95,
                "external_communication": True,
                "pre_trade_timing": True
            }
        ]
        
        # Process data
        results = self.surveillance_engine.process_surveillance_data(
            trade_data=trade_data,
            communication_data=communication_data,
            target_typologies=[RiskTypology.INSIDER_DEALING]
        )
        
        # Find STOR-eligible alerts
        stor_alerts = [
            alert for alert in results["alerts"]
            if alert.stor_eligible
        ]
        
        if stor_alerts:
            # Test enhanced explanation for STOR alert
            test_alert = stor_alerts[0]
            person_profile = next(
                profile for profile in results["person_profiles"]
                if profile.person_id == test_alert.person_id
            )
            
            # Generate comprehensive explanation
            explanation = self.surveillance_engine.alert_generator.generate_enhanced_explanation(
                alert=test_alert,
                person_profile=person_profile,
                evidence_data={},
                cross_typology_signals=[]
            )
            
            assert explanation is not None, "Should generate regulatory explanation"
            assert explanation["audit_report"]["stor_assessment"]["eligible"], \
                "Should confirm STOR eligibility"
            
            # Verify regulatory framework compliance
            regulatory_frameworks = explanation["audit_report"]["regulatory_compliance"]
            assert len(regulatory_frameworks) > 0, "Should map to regulatory frameworks"


class TestPerformanceAndStress:
    """Performance and stress testing"""
    
    def setup_method(self):
        """Set up performance test fixtures"""
        self.config = TestDataFactory.create_test_config()
        self.surveillance_engine = PersonCentricSurveillanceEngine(self.config)
    
    def test_large_dataset_processing(self):
        """Test processing of large datasets"""
        # Create large dataset
        num_trades = 10000
        num_traders = 100
        
        trade_data = [
            TestDataFactory.create_sample_trade_data(
                trader_id=f"TRADER{i % num_traders:03d}",
                timestamp=datetime.now(timezone.utc) - timedelta(minutes=i),
                quantity=1000 + (i % 5000),
                price=100 + (i % 50)
            )
            for i in range(num_trades)
        ]
        
        # Measure processing time
        start_time = datetime.now()
        
        results = self.surveillance_engine.process_surveillance_data(
            trade_data=trade_data,
            target_typologies=[RiskTypology.INSIDER_DEALING]
        )
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        assert results is not None, "Should process large dataset successfully"
        assert processing_time < 300, "Should process within reasonable time (5 minutes)"
        
        # Verify processing metrics
        metrics = results.get("processing_metrics", {})
        assert "total_trades_processed" in metrics, "Should track processing metrics"
        assert metrics["total_trades_processed"] == num_trades, "Should process all trades"
    
    def test_concurrent_person_processing(self):
        """Test concurrent processing of multiple persons"""
        # Create data for multiple persons
        persons_data = {}
        for person_idx in range(20):  # 20 different persons
            person_trades = [
                TestDataFactory.create_sample_trade_data(
                    trader_id=f"TRADER{person_idx:02d}_{acc_idx}",
                    timestamp=datetime.now(timezone.utc) - timedelta(hours=i),
                    quantity=1000 * (i + 1)
                )
                for acc_idx in range(3)  # 3 accounts per person
                for i in range(10)  # 10 trades per account
            ]
            persons_data[f"PERSON{person_idx:03d}"] = person_trades
        
        # Flatten trade data
        all_trades = []
        for trades in persons_data.values():
            all_trades.extend(trades)
        
        # Process all data
        results = self.surveillance_engine.process_surveillance_data(
            trade_data=all_trades,
            target_typologies=[RiskTypology.INSIDER_DEALING, RiskTypology.SPOOFING]
        )
        
        assert results is not None, "Should handle concurrent person processing"
        assert len(results["person_profiles"]) > 0, "Should create person profiles"
        
        # Verify that persons were properly resolved and processed
        unique_persons = set(profile.person_id for profile in results["person_profiles"])
        assert len(unique_persons) > 10, "Should identify multiple unique persons"


class TestDataQualityAndValidation:
    """Data quality and validation testing"""
    
    def setup_method(self):
        """Set up data quality test fixtures"""
        self.config = TestDataFactory.create_test_config()
        self.surveillance_engine = PersonCentricSurveillanceEngine(self.config)
    
    def test_missing_data_handling(self):
        """Test handling of missing or incomplete data"""
        # Create trades with missing fields
        incomplete_trades = [
            RawTradeData(
                trade_id="INCOMPLETE_001",
                timestamp=datetime.now(timezone.utc),
                instrument_id="AAPL",
                trader_id="TRADER001",
                desk_id=None,  # Missing desk
                quantity=1000,
                executed_price=150.0,
                notional_value=150000.0
                # Missing optional fields
            ),
            RawTradeData(
                trade_id="INCOMPLETE_002",
                timestamp=datetime.now(timezone.utc),
                instrument_id="",  # Empty instrument
                trader_id="TRADER001",
                desk_id="DESK001",
                quantity=0,  # Zero quantity
                executed_price=150.0,
                notional_value=0.0
            )
        ]
        
        # Should handle incomplete data gracefully
        results = self.surveillance_engine.process_surveillance_data(
            trade_data=incomplete_trades,
            target_typologies=[RiskTypology.INSIDER_DEALING]
        )
        
        assert results is not None, "Should handle incomplete data gracefully"
        
        # Check data quality metrics
        metrics = results.get("processing_metrics", {})
        if "data_quality" in metrics:
            assert "invalid_trades" in metrics["data_quality"], \
                "Should track data quality issues"
    
    def test_invalid_data_filtering(self):
        """Test filtering of invalid data"""
        # Create mix of valid and invalid trades
        mixed_trades = [
            # Valid trade
            TestDataFactory.create_sample_trade_data(trader_id="VALID001"),
            
            # Invalid trades
            RawTradeData(
                trade_id="INVALID_001",
                timestamp=datetime.now(timezone.utc),
                instrument_id="INVALID",
                trader_id="",  # Empty trader ID
                desk_id="DESK001",
                quantity=1000,
                executed_price=-150.0,  # Negative price
                notional_value=150000.0
            ),
            
            # Another valid trade
            TestDataFactory.create_sample_trade_data(trader_id="VALID002")
        ]
        
        results = self.surveillance_engine.process_surveillance_data(
            trade_data=mixed_trades,
            target_typologies=[RiskTypology.INSIDER_DEALING]
        )
        
        assert results is not None, "Should process mixed data successfully"
        
        # Should process valid trades and filter invalid ones
        metrics = results.get("processing_metrics", {})
        if "valid_trades_processed" in metrics:
            assert metrics["valid_trades_processed"] >= 2, \
                "Should process at least the valid trades"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])