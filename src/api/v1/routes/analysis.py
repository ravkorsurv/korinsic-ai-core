"""
Analysis API routes for risk assessment.

This module contains endpoints for analyzing trading data and calculating
market abuse risk scores using Bayesian inference models.
"""

from flask import request, jsonify
from datetime import datetime
import logging

from ....core.services.analysis_service import AnalysisService
from ....core.services.regulatory_service import RegulatoryService
from ....utils.logger import setup_logger
from ..schemas.request_schemas import AnalysisRequestSchema
from ..schemas.response_schemas import AnalysisResponseSchema
from ..middleware.validation import validate_request
from ..middleware.error_handling import handle_api_errors
from .. import api_v1

logger = setup_logger()

# Initialize services
analysis_service = AnalysisService()
regulatory_service = RegulatoryService()


@api_v1.route('/analyze', methods=['POST'])
@handle_api_errors
@validate_request(AnalysisRequestSchema)
def analyze_trading_data():
    """
    Analyze trading data for market abuse risks.
    
    This endpoint processes trading data through Bayesian inference models
    to detect potential insider dealing and spoofing activities.
    
    Returns:
        JSON response with risk scores, alerts, and optional regulatory rationale
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Extract request parameters
        use_latent_intent = data.get('use_latent_intent', False)
        include_regulatory_rationale = data.get('include_regulatory_rationale', False)
        
        # Perform risk analysis
        analysis_result = analysis_service.analyze_trading_data(
            data, 
            use_latent_intent=use_latent_intent
        )
        
        # Generate regulatory rationale if requested
        regulatory_rationales = []
        if include_regulatory_rationale and analysis_result.alerts:
            regulatory_rationales = regulatory_service.generate_rationales(
                analysis_result.alerts,
                analysis_result.risk_scores,
                analysis_result.processed_data
            )
        
        # Build response
        response = AnalysisResponseSchema().build_response(
            analysis_result=analysis_result,
            regulatory_rationales=regulatory_rationales,
            include_rationale=include_regulatory_rationale
        )
        
        logger.info(f"Analysis completed for {len(analysis_result.processed_data.get('trades', []))} trades")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error in analyze_trading_data: {str(e)}")
        raise


@api_v1.route('/analyze/batch', methods=['POST'])
@handle_api_errors
@validate_request(AnalysisRequestSchema)
def analyze_batch_data():
    """
    Analyze multiple trading datasets in batch.
    
    This endpoint allows for efficient processing of multiple trading
    scenarios in a single request.
    
    Returns:
        JSON response with batch analysis results
    """
    try:
        data = request.get_json()
        batch_data = data.get('batch_data', [])
        
        if not batch_data:
            return jsonify({'error': 'No batch data provided'}), 400
        
        # Process batch analysis
        batch_results = analysis_service.analyze_batch_data(batch_data)
        
        response = {
            'timestamp': datetime.utcnow().isoformat(),
            'batch_id': f"batch_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            'results': batch_results,
            'summary': {
                'total_analyses': len(batch_results),
                'total_alerts': sum(len(result.get('alerts', [])) for result in batch_results)
            }
        }
        
        logger.info(f"Batch analysis completed for {len(batch_data)} datasets")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error in analyze_batch_data: {str(e)}")
        raise


@api_v1.route('/analyze/realtime', methods=['POST'])
@handle_api_errors
@validate_request(AnalysisRequestSchema)
def analyze_realtime_data():
    """
    Analyze trading data in real-time mode.
    
    This endpoint is optimized for low-latency analysis of streaming
    trading data with minimal processing overhead.
    
    Returns:
        JSON response with real-time risk assessment
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Perform real-time analysis with optimizations
        analysis_result = analysis_service.analyze_realtime_data(data)
        
        # Build minimal response for real-time processing
        response = {
            'timestamp': datetime.utcnow().isoformat(),
            'analysis_id': f"rt_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            'risk_scores': analysis_result.risk_scores,
            'alerts': analysis_result.alerts,
            'processing_time_ms': analysis_result.processing_time_ms
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error in analyze_realtime_data: {str(e)}")
        raise