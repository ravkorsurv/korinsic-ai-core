"""
Enhanced Analysis API routes with OpenInference tracing.

This module demonstrates how to integrate OpenInference observability
into the Korinsic surveillance platform's API endpoints.
"""

from flask import request, jsonify, Blueprint
from datetime import datetime
import logging
import uuid
from typing import Dict, Any

from ....core.engines.enhanced_bayesian_engine import EnhancedBayesianEngine
from ....core.services.analysis_service import AnalysisService
from ....core.services.regulatory_service import RegulatoryService
from ....utils.logger import setup_logger
from ....utils.openinference_tracer import get_tracer
from ..schemas.request_schemas import AnalysisRequestSchema
from ..schemas.response_schemas import AnalysisResponseSchema
from ..middleware.validation import validate_request
from ..middleware.error_handling import handle_api_errors

# Create blueprint for enhanced analysis routes
enhanced_analysis_bp = Blueprint('enhanced_analysis', __name__)

logger = setup_logger()

# Initialize services with OpenInference tracing
tracer = get_tracer()
enhanced_bayesian_engine = EnhancedBayesianEngine()
analysis_service = AnalysisService()
regulatory_service = RegulatoryService()


@enhanced_analysis_bp.route('/analyze/enhanced', methods=['POST'])
@handle_api_errors
@validate_request(AnalysisRequestSchema)
def analyze_trading_data_enhanced():
    """
    Enhanced analysis endpoint with comprehensive OpenInference tracing.
    
    This endpoint demonstrates:
    - Full request/response tracing
    - AI model inference tracking
    - Performance monitoring
    - Evidence sufficiency analysis
    - Regulatory compliance logging
    
    Returns:
        JSON response with detailed risk analysis and tracing metadata
    """
    analysis_id = str(uuid.uuid4())
    
    # Start the main analysis trace
    with tracer.tracer.start_as_current_span(
        "surveillance_analysis",
        kind=tracer.trace.SpanKind.SERVER
    ) as main_span:
        try:
            # Set main span attributes
            main_span.set_attribute("analysis.id", analysis_id)
            main_span.set_attribute("analysis.type", "market_abuse_detection")
            main_span.set_attribute("analysis.timestamp", datetime.utcnow().isoformat())
            
            # Get request data
            data = request.get_json()
            
            if not data:
                main_span.set_status(tracer.trace.Status(tracer.trace.StatusCode.ERROR, "No data provided"))
                return jsonify({'error': 'No data provided'}), 400
            
            # Log request characteristics
            _log_request_characteristics(main_span, data)
            
            # Extract request parameters
            use_latent_intent = data.get('use_latent_intent', False)
            include_regulatory_rationale = data.get('include_regulatory_rationale', False)
            
            # Data processing phase
            with tracer.tracer.start_as_current_span("data_processing") as processing_span:
                processing_span.set_attribute("processing.use_latent_intent", use_latent_intent)
                
                # Process the input data
                processed_data = _process_input_data(data)
                
                processing_span.set_attribute("processing.processed_trade_count", 
                                            len(processed_data.get("trades", [])))
                processing_span.set_attribute("processing.processed_order_count", 
                                            len(processed_data.get("orders", [])))
            
            # Risk analysis phase
            risk_analysis_results = {}
            
            # Insider dealing analysis
            if use_latent_intent:
                insider_result = enhanced_bayesian_engine.calculate_insider_dealing_risk_with_latent_intent(processed_data)
            else:
                insider_result = enhanced_bayesian_engine.calculate_insider_dealing_risk(processed_data)
            
            risk_analysis_results["insider_dealing"] = insider_result
            
            # Spoofing analysis
            spoofing_result = enhanced_bayesian_engine.calculate_spoofing_risk(processed_data)
            risk_analysis_results["spoofing"] = spoofing_result
            
            # Overall risk aggregation
            with tracer.tracer.start_as_current_span("risk_aggregation") as aggregation_span:
                overall_risk = _calculate_overall_risk(
                    insider_result.get("overall_score", 0),
                    spoofing_result.get("overall_score", 0),
                    processed_data
                )
                
                aggregation_span.set_attribute("risk.overall_score", overall_risk)
                aggregation_span.set_attribute("risk.insider_score", insider_result.get("overall_score", 0))
                aggregation_span.set_attribute("risk.spoofing_score", spoofing_result.get("overall_score", 0))
            
            # Alert generation
            alerts = []
            with tracer.tracer.start_as_current_span("alert_generation") as alert_span:
                if insider_result.get("overall_score", 0) > 0.7:
                    alerts.append({
                        "type": "INSIDER_DEALING",
                        "severity": "HIGH",
                        "score": insider_result.get("overall_score"),
                        "confidence": insider_result.get("confidence", "Medium")
                    })
                
                if spoofing_result.get("overall_score", 0) > 0.7:
                    alerts.append({
                        "type": "SPOOFING",
                        "severity": "HIGH", 
                        "score": spoofing_result.get("overall_score"),
                        "confidence": spoofing_result.get("confidence", "Medium")
                    })
                
                alert_span.set_attribute("alerts.count", len(alerts))
                if alerts:
                    alert_types = [alert["type"] for alert in alerts]
                    alert_span.set_attribute("alerts.types", ",".join(alert_types))
            
            # Regulatory rationale generation (if requested)
            regulatory_rationales = []
            if include_regulatory_rationale and alerts:
                with tracer.tracer.start_as_current_span("regulatory_rationale") as rationale_span:
                    for alert in alerts:
                        rationale = _generate_regulatory_rationale(alert, processed_data)
                        regulatory_rationales.append(rationale)
                    
                    rationale_span.set_attribute("rationale.count", len(regulatory_rationales))
            
            # Build enhanced response
            response = {
                "status": "success",
                "data": {
                    "analysis_id": analysis_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "risk_scores": {
                        "insider_dealing": insider_result,
                        "spoofing": spoofing_result,
                        "overall_risk": overall_risk
                    },
                    "alerts": alerts,
                    "regulatory_rationales": regulatory_rationales if include_regulatory_rationale else [],
                    "tracing_metadata": {
                        "session_id": enhanced_bayesian_engine.session_id,
                        "trace_id": format(main_span.get_span_context().trace_id, '032x'),
                        "span_id": format(main_span.get_span_context().span_id, '016x'),
                        "openinference_enabled": tracer.enabled
                    }
                }
            }
            
            # Log final results
            main_span.set_attribute("analysis.status", "completed")
            main_span.set_attribute("analysis.overall_risk", overall_risk)
            main_span.set_attribute("analysis.alert_count", len(alerts))
            
            logger.info(f"Enhanced analysis {analysis_id} completed successfully")
            return jsonify(response)
            
        except Exception as e:
            logger.error(f"Error in enhanced analysis {analysis_id}: {str(e)}")
            main_span.record_exception(e)
            main_span.set_status(tracer.trace.Status(tracer.trace.StatusCode.ERROR, str(e)))
            
            return jsonify({
                "status": "error",
                "error": str(e),
                "analysis_id": analysis_id
            }), 500


