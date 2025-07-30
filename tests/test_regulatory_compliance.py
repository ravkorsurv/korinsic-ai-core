"""
Regulatory Compliance Testing Suite

This module provides specialized testing for regulatory compliance scenarios
including STOR, MAR, MiFID II, and other regulatory framework requirements.

Test Categories:
- STOR (Suspicious Transaction and Order Reporting) compliance
- MAR (Market Abuse Regulation) compliance  
- MiFID II compliance
- Regulatory explainability requirements
- Audit trail validation
- Cross-jurisdictional compliance
"""

import pytest
import json
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any
from unittest.mock import Mock, patch

from src.core.person_centric_surveillance_engine import PersonCentricSurveillanceEngine
from src.core.regulatory_explainability import (
    RegulatoryExplainabilityEngine, RegulatoryFramework, EvidenceType
)
from src.models.person_centric import (
    PersonCentricAlert, RiskTypology, AlertSeverity
)
from src.models.trading_data import RawTradeData

from tests.test_person_centric_surveillance import TestDataFactory


class TestSTORCompliance:
    """Test STOR (Suspicious Transaction and Order Reporting) compliance"""
    
    def setup_method(self):
        """Set up STOR compliance test fixtures"""
        self.config = TestDataFactory.create_test_config()
        self.surveillance_engine = PersonCentricSurveillanceEngine(self.config)
        self.explainability_engine = RegulatoryExplainabilityEngine(self.config)
    
    def test_stor_eligibility_criteria(self):
        """Test STOR eligibility criteria assessment"""
        # Create high-risk scenario that should trigger STOR
        trade_data = [
            TestDataFactory.create_sample_trade_data(
                trader_id="TRADER001",
                timestamp=datetime.now(timezone.utc) - timedelta(minutes=i*5),
                instrument="HIGH_RISK_STOCK",
                quantity=100000,  # Large quantity
                price=50 + i * 2  # Price manipulation pattern
            )
            for i in range(8)
        ]
        
        communication_data = [
            {
                "timestamp": datetime.now(timezone.utc) - timedelta(hours=1),
                "trader_id": "TRADER001",
                "type": "phone",
                "content_sensitivity": 0.95,
                "external_communication": True,
                "pre_trade_timing": True,
                "suspicious_keywords": ["inside information", "confidential"]
            }
        ]
        
        # Process surveillance data
        results = self.surveillance_engine.process_surveillance_data(
            trade_data=trade_data,
            communication_data=communication_data,
            target_typologies=[RiskTypology.INSIDER_DEALING, RiskTypology.MARKET_MANIPULATION]
        )
        
        # Find STOR-eligible alerts
        stor_alerts = [alert for alert in results["alerts"] if alert.stor_eligible]
        
        assert len(stor_alerts) > 0, "Should generate STOR-eligible alerts for high-risk scenario"
        
        # Verify STOR criteria
        for alert in stor_alerts:
            assert alert.probability_score >= 0.6, "STOR alerts should meet probability threshold"
            assert alert.severity in [AlertSeverity.HIGH, AlertSeverity.CRITICAL], \
                "STOR alerts should be high severity"
    
    def test_stor_report_generation(self):
        """Test STOR report generation and formatting"""
        # Create test alert
        alert = PersonCentricAlert(
            alert_id="STOR_TEST_001",
            person_id="PERSON001",
            person_name="John Suspicious",
            risk_typology=RiskTypology.INSIDER_DEALING,
            probability_score=0.85,
            confidence_score=0.90,
            severity=AlertSeverity.HIGH,
            involved_accounts=["TRADER001", "TRADER002"],
            timestamp=datetime.now(timezone.utc),
            stor_eligible=True,
            escalation_factors={"cross_account_correlation": 0.8},
            regulatory_rationale="Suspicious trading patterns with inside information access",
            evidence_summary={"strong_evidence_count": 5}
        )
        
        person_profile = TestDataFactory.create_sample_person_profile(
            person_id="PERSON001",
            linked_accounts=["TRADER001", "TRADER002"],
            name="John Suspicious"
        )
        
        evidence_data = {
            "TRADER001": {
                "trading_patterns": [
                    {
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "pattern_type": "pre_announcement_trading",
                        "strength": 0.9,
                        "reliability": 0.95
                    }
                ],
                "communications": [
                    {
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "type": "email",
                        "sensitivity": 0.9,
                        "reliability": 0.85,
                        "external_contact": True
                    }
                ]
            }
        }
        
        # Generate enhanced explanation with STOR assessment
        explanation = self.surveillance_engine.alert_generator.generate_enhanced_explanation(
            alert=alert,
            person_profile=person_profile,
            evidence_data=evidence_data,
            cross_typology_signals=[]
        )
        
        # Verify STOR report structure
        assert explanation is not None, "Should generate explanation for STOR alert"
        audit_report = explanation["audit_report"]
        
        assert "stor_assessment" in audit_report, "Should include STOR assessment"
        stor_assessment = audit_report["stor_assessment"]
        
        # Verify required STOR fields
        required_stor_fields = [
            "eligible", "criteria_assessment", "confidence_level",
            "recommended_action", "supporting_evidence", "regulatory_rationale"
        ]
        
        for field in required_stor_fields:
            assert field in stor_assessment, f"STOR assessment should include {field}"
        
        assert stor_assessment["eligible"] == True, "Should confirm STOR eligibility"
        assert stor_assessment["confidence_level"] in ["High", "Medium"], \
            "Should provide confidence level"
    
    def test_stor_timeline_requirements(self):
        """Test STOR timeline and reporting requirements"""
        # Create time-sensitive scenario
        alert_time = datetime.now(timezone.utc)
        
        alert = PersonCentricAlert(
            alert_id="STOR_TIMELINE_001",
            person_id="PERSON001",
            person_name="Time Sensitive Trader",
            risk_typology=RiskTypology.MARKET_MANIPULATION,
            probability_score=0.75,
            confidence_score=0.85,
            severity=AlertSeverity.HIGH,
            involved_accounts=["TRADER001"],
            timestamp=alert_time,
            stor_eligible=True,
            escalation_factors={},
            regulatory_rationale="Time-sensitive market manipulation detected",
            evidence_summary={}
        )
        
        # Test STOR timeline calculation
        # STOR should be filed within specific timeframes based on jurisdiction
        
        # UK: Within 1 business day of detection
        uk_deadline = self._calculate_stor_deadline(alert_time, jurisdiction="UK")
        assert uk_deadline > alert_time, "UK STOR deadline should be after alert time"
        
        # EU: Within 1 business day of detection  
        eu_deadline = self._calculate_stor_deadline(alert_time, jurisdiction="EU")
        assert eu_deadline > alert_time, "EU STOR deadline should be after alert time"
        
        # Verify deadline calculation logic
        business_hours_until_deadline = self._calculate_business_hours(alert_time, uk_deadline)
        assert business_hours_until_deadline <= 24, "Should meet 1 business day requirement"
    
    def _calculate_stor_deadline(self, alert_time: datetime, jurisdiction: str) -> datetime:
        """Calculate STOR filing deadline based on jurisdiction"""
        # Simplified deadline calculation - in practice this would be more complex
        if jurisdiction in ["UK", "EU"]:
            # 1 business day from detection
            deadline = alert_time + timedelta(days=1)
            # Adjust for weekends
            if deadline.weekday() >= 5:  # Saturday or Sunday
                days_to_add = 7 - deadline.weekday() + 1  # Next Monday
                deadline = deadline + timedelta(days=days_to_add)
            return deadline
        else:
            return alert_time + timedelta(days=1)
    
    def _calculate_business_hours(self, start_time: datetime, end_time: datetime) -> float:
        """Calculate business hours between two timestamps"""
        # Simplified business hours calculation
        total_hours = (end_time - start_time).total_seconds() / 3600
        # Assume 8 business hours per day, 5 days per week
        business_days = total_hours / 24
        return business_days * 8


