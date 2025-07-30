"""
Person-Centric Surveillance Engine

This is the main orchestration service that integrates all components of the
individual-centric surveillance system, transitioning from account-based 
alerts to person-based probabilistic detection across all risk typologies.

Features:
- Complete person-centric surveillance workflow
- Integration of all surveillance components
- Configurable processing pipeline
- Performance monitoring and optimization
- Comprehensive logging and error handling
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from src.models.person_centric import (
    PersonCentricAlert,
    PersonRiskProfile,
    RiskTypology,
    AlertSeverity
)
from src.models.trading_data import RawTradeData

from .entity_resolution import EntityResolutionService
from .person_evidence_aggregator import PersonEvidenceAggregator
from .cross_typology_engine import CrossTypologyEngine
from .person_centric_alert_generator import PersonCentricAlertGenerator

logger = logging.getLogger(__name__)


class PersonCentricSurveillanceEngine:
    """
    Main orchestration engine for individual-centric surveillance
    
    This engine coordinates all components to provide comprehensive person-level
    risk assessment and alert generation across multiple risk typologies.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the person-centric surveillance engine
        
        Args:
            config_path: Path to configuration file (optional)
        """
        # Load configuration
        self.config = self._load_configuration(config_path)
        
        # Initialize core services
        self.entity_resolution = EntityResolutionService()
        self.evidence_aggregator = PersonEvidenceAggregator(self.entity_resolution)
        self.cross_typology_engine = CrossTypologyEngine()
        self.alert_generator = PersonCentricAlertGenerator(
            self.entity_resolution,
            self.evidence_aggregator,
            self.cross_typology_engine
        )
        
        # Performance tracking
        self.performance_metrics = {
            "total_persons_processed": 0,
            "total_alerts_generated": 0,
            "average_processing_time": 0.0,
            "identity_resolution_accuracy": 0.0,
            "cross_typology_signals_generated": 0
        }
        
        # Processing state
        self.is_enabled = self.config.get("person_centric_surveillance", {}).get("enabled", True)
        self.processing_batch_size = self.config.get("person_centric_surveillance", {}).get(
            "performance_optimization", {}
        ).get("batch_processing", {}).get("max_persons_per_batch", 100)
        
        logger.info("Person-Centric Surveillance Engine initialized")
    
    def _load_configuration(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """Load configuration from file"""
        if config_path is None:
            config_path = "config/person_centric_surveillance.json"
        
        try:
            config_file = Path(config_path)
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config = json.load(f)
                logger.info(f"Loaded configuration from {config_path}")
                return config
            else:
                logger.warning(f"Configuration file not found: {config_path}, using defaults")
                return self._get_default_configuration()
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}, using defaults")
            return self._get_default_configuration()
    
    def _get_default_configuration(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "person_centric_surveillance": {
                "enabled": True,
                "alert_generation": {
                    "probability_thresholds": {
                        "minimum_alert": 0.4,
                        "stor_eligible": 0.75
                    }
                }
            }
        }
    
    def process_surveillance_data(
        self,
        trade_data: List[RawTradeData],
        communication_data: Optional[List[Dict[str, Any]]] = None,
        hr_data: Optional[List[Dict[str, Any]]] = None,
        news_events: Optional[List[Dict[str, Any]]] = None,
        target_typologies: Optional[List[RiskTypology]] = None
    ) -> Dict[str, Any]:
        """
        Process surveillance data for person-centric analysis
        
        Args:
            trade_data: Trading data from all accounts
            communication_data: Communication data from all channels
            hr_data: HR data for identity resolution
            news_events: News events for timing analysis
            target_typologies: Specific typologies to analyze (optional)
            
        Returns:
            Dictionary containing analysis results and generated alerts
        """
        if not self.is_enabled:
            logger.warning("Person-centric surveillance is disabled")
            return {"status": "disabled", "alerts": []}
        
        start_time = datetime.now()
        logger.info(f"Starting person-centric surveillance processing with {len(trade_data)} trades")
        
        try:
            # Step 1: Identity Resolution
            logger.info("Step 1: Performing identity resolution")
            person_identities = self._perform_identity_resolution(trade_data, communication_data, hr_data)
            
            # Step 2: Evidence Aggregation
            logger.info("Step 2: Aggregating evidence across persons")
            person_profiles = self._aggregate_person_evidence(
                person_identities, trade_data, communication_data
            )
            
            # Step 3: Cross-Typology Analysis
            logger.info("Step 3: Performing cross-typology analysis")
            cross_typology_results = self._perform_cross_typology_analysis(
                person_profiles, target_typologies or list(RiskTypology)
            )
            
            # Step 4: Alert Generation
            logger.info("Step 4: Generating person-centric alerts")
            alerts = self._generate_person_alerts(
                person_profiles, trade_data, communication_data, news_events, target_typologies
            )
            
            # Step 5: Performance Tracking
            processing_time = (datetime.now() - start_time).total_seconds()
            self._update_performance_metrics(len(person_identities), len(alerts), processing_time)
            
            # Prepare results
            results = {
                "status": "completed",
                "processing_time_seconds": processing_time,
                "persons_analyzed": len(person_identities),
                "alerts_generated": len(alerts),
                "alerts": [alert.to_dict() for alert in alerts],
                "cross_typology_summary": cross_typology_results,
                "performance_metrics": self.performance_metrics.copy(),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            logger.info(f"Person-centric surveillance completed: {len(alerts)} alerts generated for {len(person_identities)} persons in {processing_time:.2f}s")
            return results
            
        except Exception as e:
            logger.error(f"Error in person-centric surveillance processing: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    def _perform_identity_resolution(
        self,
        trade_data: List[RawTradeData],
        communication_data: Optional[List[Dict[str, Any]]],
        hr_data: Optional[List[Dict[str, Any]]]
    ) -> Dict[str, str]:
        """
        Perform identity resolution to map accounts to persons
        
        Returns:
            Dictionary mapping account_ids to person_ids
        """
        # Add HR data if available
        if hr_data:
            self.entity_resolution.add_hr_data(hr_data)
        
        # Resolve person IDs for trading data
        account_to_person = {}
        
        for trade in trade_data:
            if trade.trader_id not in account_to_person:
                person_id, confidence = self.entity_resolution.resolve_trading_data_person_id(
                    trade.__dict__
                )
                account_to_person[trade.trader_id] = person_id
                
                # Update trade data with person information
                trade.person_id = person_id
                trade.person_confidence = confidence
        
        # Resolve person IDs for communication data
        if communication_data:
            for comm in communication_data:
                person_id, confidence = self.entity_resolution.resolve_communication_person_id(comm)
                comm["person_id"] = person_id
                comm["person_confidence"] = confidence
        
        # Get unique persons
        unique_persons = set(account_to_person.values())
        logger.info(f"Identity resolution completed: {len(unique_persons)} unique persons identified from {len(account_to_person)} accounts")
        
        return account_to_person
    
    def _aggregate_person_evidence(
        self,
        person_identities: Dict[str, str],
        trade_data: List[RawTradeData],
        communication_data: Optional[List[Dict[str, Any]]]
    ) -> Dict[str, PersonRiskProfile]:
        """Aggregate evidence for each person"""
        
        person_profiles = {}
        unique_persons = set(person_identities.values())
        
        for person_id in unique_persons:
            # Get person's trade data
            person_trades = [trade for trade in trade_data if trade.person_id == person_id]
            
            # Get person's communication data
            person_comms = []
            if communication_data:
                person_comms = [comm for comm in communication_data if comm.get("person_id") == person_id]
            
            # Aggregate evidence
            person_profile = self.evidence_aggregator.aggregate_person_evidence(
                person_id, person_trades, person_comms
            )
            
            person_profiles[person_id] = person_profile
        
        logger.info(f"Evidence aggregation completed for {len(person_profiles)} persons")
        return person_profiles
    
    def _perform_cross_typology_analysis(
        self,
        person_profiles: Dict[str, PersonRiskProfile],
        target_typologies: List[RiskTypology]
    ) -> Dict[str, Any]:
        """Perform cross-typology analysis for all persons"""
        
        cross_typology_results = {}
        total_signals = 0
        
        for person_id in person_profiles.keys():
            # Analyze cross-typology signals for this person
            signals = self.cross_typology_engine.analyze_cross_typology_signals(person_id)
            total_signals += len(signals)
            
            # Get comprehensive summary
            summary = self.cross_typology_engine.get_person_cross_typology_summary(person_id)
            cross_typology_results[person_id] = summary
        
        # Cleanup expired signals
        self.cross_typology_engine.cleanup_expired_signals()
        
        logger.info(f"Cross-typology analysis completed: {total_signals} signals generated across {len(person_profiles)} persons")
        
        return {
            "total_signals_generated": total_signals,
            "persons_analyzed": len(person_profiles),
            "person_summaries": cross_typology_results
        }
    
    def _generate_person_alerts(
        self,
        person_profiles: Dict[str, PersonRiskProfile],
        trade_data: List[RawTradeData],
        communication_data: Optional[List[Dict[str, Any]]],
        news_events: Optional[List[Dict[str, Any]]],
        target_typologies: Optional[List[RiskTypology]]
    ) -> List[PersonCentricAlert]:
        """Generate person-centric alerts"""
        
        all_alerts = []
        typologies_to_analyze = target_typologies or list(RiskTypology)
        
        for person_id, person_profile in person_profiles.items():
            # Get person's data
            person_trades = [trade for trade in trade_data if trade.person_id == person_id]
            person_comms = []
            if communication_data:
                person_comms = [comm for comm in communication_data if comm.get("person_id") == person_id]
            
            # Generate alerts for each typology
            for typology in typologies_to_analyze:
                alert = self.alert_generator.generate_person_alert(
                    person_id=person_id,
                    risk_typology=typology,
                    person_profile=person_profile,
                    trade_data=person_trades,
                    communication_data=person_comms,
                    news_events=news_events
                )
                
                if alert:
                    all_alerts.append(alert)
        
        # Sort alerts by probability (highest first)
        all_alerts.sort(key=lambda x: x.probability_score, reverse=True)
        
        logger.info(f"Alert generation completed: {len(all_alerts)} alerts generated")
        return all_alerts
    
    def _update_performance_metrics(self, persons_count: int, alerts_count: int, processing_time: float):
        """Update performance metrics"""
        self.performance_metrics["total_persons_processed"] += persons_count
        self.performance_metrics["total_alerts_generated"] += alerts_count
        
        # Update average processing time
        current_avg = self.performance_metrics["average_processing_time"]
        total_processed = self.performance_metrics["total_persons_processed"]
        
        if total_processed > persons_count:  # Not first batch
            new_avg = ((current_avg * (total_processed - persons_count)) + processing_time) / total_processed
            self.performance_metrics["average_processing_time"] = new_avg
        else:
            self.performance_metrics["average_processing_time"] = processing_time
        
        # Update cross-typology signals
        active_signals = sum(
            len(signals) for signals in self.cross_typology_engine.active_signals.values()
        )
        self.performance_metrics["cross_typology_signals_generated"] = active_signals
    
    def analyze_single_person(
        self,
        person_id: str,
        trade_data: List[RawTradeData],
        communication_data: Optional[List[Dict[str, Any]]] = None,
        news_events: Optional[List[Dict[str, Any]]] = None,
        target_typologies: Optional[List[RiskTypology]] = None
    ) -> Dict[str, Any]:
        """
        Analyze a single person for all risk typologies
        
        Args:
            person_id: The person to analyze
            trade_data: Trading data for this person
            communication_data: Communication data for this person
            news_events: Relevant news events
            target_typologies: Specific typologies to analyze
            
        Returns:
            Comprehensive analysis results for the person
        """
        logger.info(f"Analyzing single person: {person_id}")
        
        try:
            # Get person profile
            person_profile = self.evidence_aggregator.aggregate_person_evidence(
                person_id, trade_data, communication_data
            )
            
            # Perform cross-typology analysis
            signals = self.cross_typology_engine.analyze_cross_typology_signals(person_id)
            cross_typology_summary = self.cross_typology_engine.get_person_cross_typology_summary(person_id)
            
            # Generate alerts for each typology
            alerts = []
            typologies_to_analyze = target_typologies or list(RiskTypology)
            
            for typology in typologies_to_analyze:
                alert = self.alert_generator.generate_person_alert(
                    person_id=person_id,
                    risk_typology=typology,
                    person_profile=person_profile,
                    trade_data=trade_data,
                    communication_data=communication_data,
                    news_events=news_events
                )
                
                if alert:
                    alerts.append(alert)
            
            return {
                "person_id": person_id,
                "person_profile": {
                    "primary_name": person_profile.primary_name,
                    "linked_accounts": list(person_profile.linked_accounts),
                    "linked_desks": list(person_profile.linked_desks),
                    "identity_confidence": person_profile.identity_confidence
                },
                "cross_typology_summary": cross_typology_summary,
                "alerts": [alert.to_dict() for alert in alerts],
                "analysis_timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing person {person_id}: {str(e)}")
            return {
                "person_id": person_id,
                "error": str(e),
                "analysis_timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        
        # Get entity resolution statistics
        all_persons = self.entity_resolution.get_all_persons()
        
        # Get alert statistics
        alert_stats = self.alert_generator.get_alert_statistics()
        
        # Get cross-typology correlation matrix
        correlation_matrix = self.cross_typology_engine.get_correlation_matrix()
        
        return {
            "system_enabled": self.is_enabled,
            "configuration_loaded": bool(self.config),
            "identity_resolution": {
                "total_persons": len(all_persons),
                "total_accounts_mapped": sum(len(p.linked_accounts) for p in all_persons.values()),
                "average_accounts_per_person": (
                    sum(len(p.linked_accounts) for p in all_persons.values()) / len(all_persons)
                    if all_persons else 0
                )
            },
            "cross_typology_engine": {
                "active_signals": len(self.cross_typology_engine.active_signals),
                "correlation_matrix": correlation_matrix
            },
            "alert_generation": alert_stats,
            "performance_metrics": self.performance_metrics,
            "system_timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def update_configuration(self, new_config: Dict[str, Any]):
        """Update system configuration"""
        self.config.update(new_config)
        
        # Update component configurations
        if "person_centric_surveillance" in new_config:
            pcs_config = new_config["person_centric_surveillance"]
            
            # Update enabled status
            self.is_enabled = pcs_config.get("enabled", self.is_enabled)
            
            # Update cross-typology correlations if provided
            if "cross_typology_engine" in pcs_config:
                cte_config = pcs_config["cross_typology_engine"]
                if "typology_correlations" in cte_config:
                    # Convert to the format expected by CrossTypologyEngine
                    correlations = {}
                    for source_name, targets in cte_config["typology_correlations"].items():
                        try:
                            source_typology = RiskTypology(source_name)
                            for target_name, correlation in targets.items():
                                target_typology = RiskTypology(target_name)
                                correlations[(source_typology, target_typology)] = correlation
                        except ValueError:
                            continue
                    
                    self.cross_typology_engine.update_typology_correlations(correlations)
        
        logger.info("Configuration updated successfully")
    
    def export_results(self, results: Dict[str, Any], output_path: str):
        """Export analysis results to file"""
        try:
            with open(output_path, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            logger.info(f"Results exported to {output_path}")
        except Exception as e:
            logger.error(f"Error exporting results: {str(e)}")
    
    def cleanup(self):
        """Cleanup resources and perform maintenance"""
        logger.info("Performing system cleanup")
        
        # Cleanup expired signals
        self.cross_typology_engine.cleanup_expired_signals()
        
        # Clear evidence caches
        self.evidence_aggregator.clear_evidence_cache()
        
        logger.info("System cleanup completed")


def create_surveillance_engine(config_path: Optional[str] = None) -> PersonCentricSurveillanceEngine:
    """
    Factory function to create a configured surveillance engine
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Configured PersonCentricSurveillanceEngine instance
    """
    return PersonCentricSurveillanceEngine(config_path)


# Example usage and demonstration
def demonstrate_person_centric_surveillance():
    """Demonstrate the person-centric surveillance system"""
    
    # Create surveillance engine
    engine = create_surveillance_engine()
    
    # Example trade data
    example_trades = [
        RawTradeData(
            trade_id="trade_001",
            execution_timestamp="2024-01-15T10:30:00Z",
            instrument="equity",
            instrument_type="stock",
            symbol="AAPL",
            exchange="NASDAQ",
            direction="buy",
            quantity=1000,
            executed_price=150.0,
            notional_value=150000,
            trader_id="account_001",
            trader_name="John Smith",
            trader_role="senior_trader",
            desk="equity_trading"
        ),
        RawTradeData(
            trade_id="trade_002",
            execution_timestamp="2024-01-15T10:35:00Z",
            instrument="equity",
            instrument_type="stock",
            symbol="AAPL",
            exchange="NASDAQ",
            direction="sell",
            quantity=500,
            executed_price=151.0,
            notional_value=75500,
            trader_id="account_002",
            trader_name="J. Smith",
            trader_role="trader",
            desk="equity_trading"
        )
    ]
    
    # Example communication data
    example_comms = [
        {
            "id": "comm_001",
            "timestamp": "2024-01-15T10:25:00Z",
            "sender_email": "john.smith@firm.com",
            "content": "AAPL earnings announcement coming soon",
            "channel": "email",
            "external": False
        }
    ]
    
    # Process surveillance data
    results = engine.process_surveillance_data(
        trade_data=example_trades,
        communication_data=example_comms,
        target_typologies=[RiskTypology.INSIDER_DEALING, RiskTypology.SPOOFING]
    )
    
    print("=== Person-Centric Surveillance Results ===")
    print(f"Status: {results['status']}")
    print(f"Persons Analyzed: {results['persons_analyzed']}")
    print(f"Alerts Generated: {results['alerts_generated']}")
    print(f"Processing Time: {results['processing_time_seconds']:.2f}s")
    
    if results['alerts']:
        print("\n=== Generated Alerts ===")
        for alert in results['alerts']:
            print(f"Alert ID: {alert['alert_id']}")
            print(f"Person: {alert['person_name']} ({alert['person_id']})")
            print(f"Risk Type: {alert['risk_typology']}")
            print(f"Severity: {alert['severity']}")
            print(f"Probability: {alert['probability_score']:.1%}")
            print(f"Accounts: {alert['account_count']}")
            print(f"STOR Eligible: {alert['stor_eligible']}")
            print(f"Explanation: {alert['explanation_summary']}")
            print("-" * 50)
    
    return results


if __name__ == "__main__":
    # Run demonstration
    demonstrate_person_centric_surveillance()