@enhanced_analysis_bp.route('/analyze/batch/enhanced', methods=['POST'])
@handle_api_errors
def analyze_batch_enhanced():
    """
    Enhanced batch analysis endpoint with distributed tracing.
    
    This endpoint processes multiple trading scenarios with:
    - Individual trace spans for each analysis
    - Batch-level performance metrics
    - Aggregated risk assessments
    - Comprehensive audit logging
    
    Returns:
        JSON response with batch analysis results and tracing metadata
    """
    batch_id = str(uuid.uuid4())
    
    with tracer.tracer.start_as_current_span(
        "surveillance_batch_analysis",
        kind=tracer.trace.SpanKind.SERVER
    ) as batch_span:
        try:
            batch_span.set_attribute("batch.id", batch_id)
            batch_span.set_attribute("batch.timestamp", datetime.utcnow().isoformat())
            
            data = request.get_json()
            batch_data = data.get('batch_data', [])
            
            if not batch_data:
                batch_span.set_status(tracer.trace.Status(tracer.trace.StatusCode.ERROR, "No batch data provided"))
                return jsonify({'error': 'No batch data provided'}), 400
            
            batch_span.set_attribute("batch.dataset_count", len(batch_data))
            
            results = []
            total_high_risk_alerts = 0
            
            # Process each dataset in the batch
            for i, dataset in enumerate(batch_data):
                with tracer.tracer.start_as_current_span(f"batch_item_{i}") as item_span:
                    item_span.set_attribute("batch.item.index", i)
                    item_span.set_attribute("batch.item.id", dataset.get("id", f"item_{i}"))
                    
                    # Process individual dataset
                    processed_data = _process_input_data(dataset)
                    
                    # Calculate risks
                    insider_result = enhanced_bayesian_engine.calculate_insider_dealing_risk(processed_data)
                    spoofing_result = enhanced_bayesian_engine.calculate_spoofing_risk(processed_data)
                    
                    overall_risk = _calculate_overall_risk(
                        insider_result.get("overall_score", 0),
                        spoofing_result.get("overall_score", 0),
                        processed_data
                    )
                    
                    # Count high-risk alerts
                    high_risk_count = 0
                    if insider_result.get("overall_score", 0) > 0.7:
                        high_risk_count += 1
                    if spoofing_result.get("overall_score", 0) > 0.7:
                        high_risk_count += 1
                    
                    total_high_risk_alerts += high_risk_count
                    
                    item_span.set_attribute("item.overall_risk", overall_risk)
                    item_span.set_attribute("item.high_risk_alerts", high_risk_count)
                    
                    results.append({
                        "dataset_id": dataset.get("id", f"item_{i}"),
                        "risk_scores": {
                            "insider_dealing": insider_result,
                            "spoofing": spoofing_result,
                            "overall_risk": overall_risk
                        }
                    })
            
            # Calculate batch-level metrics
            avg_risk = sum(result["risk_scores"]["overall_risk"] for result in results) / len(results)
            
            batch_span.set_attribute("batch.average_risk", avg_risk)
            batch_span.set_attribute("batch.total_high_risk_alerts", total_high_risk_alerts)
            batch_span.set_attribute("batch.status", "completed")
            
            response = {
                "status": "success",
                "data": {
                    "batch_id": batch_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "results": results,
                    "batch_metrics": {
                        "dataset_count": len(batch_data),
                        "average_risk": avg_risk,
                        "total_high_risk_alerts": total_high_risk_alerts
                    },
                    "tracing_metadata": {
                        "batch_trace_id": format(batch_span.get_span_context().trace_id, '032x'),
                        "openinference_enabled": tracer.enabled
                    }
                }
            }
            
            logger.info(f"Batch analysis {batch_id} completed: {len(results)} datasets processed")
            return jsonify(response)
            
        except Exception as e:
            logger.error(f"Error in batch analysis {batch_id}: {str(e)}")
            batch_span.record_exception(e)
            batch_span.set_status(tracer.trace.Status(tracer.trace.StatusCode.ERROR, str(e)))
            
            return jsonify({
                "status": "error",
                "error": str(e),
                "batch_id": batch_id
            }), 500