class TestMARCompliance:
    """Test MAR (Market Abuse Regulation) compliance"""
    
    def setup_method(self):
        """Set up MAR compliance test fixtures"""
        self.config = TestDataFactory.create_test_config()
        self.explainability_engine = RegulatoryExplainabilityEngine(self.config)
    
    def test_mar_article_8_insider_dealing(self):
        """Test MAR Article 8 (Insider Dealing) compliance"""
        # Create insider dealing scenario
        alert = PersonCentricAlert(
            alert_id="MAR_ART8_001",
            person_id="PERSON001",
            person_name="Insider Trader",
            risk_typology=RiskTypology.INSIDER_DEALING,
            probability_score=0.80,
            confidence_score=0.85,
            severity=AlertSeverity.HIGH,
            involved_accounts=["TRADER001"],
            timestamp=datetime.now(timezone.utc),
            stor_eligible=True,
            escalation_factors={},
            regulatory_rationale="Insider dealing detected with material information access",
            evidence_summary={}
        )
        
        person_profile = TestDataFactory.create_sample_person_profile()
        evidence_data = {
            "TRADER001": {
                "trading_patterns": [
                    {
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "pattern_type": "pre_announcement_trading",
                        "strength": 0.85,
                        "reliability": 0.90,
                        "material_information_correlation": True
                    }
                ],
                "access_privileges": [
                    {
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "access_type": "confidential_documents",
                        "strength": 0.95,
                        "reliability": 0.98
                    }
                ]
            }
        }
        
        # Generate comprehensive explanation
        explanation = self.explainability_engine.generate_comprehensive_explanation(
            alert=alert,
            person_profile=person_profile,
            evidence_data=evidence_data,
            cross_typology_signals=[]
        )
        
        # Verify MAR Article 8 compliance
        assert RegulatoryFramework.MAR_ARTICLE_8 in explanation.applicable_frameworks, \
            "Should map to MAR Article 8"
        
        mar_art8_analysis = explanation.applicable_frameworks[RegulatoryFramework.MAR_ARTICLE_8]
        
        # Verify MAR Article 8 requirements
        required_elements = [
            "relevance_score", "requirements_met", "evidence_quality", "compliance_assessment"
        ]
        
        for element in required_elements:
            assert element in mar_art8_analysis, f"Should include {element} for MAR Article 8"
        
        assert mar_art8_analysis["relevance_score"] > 0.7, \
            "Should have high relevance for insider dealing"
    
    def test_mar_article_12_market_manipulation(self):
        """Test MAR Article 12 (Market Manipulation) compliance"""
        # Create market manipulation scenario
        alert = PersonCentricAlert(
            alert_id="MAR_ART12_001",
            person_id="PERSON002",
            person_name="Market Manipulator",
            risk_typology=RiskTypology.MARKET_MANIPULATION,
            probability_score=0.75,
            confidence_score=0.80,
            severity=AlertSeverity.HIGH,
            involved_accounts=["TRADER002", "TRADER003"],
            timestamp=datetime.now(timezone.utc),
            stor_eligible=True,
            escalation_factors={"price_impact": 0.85},
            regulatory_rationale="Market manipulation through coordinated trading",
            evidence_summary={}
        )
        
        person_profile = TestDataFactory.create_sample_person_profile(
            person_id="PERSON002",
            linked_accounts=["TRADER002", "TRADER003"],
            name="Market Manipulator"
        )
        
        evidence_data = {
            "TRADER002": {
                "trading_patterns": [
                    {
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "pattern_type": "price_manipulation",
                        "strength": 0.80,
                        "reliability": 0.85,
                        "market_impact": 0.75
                    }
                ]
            },
            "TRADER003": {
                "trading_patterns": [
                    {
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "pattern_type": "coordinated_trading",
                        "strength": 0.75,
                        "reliability": 0.80,
                        "correlation_with_other_accounts": 0.90
                    }
                ]
            }
        }
        
        # Generate comprehensive explanation
        explanation = self.explainability_engine.generate_comprehensive_explanation(
            alert=alert,
            person_profile=person_profile,
            evidence_data=evidence_data,
            cross_typology_signals=[]
        )
        
        # Verify MAR Article 12 compliance
        assert RegulatoryFramework.MAR_ARTICLE_12 in explanation.applicable_frameworks, \
            "Should map to MAR Article 12"
        
        mar_art12_analysis = explanation.applicable_frameworks[RegulatoryFramework.MAR_ARTICLE_12]
        assert mar_art12_analysis["relevance_score"] > 0.6, \
            "Should have good relevance for market manipulation"


