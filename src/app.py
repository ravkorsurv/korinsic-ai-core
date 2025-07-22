import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from datetime import datetime, timezone
import traceback
from opentelemetry import trace

from core.bayesian_engine import BayesianEngine
from core.data_processor import DataProcessor
from core.alert_generator import AlertGenerator
from core.risk_calculator import RiskCalculator
from core.trading_data_service import TradingDataService
from utils.config import Config
from utils.logger import setup_logger
from utils.ai_observability import get_ai_observability
from api.v1.routes.trading_data import trading_data_bp

# Initialize core components
config = Config()

# Initialize Flask app
app = Flask(__name__)

# Setup CORS with configuration
cors_origins = config.get_security_config().get('cors_origins', ["http://localhost:3000"])
CORS(app, origins=cors_origins, allow_headers=["Content-Type", "Authorization"])

# Setup logging and AI observability
logger = setup_logger()
ai_observability = get_ai_observability()
bayesian_engine = BayesianEngine()
data_processor = DataProcessor()
alert_generator = AlertGenerator()
risk_calculator = RiskCalculator()
trading_data_service = TradingDataService()

# Register blueprints
app.register_blueprint(trading_data_bp, url_prefix='/api/v1')

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'service': 'kor-ai-surveillance-platform'
    })

@app.route('/api/v1/analyze', methods=['POST'])
def analyze_trading_data():
    """Main endpoint to analyze trading data for market abuse risks"""
    with ai_observability.tracer.start_as_current_span("market_abuse_analysis") as span:
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            # Extract trader info for tracing
            trader_id = data.get('trader_info', {}).get('trader_id', 'unknown')
            analysis_id = f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{trader_id}"
            
            # Set span attributes
            span.set_attribute("ai.request.trader_id", trader_id)
            span.set_attribute("ai.request.analysis_id", analysis_id)
            span.set_attribute("ai.request.data_size", len(str(data)))
            span.set_attribute("ai.analysis.timestamp", datetime.now().isoformat())
            span.set_attribute("ai.request.use_latent_intent", data.get('use_latent_intent', False))
            span.set_attribute("ai.request.include_regulatory_rationale", data.get('include_regulatory_rationale', False))
            
            # Process incoming trading data
            with ai_observability.tracer.start_as_current_span("data_processing") as data_span:
                processed_data = data_processor.process(data)
                data_span.set_attribute("ai.data.processed_fields", len(processed_data))
            
            # Check for latent intent flag
            use_latent_intent = data.get('use_latent_intent', False)
            
            # Check for regulatory explainability flag
            include_regulatory_rationale = data.get('include_regulatory_rationale', False)
            
            # Calculate risk scores using Bayesian models
            with ai_observability.tracer.start_as_current_span("risk_analysis") as risk_span:
                if use_latent_intent:
                    insider_dealing_score = bayesian_engine.analyze_insider_dealing(processed_data)
                else:
                    insider_dealing_score = bayesian_engine.analyze_insider_dealing(processed_data)
                spoofing_score = bayesian_engine.analyze_spoofing(processed_data)
                
                risk_span.set_attribute("ai.models.insider_dealing_score", insider_dealing_score.get('risk_score', 0.0))
                risk_span.set_attribute("ai.models.spoofing_score", spoofing_score.get('risk_score', 0.0))
            
            # Generate overall risk assessment
            with ai_observability.tracer.start_as_current_span("risk_aggregation") as agg_span:
                overall_risk = risk_calculator.calculate_overall_risk(
                    insider_dealing_score, spoofing_score, processed_data
                )
                agg_span.set_attribute("ai.risk.overall_score", overall_risk)
            
            # Generate alerts if thresholds exceeded
            with ai_observability.tracer.start_as_current_span("alert_generation") as alert_span:
                alerts = alert_generator.generate_alerts(
                    processed_data, insider_dealing_score, spoofing_score, overall_risk
                )
                alert_span.set_attribute("ai.alerts.count", len(alerts))
                if alerts:
                    alert_types = [alert.get('type', 'UNKNOWN') for alert in alerts]
                    alert_span.set_attribute("ai.alerts.types", alert_types)
        
        # Generate regulatory rationale if requested
        regulatory_rationales = []
        if include_regulatory_rationale and alerts:
            for alert in alerts:
                try:
                    # Determine which risk scores to use based on alert type
                    if alert['type'] == 'INSIDER_DEALING':
                        risk_scores = insider_dealing_score
                    elif alert['type'] == 'SPOOFING':
                        risk_scores = spoofing_score
                    else:
                        risk_scores = {'overall_score': overall_risk}
                    
                    rationale = alert_generator.generate_regulatory_rationale(
                        alert, risk_scores, processed_data
                    )
                    regulatory_rationales.append({
                        'alert_id': alert['id'],
                        'deterministic_narrative': rationale.deterministic_narrative,
                        'inference_paths': [
                            {
                                'evidence_node': path.evidence_node,
                                'evidence_state': path.evidence_state,
                                'evidence_weight': path.evidence_weight,
                                'inference_rule': path.inference_rule,
                                'conclusion_impact': path.conclusion_impact,
                                'confidence_level': path.confidence_level
                            }
                            for path in rationale.inference_paths
                        ],
                        'audit_trail': rationale.audit_trail
                    })
                except Exception as e:
                    logger.error(f"Error generating regulatory rationale for alert {alert['id']}: {str(e)}")
        
            response = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'analysis_id': analysis_id,
                'trace_id': format(span.get_span_context().trace_id, '032x'),  # Include trace ID for debugging
                'risk_scores': {
                    'insider_dealing': insider_dealing_score,
                    'spoofing': spoofing_score,
                    'overall_risk': overall_risk
                },
                'alerts': alerts,
                'regulatory_rationales': regulatory_rationales if include_regulatory_rationale else [],
                'processed_data_summary': {
                    'trades_analyzed': len(processed_data.get('trades', [])),
                    'timeframe': processed_data.get('timeframe', 'unknown'),
                    'instruments': processed_data.get('instruments', [])
                }
            }
            
            # Set final span attributes
            span.set_attribute("ai.response.final_risk_score", overall_risk)
            span.set_attribute("ai.response.alerts_generated", len(alerts))
            span.set_attribute("ai.response.trades_analyzed", len(processed_data.get('trades', [])))
            
            logger.info(f"Analysis completed for {len(processed_data.get('trades', []))} trades")
            return jsonify(response)
            
        except Exception as e:
            span.record_exception(e)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
            logger.error(f"Error in analyze_trading_data: {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

@app.route('/api/v1/models/info', methods=['GET'])
def get_models_info():
    """Get information about available Bayesian models"""
    try:
        models_info = bayesian_engine.get_model_info()
        return jsonify(models_info)
    except Exception as e:
        logger.error(f"Error getting models info: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/v1/simulate', methods=['POST'])
def simulate_scenario():
    """Simulate a specific market abuse scenario for testing"""
    try:
        data = request.get_json()
        scenario_type = data.get('scenario_type')
        parameters = data.get('parameters', {})
        
        if scenario_type not in ['insider_dealing', 'spoofing']:
            return jsonify({'error': 'Invalid scenario type'}), 400
        
        # Generate simulated data
        simulated_data = data_processor.generate_simulation_data(scenario_type, parameters)
        
        # Analyze simulated data
        if scenario_type == 'insider_dealing':
            risk_score = bayesian_engine.analyze_insider_dealing(simulated_data)
        else:
            risk_score = bayesian_engine.analyze_spoofing(simulated_data)
        
        response = {
            'scenario_type': scenario_type,
            'parameters': parameters,
            'risk_score': risk_score,
            'simulated_data': simulated_data,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error in simulate_scenario: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/v1/alerts/history', methods=['GET'])
def get_alerts_history():
    """Get historical alerts"""
    try:
        limit = request.args.get('limit', 100, type=int)
        alert_type = request.args.get('type')
        
        alerts = alert_generator.get_historical_alerts(limit=limit, alert_type=alert_type)
        
        return jsonify({
            'alerts': alerts,
            'count': len(alerts),
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting alerts history: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/v1/export/stor/<alert_id>', methods=['POST'])
def export_stor_report(alert_id):
    """Export alert in STOR format"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Process data and generate alert
        processed_data = data_processor.process(data)
        
        # Calculate risk scores
        insider_dealing_score = bayesian_engine.analyze_insider_dealing(processed_data)
        spoofing_score = bayesian_engine.analyze_spoofing(processed_data)
        overall_risk = risk_calculator.calculate_overall_risk(
            insider_dealing_score, spoofing_score, processed_data
        )
        
        # Generate alerts
        alerts = alert_generator.generate_alerts(
            processed_data, insider_dealing_score, spoofing_score, overall_risk
        )
        
        # Find the specific alert
        target_alert = None
        for alert in alerts:
            if alert['id'] == alert_id:
                target_alert = alert
                break
        
        if not target_alert:
            return jsonify({'error': f'Alert {alert_id} not found'}), 404
        
        # Determine risk scores for the alert
        if target_alert['type'] == 'INSIDER_DEALING':
            risk_scores = insider_dealing_score
        elif target_alert['type'] == 'SPOOFING':
            risk_scores = spoofing_score
        else:
            risk_scores = {'overall_score': overall_risk}
        
        # Export STOR format
        stor_record = alert_generator.export_stor_report(target_alert, risk_scores, processed_data)
        
        return jsonify({
            'stor_record': {
                'record_id': stor_record.record_id,
                'timestamp': stor_record.timestamp,
                'entity_id': stor_record.entity_id,
                'transaction_type': stor_record.transaction_type,
                'risk_score': stor_record.risk_score,
                'risk_level': stor_record.risk_level,
                'narrative': stor_record.narrative,
                'evidence_summary': stor_record.evidence_summary,
                'regulatory_basis': stor_record.regulatory_basis
            }
        })
        
    except Exception as e:
        logger.error(f"Error exporting STOR report: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/export/csv/<alert_id>', methods=['POST'])
def export_regulatory_csv(alert_id):
    """Export regulatory rationale as CSV"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Process data and generate alert
        processed_data = data_processor.process(data)
        
        # Calculate risk scores
        insider_dealing_score = bayesian_engine.analyze_insider_dealing(processed_data)
        spoofing_score = bayesian_engine.analyze_spoofing(processed_data)
        overall_risk = risk_calculator.calculate_overall_risk(
            insider_dealing_score, spoofing_score, processed_data
        )
        
        # Generate alerts
        alerts = alert_generator.generate_alerts(
            processed_data, insider_dealing_score, spoofing_score, overall_risk
        )
        
        # Find the specific alert
        target_alert = None
        for alert in alerts:
            if alert['id'] == alert_id:
                target_alert = alert
                break
        
        if not target_alert:
            return jsonify({'error': f'Alert {alert_id} not found'}), 404
        
        # Determine risk scores for the alert
        if target_alert['type'] == 'INSIDER_DEALING':
            risk_scores = insider_dealing_score
        elif target_alert['type'] == 'SPOOFING':
            risk_scores = spoofing_score
        else:
            risk_scores = {'overall_score': overall_risk}
        
        # Export CSV
        filename = alert_generator.export_regulatory_csv(target_alert, risk_scores, processed_data)
        
        return jsonify({
            'csv_export': {
                'filename': filename,
                'message': f'Regulatory report exported to {filename}'
            }
        })
        
    except Exception as e:
        logger.error(f"Error exporting regulatory CSV: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    server_config = config.get_server_config()
    
    port = server_config.get('port', 5000)
    host = server_config.get('host', '0.0.0.0')
    debug = server_config.get('debug', False)
    
    logger.info(f"Starting Korinsic Surveillance Platform on {host}:{port} (debug={debug})")
    logger.info(f"Environment: {config.environment}")
    
    app.run(host=host, port=port, debug=debug)