def _log_request_characteristics(span: Any, data: Dict[str, Any]):
    """Log request characteristics to the trace span."""
    try:
        span.set_attribute("request.has_trades", bool(data.get("trades")))
        span.set_attribute("request.has_orders", bool(data.get("orders")))
        span.set_attribute("request.has_material_events", bool(data.get("material_events")))
        span.set_attribute("request.use_latent_intent", data.get("use_latent_intent", False))
        span.set_attribute("request.include_regulatory_rationale", data.get("include_regulatory_rationale", False))
        
        if data.get("trades"):
            span.set_attribute("request.trade_count", len(data["trades"]))
        if data.get("orders"):
            span.set_attribute("request.order_count", len(data["orders"]))
            
    except Exception as e:
        logger.warning(f"Failed to log request characteristics: {e}")


def _process_input_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Process input data (placeholder for actual processing logic)."""
    # This would contain the actual data processing logic
    # For now, return the data as-is
    return data


def _calculate_overall_risk(insider_score: float, spoofing_score: float, processed_data: Dict[str, Any]) -> float:
    """Calculate overall risk score (placeholder for actual logic)."""
    # Simple weighted average - in reality this would be more sophisticated
    return (insider_score * 0.6) + (spoofing_score * 0.4)


def _generate_regulatory_rationale(alert: Dict[str, Any], processed_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate regulatory rationale (placeholder for actual logic)."""
    return {
        "alert_type": alert["type"],
        "rationale": f"Regulatory rationale for {alert['type']} alert",
        "applicable_regulations": ["MiFID II", "MAR"],
        "confidence": alert.get("confidence", "Medium")
    }