class TestMiFIDIICompliance:
    """Test MiFID II compliance requirements"""
    
    def setup_method(self):
        """Set up MiFID II compliance test fixtures"""
        self.config = TestDataFactory.create_test_config()
        self.explainability_engine = RegulatoryExplainabilityEngine(self.config)
    
    def test_mifid_ii_article_17_compliance(self):
        """Test MiFID II Article 17 (Investment Firm Obligations) compliance"""
        # Create scenario involving investment firm obligations
        alert = PersonCentricAlert(
            alert_id="MIFID_ART17_001",
            person_id="PERSON003",
            person_name="Investment Manager",
            risk_typology=RiskTypology.FRONT_RUNNING,
            probability_score=0.70,
            confidence_score=0.75,
            severity=AlertSeverity.MEDIUM,
            involved_accounts=["TRADER004"],
            timestamp=datetime.now(timezone.utc),
            stor_eligible=False,
            escalation_factors={},
            regulatory_rationale="Front running detected in client order execution",
            evidence_summary={}
        )
        
        person_profile = TestDataFactory.create_sample_person_profile(
            person_id="PERSON003",
            linked_accounts=["TRADER004"],
            name="Investment Manager"
        )
        
        evidence_data = {
            "TRADER004": {
                "trading_patterns": [
                    {
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "pattern_type": "front_running",
                        "strength": 0.70,
                        "reliability": 0.75,
                        "client_order_correlation": True
                    }
                ],
                "communications": [
                    {
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "type": "client_communication",
                        "sensitivity": 0.60,
                        "reliability": 0.70
                    }
                ]
            }
        }
        
        # Generate comprehensive explanation
        explanation = self.explainability_engine.generate_comprehensive_explanation(
            alert=alert,
            person_profile=person_profile,
            evidence_data=evidence_data,
            cross_typology_signals=[]
        )
        
        # Check if MiFID II Article 17 is applicable
        if RegulatoryFramework.MIFID_II_ARTICLE_17 in explanation.applicable_frameworks:
            mifid_analysis = explanation.applicable_frameworks[RegulatoryFramework.MIFID_II_ARTICLE_17]
            assert mifid_analysis["relevance_score"] > 0.5, \
                "Should have relevance for investment firm obligations"


