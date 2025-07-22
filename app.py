#!/usr/bin/env python3
"""
KOR AI Surveillance Platform - Main Application
Deployed on AWS Amplify
"""

import os
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from datetime import datetime
import traceback

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.bayesian_engine import BayesianEngine
from src.core.data_processor import DataProcessor
from src.core.alert_generator import AlertGenerator
from src.core.risk_calculator import RiskCalculator
from src.utils.config import Config
from src.utils.logger import setup_logger

# Initialize Flask app
app = Flask(__name__)
CORS(app, origins="*", allow_headers=["Content-Type", "Authorization"])

# Setup logging
logger = setup_logger()

# Initialize core components
config = Config()
bayesian_engine = BayesianEngine()
data_processor = DataProcessor()
alert_generator = AlertGenerator()
risk_calculator = RiskCalculator()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'kor-ai-surveillance-platform',
        'environment': config.get('environment'),
        'version': '1.0.0'
    })

@app.route('/api/v1/analyze', methods=['POST'])
def analyze_trading_data():
    """Main endpoint to analyze trading data for market abuse risks"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Process incoming trading data
        processed_data = data_processor.process(data)
        
        # Check for latent intent flag
        use_latent_intent = data.get('use_latent_intent', False)
        
        # Check for regulatory explainability flag
        include_regulatory_rationale = data.get('include_regulatory_rationale', False)
        
        # Calculate risk scores using Bayesian models
        if use_latent_intent:
            insider_dealing_score = bayesian_engine.calculate_insider_dealing_risk_with_latent_intent(processed_data)
        else:
            insider_dealing_score = bayesian_engine.calculate_insider_dealing_risk(processed_data)
        spoofing_score = bayesian_engine.calculate_spoofing_risk(processed_data)
        
        # Generate overall risk assessment
        overall_risk = risk_calculator.calculate_overall_risk(
            insider_dealing_score, spoofing_score, processed_data
        )
        
        # Generate alerts if thresholds exceeded
        alerts = alert_generator.generate_alerts(
            processed_data, insider_dealing_score, spoofing_score, overall_risk
        )
        
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
                                'node_name': path.node_name,
                                'evidence_value': path.evidence_value,
                                'probability': path.probability,
                                'contribution': path.contribution,
                                'rationale': path.rationale,
                                'confidence': path.confidence,
                                'regulatory_relevance': path.regulatory_relevance
                            }
                            for path in rationale.inference_paths
                        ],
                        'voi_analysis': rationale.voi_analysis,
                        'sensitivity_report': rationale.sensitivity_report,
                        'regulatory_frameworks': rationale.regulatory_frameworks,
                        'audit_trail': rationale.audit_trail
                    })
                except Exception as e:
                    logger.error(f"Error generating regulatory rationale for alert {alert['id']}: {str(e)}")
        
        response = {
            'timestamp': datetime.utcnow().isoformat(),
            'analysis_id': f"analysis_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
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
        
        logger.info(f"Analysis completed for {len(processed_data.get('trades', []))} trades")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error in analyze_trading_data: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

@app.route('/api/v1/models/info', methods=['GET'])
def get_models_info():
    """Get information about available Bayesian models"""
    try:
        models_info = bayesian_engine.get_models_info()
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
            risk_score = bayesian_engine.calculate_insider_dealing_risk(simulated_data)
        else:
            risk_score = bayesian_engine.calculate_spoofing_risk(simulated_data)
        
        response = {
            'scenario_type': scenario_type,
            'parameters': parameters,
            'risk_score': risk_score,
            'simulated_data': simulated_data,
            'timestamp': datetime.utcnow().isoformat()
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
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting alerts history: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/v1/export/stor/<alert_id>', methods=['POST'])
def export_regulatory_stor(alert_id):
    """Export regulatory STOR record for an alert"""
    try:
        data = request.get_json() or {}
        
        stor_record = alert_generator.generate_stor_record(alert_id, data)
        
        return jsonify({
            'alert_id': alert_id,
            'stor_record': stor_record,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error exporting STOR record for alert {alert_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/v1/export/csv/<alert_id>', methods=['POST'])
def export_regulatory_csv(alert_id):
    """Export regulatory CSV report for an alert"""
    try:
        data = request.get_json() or {}
        
        csv_data = alert_generator.generate_csv_report(alert_id, data)
        
        return jsonify({
            'alert_id': alert_id,
            'csv_data': csv_data,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error exporting CSV report for alert {alert_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/v1/config', methods=['GET'])
def get_config():
    """Get current configuration (non-sensitive)"""
    try:
        return jsonify({
            'environment': config.get('environment'),
            'risk_thresholds': config.get('risk_thresholds'),
            'models': config.get('models'),
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Error getting config: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # For local development
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False) 