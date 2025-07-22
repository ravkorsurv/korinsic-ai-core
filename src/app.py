import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from datetime import datetime
import traceback

from core.bayesian_engine import BayesianEngine
from core.data_processor import DataProcessor
from core.alert_generator import AlertGenerator
from core.risk_calculator import RiskCalculator
from core.trading_data_service import TradingDataService
from utils.config import Config
from utils.logger import setup_logger
from openinference.instrumentation import instrument_app
from api.v1.routes.trading_data import trading_data_bp

# Initialize core components
config = Config()
instrument_app()

# Initialize Flask app
app = Flask(__name__)

# Setup CORS with configuration
cors_origins = config.get_security_config().get('cors_origins', ["http://localhost:3000"])
CORS(app, origins=cors_origins, allow_headers=["Content-Type", "Authorization"])

# Setup logging
logger = setup_logger()

# Initialize core components
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
        'service': 'kor-ai-surveillance-platform'
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
        
        # Calculate risk scores using Bayesian models
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
        
        response = {
            'timestamp': datetime.utcnow().isoformat(),
            'analysis_id': f"analysis_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            'risk_scores': {
                'insider_dealing': insider_dealing_score,
                'spoofing': spoofing_score,
                'overall_risk': overall_risk
            },
            'alerts': alerts,
            'processed_data_summary': {
                'trades_analyzed': len(processed_data.get('trades', [])),
                'timeframe': processed_data.get('timeframe'),
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

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting Kor.ai Surveillance Platform on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)