class TestAuditTrailValidation:
    """Test audit trail and documentation requirements"""
    
    def setup_method(self):
        """Set up audit trail test fixtures"""
        self.config = TestDataFactory.create_test_config()
        self.explainability_engine = RegulatoryExplainabilityEngine(self.config)
    
    def test_complete_audit_trail_generation(self):
        """Test complete audit trail generation for regulatory compliance"""
        # Create comprehensive test scenario
        alert = PersonCentricAlert(
            alert_id="AUDIT_001",
            person_id="PERSON004",
            person_name="Audit Test Person",
            risk_typology=RiskTypology.INSIDER_DEALING,
            probability_score=0.85,
            confidence_score=0.90,
            severity=AlertSeverity.HIGH,
            involved_accounts=["TRADER005", "TRADER006"],
            timestamp=datetime.now(timezone.utc),
            stor_eligible=True,
            escalation_factors={"cross_account_correlation": 0.85},
            regulatory_rationale="Complex insider dealing with cross-account coordination",
            evidence_summary={"total_evidence_items": 12}
        )
        
        person_profile = TestDataFactory.create_sample_person_profile(
            person_id="PERSON004",
            linked_accounts=["TRADER005", "TRADER006"],
            name="Audit Test Person"
        )
        
        evidence_data = {
            "TRADER005": {
                "trading_patterns": [
                    {
                        "timestamp": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
                        "pattern_type": "unusual_volume",
                        "strength": 0.80,
                        "reliability": 0.85
                    },
                    {
                        "timestamp": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat(),
                        "pattern_type": "timing_anomaly",
                        "strength": 0.75,
                        "reliability": 0.80
                    }
                ],
                "communications": [
                    {
                        "timestamp": (datetime.now(timezone.utc) - timedelta(hours=3)).isoformat(),
                        "type": "email",
                        "sensitivity": 0.90,
                        "reliability": 0.85
                    }
                ]
            },
            "TRADER006": {
                "trading_patterns": [
                    {
                        "timestamp": (datetime.now(timezone.utc) - timedelta(hours=1, minutes=30)).isoformat(),
                        "pattern_type": "correlated_trading",
                        "strength": 0.85,
                        "reliability": 0.90
                    }
                ]
            }
        }
        
        # Generate comprehensive explanation with full audit trail
        explanation = self.explainability_engine.generate_comprehensive_explanation(
            alert=alert,
            person_profile=person_profile,
            evidence_data=evidence_data,
            cross_typology_signals=[]
        )
        
        # Verify audit trail completeness
        audit_report = explanation.to_audit_report()
        
        # Check required audit trail components
        required_audit_components = [
            "alert_metadata", "executive_summary", "detailed_analysis",
            "evidence_summary", "account_breakdown", "cross_account_analysis",
            "regulatory_compliance", "stor_assessment", "audit_trail"
        ]
        
        for component in required_audit_components:
            assert component in audit_report, f"Audit report should include {component}"
        
        # Verify evidence chain integrity
        audit_trail = audit_report["audit_trail"]
        
        assert "evidence_chain" in audit_trail, "Should include evidence chain"
        assert "decision_tree" in audit_trail, "Should include decision tree"
        assert "model_interpretability" in audit_trail, "Should include model interpretability"
        
        evidence_chain = audit_trail["evidence_chain"]
        assert len(evidence_chain) > 0, "Evidence chain should not be empty"
        
        # Verify evidence chain sequence and timestamps
        for i, evidence_item in enumerate(evidence_chain):
            assert "sequence_id" in evidence_item, f"Evidence item {i} should have sequence ID"
            assert "evidence_type" in evidence_item, f"Evidence item {i} should have type"
            
            if evidence_item["evidence_type"] == "account_level":
                assert "timestamp" in evidence_item, f"Account evidence {i} should have timestamp"
                assert "strength" in evidence_item, f"Account evidence {i} should have strength"
                assert "reliability" in evidence_item, f"Account evidence {i} should have reliability"
    
    def test_regulatory_documentation_standards(self):
        """Test adherence to regulatory documentation standards"""
        # Test different regulatory frameworks' documentation requirements
        frameworks_to_test = [
            RegulatoryFramework.MAR_ARTICLE_8,
            RegulatoryFramework.MAR_ARTICLE_12,
            RegulatoryFramework.STOR_REQUIREMENTS
        ]
        
        for framework in frameworks_to_test:
            # Get framework requirements from explainability engine
            framework_mapping = self.explainability_engine.framework_mappings.get(framework)
            
            if framework_mapping:
                assert "requirements" in framework_mapping, \
                    f"{framework.value} should have defined requirements"
                assert "evidence_thresholds" in framework_mapping, \
                    f"{framework.value} should have evidence thresholds"
                assert "documentation_standards" in framework_mapping, \
                    f"{framework.value} should have documentation standards"
                
                # Verify evidence thresholds are reasonable
                thresholds = framework_mapping["evidence_thresholds"]
                if "minimum_strength" in thresholds:
                    assert 0.0 <= thresholds["minimum_strength"] <= 1.0, \
                        f"{framework.value} minimum strength should be valid range"
                if "minimum_reliability" in thresholds:
                    assert 0.0 <= thresholds["minimum_reliability"] <= 1.0, \
                        f"{framework.value} minimum reliability should be valid range"


