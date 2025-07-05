"""
Analysis Service for coordinating risk analysis operations.

This service coordinates the flow of data through the analysis pipeline,
managing data processing, risk calculation, and alert generation.
"""

import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from ..engines.bayesian_engine import BayesianEngine
from ..processors.data_processor import DataProcessor
from ..services.alert_service import AlertService
from ..engines.risk_calculator import RiskCalculator
from ...utils.logger import setup_logger

logger = setup_logger()


@dataclass
class AnalysisResult:
    """Result of risk analysis operation."""
    analysis_id: str
    timestamp: str
    processed_data: Dict[str, Any]
    risk_scores: Dict[str, Any]
    alerts: List[Dict[str, Any]]
    processing_time_ms: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


class AnalysisService:
    """
    Service for coordinating risk analysis operations.
    
    This service orchestrates the analysis pipeline:
    1. Data processing and validation
    2. Risk score calculation using Bayesian models
    3. Alert generation based on thresholds
    4. Result aggregation and formatting
    """
    
    def __init__(self):
        """Initialize the analysis service with required components."""
        self.bayesian_engine = BayesianEngine()
        self.data_processor = DataProcessor()
        self.alert_service = AlertService()
        self.risk_calculator = RiskCalculator()
        
    def analyze_trading_data(self, data: Dict[str, Any], 
                           use_latent_intent: bool = False) -> AnalysisResult:
        """
        Analyze trading data for market abuse risks.
        
        Args:
            data: Raw trading data to analyze
            use_latent_intent: Whether to use latent intent models
            
        Returns:
            AnalysisResult containing risk scores and alerts
        """
        start_time = time.time()
        
        try:
            # Generate analysis ID
            analysis_id = f"analysis_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            # Process incoming trading data
            processed_data = self.data_processor.process(data)
            
            # Calculate risk scores using Bayesian models
            if use_latent_intent:
                insider_dealing_score = self.bayesian_engine.calculate_insider_dealing_risk_with_latent_intent(processed_data)
            else:
                insider_dealing_score = self.bayesian_engine.calculate_insider_dealing_risk(processed_data)
                
            spoofing_score = self.bayesian_engine.calculate_spoofing_risk(processed_data)
            
            # Generate overall risk assessment
            overall_risk = self.risk_calculator.calculate_overall_risk(
                insider_dealing_score, spoofing_score, processed_data
            )
            
            # Aggregate risk scores
            risk_scores = {
                'insider_dealing': insider_dealing_score,
                'spoofing': spoofing_score,
                'overall_risk': overall_risk
            }
            
            # Generate alerts if thresholds exceeded
            alerts = self.alert_service.generate_alerts(
                processed_data, insider_dealing_score, spoofing_score, overall_risk
            )
            
            # Calculate processing time
            processing_time_ms = (time.time() - start_time) * 1000
            
            # Create result
            result = AnalysisResult(
                analysis_id=analysis_id,
                timestamp=datetime.utcnow().isoformat(),
                processed_data=processed_data,
                risk_scores=risk_scores,
                alerts=alerts,
                processing_time_ms=processing_time_ms,
                metadata={
                    'use_latent_intent': use_latent_intent,
                    'trades_analyzed': len(processed_data.get('trades', [])),
                    'timeframe': processed_data.get('timeframe', 'unknown'),
                    'instruments': processed_data.get('instruments', [])
                }
            )
            
            logger.info(f"Analysis {analysis_id} completed in {processing_time_ms:.2f}ms")
            return result
            
        except Exception as e:
            logger.error(f"Error in analyze_trading_data: {str(e)}")
            raise
    
    def analyze_batch_data(self, batch_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analyze multiple trading datasets in batch.
        
        Args:
            batch_data: List of trading datasets to analyze
            
        Returns:
            List of analysis results
        """
        results = []
        
        for i, data in enumerate(batch_data):
            try:
                # Analyze each dataset
                result = self.analyze_trading_data(data)
                
                # Convert to dictionary format for batch response
                batch_result = {
                    'batch_index': i,
                    'analysis_id': result.analysis_id,
                    'timestamp': result.timestamp,
                    'risk_scores': result.risk_scores,
                    'alerts': result.alerts,
                    'processing_time_ms': result.processing_time_ms,
                    'summary': {
                        'trades_analyzed': len(result.processed_data.get('trades', [])),
                        'alerts_generated': len(result.alerts)
                    }
                }
                
                results.append(batch_result)
                
            except Exception as e:
                logger.error(f"Error analyzing batch item {i}: {str(e)}")
                # Add error result to maintain batch integrity
                results.append({
                    'batch_index': i,
                    'error': str(e),
                    'timestamp': datetime.utcnow().isoformat()
                })
        
        return results
    
    def analyze_realtime_data(self, data: Dict[str, Any]) -> AnalysisResult:
        """
        Analyze trading data in real-time mode with optimizations.
        
        This method is optimized for low-latency processing by:
        - Using simplified data validation
        - Skipping non-essential calculations
        - Using cached model components
        
        Args:
            data: Trading data to analyze
            
        Returns:
            AnalysisResult with minimal processing overhead
        """
        start_time = time.time()
        
        try:
            # Generate analysis ID for real-time
            analysis_id = f"rt_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}"
            
            # Fast-track data processing for real-time
            processed_data = self.data_processor.process_realtime(data)
            
            # Calculate only essential risk scores
            insider_dealing_score = self.bayesian_engine.calculate_insider_dealing_risk(processed_data)
            spoofing_score = self.bayesian_engine.calculate_spoofing_risk(processed_data)
            
            # Skip overall risk calculation for speed
            risk_scores = {
                'insider_dealing': insider_dealing_score,
                'spoofing': spoofing_score
            }
            
            # Generate only high-priority alerts
            alerts = self.alert_service.generate_realtime_alerts(
                processed_data, insider_dealing_score, spoofing_score
            )
            
            # Calculate processing time
            processing_time_ms = (time.time() - start_time) * 1000
            
            # Create minimal result for real-time response
            result = AnalysisResult(
                analysis_id=analysis_id,
                timestamp=datetime.utcnow().isoformat(),
                processed_data=processed_data,
                risk_scores=risk_scores,
                alerts=alerts,
                processing_time_ms=processing_time_ms
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error in analyze_realtime_data: {str(e)}")
            raise
    
    def get_analysis_status(self, analysis_id: str) -> Dict[str, Any]:
        """
        Get the status of a specific analysis.
        
        Args:
            analysis_id: ID of the analysis to check
            
        Returns:
            Status information for the analysis
        """
        # This would typically query a database or cache
        # For now, return a placeholder implementation
        return {
            'analysis_id': analysis_id,
            'status': 'completed',
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def validate_analysis_request(self, data: Dict[str, Any]) -> bool:
        """
        Validate analysis request data.
        
        Args:
            data: Request data to validate
            
        Returns:
            True if valid, raises exception if invalid
        """
        required_fields = ['trades', 'trader_info']
        
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        
        if not isinstance(data['trades'], list) or len(data['trades']) == 0:
            raise ValueError("Trades must be a non-empty list")
        
        return True