class TestCrossJurisdictionalCompliance:
    """Test compliance across different jurisdictions"""
    
    def setup_method(self):
        """Set up cross-jurisdictional test fixtures"""
        self.config = TestDataFactory.create_test_config()
        
        # Add jurisdiction-specific configuration
        self.config["jurisdictions"] = {
            "UK": {
                "regulatory_frameworks": ["MAR", "STOR", "FCA_MAR_GUIDANCE"],
                "stor_deadline_hours": 24,
                "language": "en-GB"
            },
            "EU": {
                "regulatory_frameworks": ["MAR", "MIFID_II", "ESMA_GUIDELINES"],
                "stor_deadline_hours": 24,
                "language": "en-EU"
            },
            "US": {
                "regulatory_frameworks": ["SEC_RULES", "FINRA"],
                "reporting_deadline_hours": 48,
                "language": "en-US"
            }
        }
        
        self.explainability_engine = RegulatoryExplainabilityEngine(self.config)
    
    def test_multi_jurisdiction_alert_handling(self):
        """Test handling of alerts that span multiple jurisdictions"""
        # Create alert involving multiple jurisdictions
        alert = PersonCentricAlert(
            alert_id="MULTI_JURIS_001",
            person_id="PERSON005",
            person_name="Global Trader",
            risk_typology=RiskTypology.MARKET_MANIPULATION,
            probability_score=0.80,
            confidence_score=0.85,
            severity=AlertSeverity.HIGH,
            involved_accounts=["UK_TRADER001", "EU_TRADER001"],
            timestamp=datetime.now(timezone.utc),
            stor_eligible=True,
            escalation_factors={"cross_jurisdiction": True},
            regulatory_rationale="Cross-border market manipulation detected",
            evidence_summary={}
        )
        
        person_profile = TestDataFactory.create_sample_person_profile(
            person_id="PERSON005",
            linked_accounts=["UK_TRADER001", "EU_TRADER001"],
            name="Global Trader"
        )
        
        evidence_data = {
            "UK_TRADER001": {
                "jurisdiction": "UK",
                "trading_patterns": [
                    {
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "pattern_type": "coordinated_manipulation",
                        "strength": 0.85,
                        "reliability": 0.90
                    }
                ]
            },
            "EU_TRADER001": {
                "jurisdiction": "EU",
                "trading_patterns": [
                    {
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "pattern_type": "coordinated_manipulation",
                        "strength": 0.80,
                        "reliability": 0.85
                    }
                ]
            }
        }
        
        # Generate explanation for multi-jurisdictional scenario
        explanation = self.explainability_engine.generate_comprehensive_explanation(
            alert=alert,
            person_profile=person_profile,
            evidence_data=evidence_data,
            cross_typology_signals=[]
        )
        
        # Verify cross-jurisdictional handling
        audit_report = explanation.to_audit_report()
        
        # Should identify multiple jurisdictions
        account_breakdown = audit_report["account_breakdown"]
        jurisdictions_involved = set()
        
        for account_id, account_info in account_breakdown.items():
            if account_id in evidence_data and "jurisdiction" in evidence_data[account_id]:
                jurisdictions_involved.add(evidence_data[account_id]["jurisdiction"])
        
        assert len(jurisdictions_involved) > 1, "Should detect multiple jurisdictions"
        
        # Should apply appropriate regulatory frameworks for each jurisdiction
        regulatory_compliance = audit_report["regulatory_compliance"]
        assert len(regulatory_compliance) > 0, "Should apply regulatory frameworks"
    
    def test_jurisdiction_specific_reporting_requirements(self):
        """Test jurisdiction-specific reporting requirements"""
        jurisdictions = ["UK", "EU", "US"]
        
        for jurisdiction in jurisdictions:
            if jurisdiction in self.config["jurisdictions"]:
                juris_config = self.config["jurisdictions"][jurisdiction]
                
                # Verify required configuration elements
                assert "regulatory_frameworks" in juris_config, \
                    f"{jurisdiction} should have regulatory frameworks defined"
                assert len(juris_config["regulatory_frameworks"]) > 0, \
                    f"{jurisdiction} should have at least one regulatory framework"
                
                # Verify timing requirements
                if "stor_deadline_hours" in juris_config:
                    assert juris_config["stor_deadline_hours"] > 0, \
                        f"{jurisdiction} STOR deadline should be positive"
                elif "reporting_deadline_hours" in juris_config:
                    assert juris_config["reporting_deadline_hours"] > 0, \
                        f"{jurisdiction} reporting deadline should be positive"


if __name__ == "__main__":
    # Run regulatory compliance tests
    pytest.main([__file__, "-v", "--tb=short"])