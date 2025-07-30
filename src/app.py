import logging
import os
import traceback
from datetime import datetime, timezone

from flask import Flask, jsonify, request
from flask_cors import CORS

from api.v1.routes.trading_data import trading_data_bp
from core.alert_generator import AlertGenerator
from core.bayesian_engine import BayesianEngine
from core.data_processor import DataProcessor
from core.risk_calculator import RiskCalculator
from core.trading_data_service import TradingDataService
from utils.config import Config
from utils.logger import setup_logger

# Initialize core components
config = Config()

# Initialize Flask app
app = Flask(__name__)

# Setup CORS with configuration
cors_origins = config.get_security_config().get(
    "cors_origins", ["http://localhost:3000"]
)
CORS(app, origins=cors_origins, allow_headers=["Content-Type", "Authorization"])

# Setup logging
logger = setup_logger()
bayesian_engine = BayesianEngine()
data_processor = DataProcessor()
alert_generator = AlertGenerator()
risk_calculator = RiskCalculator()
trading_data_service = TradingDataService()

# Register blueprints
app.register_blueprint(trading_data_bp, url_prefix="/api/v1")


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify(
        {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "service": "kor-ai-surveillance-platform",
        }
    )


@app.route("/api/v1/analyze", methods=["POST"])
def analyze_trading_data():
    """Main endpoint to analyze trading data for market abuse risks"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Process incoming trading data
        processed_data = data_processor.process(data)

        # Check for latent intent flag
        use_latent_intent = data.get("use_latent_intent", False)

        # Check for regulatory explainability flag
        include_regulatory_rationale = data.get("include_regulatory_rationale", False)

        # Calculate risk scores using Bayesian models
        if use_latent_intent:
            insider_dealing_score = bayesian_engine.analyze_insider_dealing(
                processed_data
            )
        else:
            insider_dealing_score = bayesian_engine.analyze_insider_dealing(
                processed_data
            )
        spoofing_score = bayesian_engine.analyze_spoofing(processed_data)

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
                    if alert["type"] == "INSIDER_DEALING":
                        risk_scores = insider_dealing_score
                    elif alert["type"] == "SPOOFING":
                        risk_scores = spoofing_score
                    else:
                        risk_scores = {"overall_score": overall_risk}

                    rationale = alert_generator.generate_regulatory_rationale(
                        alert, risk_scores, processed_data
                    )
                    regulatory_rationales.append(
                        {
                            "alert_id": alert["id"],
                            "deterministic_narrative": rationale.deterministic_narrative,
                            "inference_paths": [
                                {
                                    "evidence_node": path.evidence_node,
                                    "evidence_state": path.evidence_state,
                                    "evidence_weight": path.evidence_weight,
                                    "inference_rule": path.inference_rule,
                                    "conclusion_impact": path.conclusion_impact,
                                    "confidence_level": path.confidence_level,
                                }
                                for path in rationale.inference_paths
                            ],
                            "audit_trail": rationale.audit_trail,
                        }
                    )
                except Exception as e:
                    logger.error(
                        f"Error generating regulatory rationale for alert {alert['id']}: {str(e)}"
                    )

        response = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "analysis_id": f"analysis_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}",
            "risk_scores": {
                "insider_dealing": insider_dealing_score,
                "spoofing": spoofing_score,
                "overall_risk": overall_risk,
            },
            "alerts": alerts,
            "regulatory_rationales": (
                regulatory_rationales if include_regulatory_rationale else []
            ),
            "processed_data_summary": {
                "trades_analyzed": len(processed_data.get("trades", [])),
                "timeframe": processed_data.get("timeframe", "unknown"),
                "instruments": processed_data.get("instruments", []),
            },
        }

        logger.info(
            f"Analysis completed for {len(processed_data.get('trades', []))} trades"
        )
        return jsonify(response)

    except Exception as e:
        logger.error(f"Error in analyze_trading_data: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": "Internal server error", "details": str(e)}), 500


@app.route("/api/v1/models/info", methods=["GET"])
def get_models_info():
    """Get information about available Bayesian models"""
    try:
        models_info = bayesian_engine.get_model_info()
        return jsonify(models_info)
    except Exception as e:
        logger.error(f"Error getting models info: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@app.route("/api/v1/simulate", methods=["POST"])
def simulate_scenario():
    """Simulate a specific market abuse scenario for testing"""
    try:
        data = request.get_json()
        scenario_type = data.get("scenario_type")
        parameters = data.get("parameters", {})

        if scenario_type not in ["insider_dealing", "spoofing"]:
            return jsonify({"error": "Invalid scenario type"}), 400

        # Generate simulated data
        simulated_data = data_processor.generate_simulation_data(
            scenario_type, parameters
        )

        # Analyze simulated data
        if scenario_type == "insider_dealing":
            risk_score = bayesian_engine.analyze_insider_dealing(simulated_data)
        else:
            risk_score = bayesian_engine.analyze_spoofing(simulated_data)

        response = {
            "scenario_type": scenario_type,
            "parameters": parameters,
            "risk_score": risk_score,
            "simulated_data": simulated_data,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        return jsonify(response)

    except Exception as e:
        logger.error(f"Error in simulate_scenario: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@app.route("/api/v1/analyze/economic-withholding", methods=["POST"])
def analyze_economic_withholding():
    """
    Analyze power plant data for economic withholding using ARERA methodology.
    
    Expected request format:
    {
        "plant_data": {
            "unit_id": "PLANT_001",
            "fuel_type": "gas",
            "capacity_mw": 400.0,
            "heat_rate": 7200,
            "efficiency": 0.47,
            "variable_costs": {
                "fuel_cost_ratio": 0.85,
                "vom_cost": 3.2,
                "emission_cost": 1.1
            }
        },
        "offers": [
            {
                "timestamp": "2024-01-15T08:00:00Z",
                "price_eur_mwh": 52.5,
                "quantity_mw": 100.0,
                "product_block": "hour_09"
            }
        ],
        "market_data": {
            "system_load_mw": 25000,
            "load_factor": "normal_demand",
            "market_tightness": "balanced",
            "transmission_constraints": "unconstrained"
        },
        "fuel_prices": {
            "gas": 48.0
        },
        "use_latent_intent": false,
        "model_config": {}
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Validate required fields
        required_fields = ["plant_data", "offers", "market_data", "fuel_prices"]
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return jsonify({
                "error": f"Missing required fields: {', '.join(missing_fields)}"
            }), 400
        
        # Validate plant data
        plant_data = data.get("plant_data", {})
        required_plant_fields = ["unit_id", "fuel_type", "capacity_mw"]
        missing_plant_fields = [field for field in required_plant_fields if field not in plant_data]
        
        if missing_plant_fields:
            return jsonify({
                "error": f"Missing required plant data fields: {', '.join(missing_plant_fields)}"
            }), 400
        
        # Validate offers
        offers = data.get("offers", [])
        if not offers:
            return jsonify({"error": "At least one offer is required"}), 400
        
        # Validate offer structure
        required_offer_fields = ["price_eur_mwh", "quantity_mw"]
        for i, offer in enumerate(offers):
            missing_offer_fields = [field for field in required_offer_fields if field not in offer]
            if missing_offer_fields:
                return jsonify({
                    "error": f"Offer {i+1} missing required fields: {', '.join(missing_offer_fields)}"
                }), 400
        
        # Log analysis request
        logger.info(f"Economic withholding analysis requested for plant: {plant_data.get('unit_id')}")
        
        # Prepare data for analysis
        processed_data = {
            "plant_data": plant_data,
            "offers": offers,
            "market_data": data.get("market_data", {}),
            "fuel_prices": data.get("fuel_prices", {}),
            "use_latent_intent": data.get("use_latent_intent", False),
            "model_config": data.get("model_config", {})
        }
        
        # Perform economic withholding analysis using Bayesian engine
        analysis_results = bayesian_engine.calculate_economic_withholding_risk(processed_data)
        
        # Validate analysis results structure
        required_result_fields = ['risk_level', 'risk_score']
        missing_result_fields = []
        for field in required_result_fields:
            if field not in analysis_results:
                missing_result_fields.append(field)
        
        if missing_result_fields and "error" not in analysis_results:
            error_msg = f"Analysis results missing required fields: {', '.join(missing_result_fields)}"
            logger.error(error_msg)
            return jsonify({
                "error": "Invalid analysis results",
                "details": error_msg
            }), 500
        
        # Check for analysis errors
        if "error" in analysis_results:
            logger.error(f"Economic withholding analysis failed: {analysis_results['error']}")
            return jsonify({
                "error": "Analysis failed",
                "details": analysis_results["error"]
            }), 500
        
        # Extract key metrics for response
        risk_level = analysis_results.get("risk_level", "unknown")
        risk_score = analysis_results.get("risk_score", 0.0)
        compliance_report = analysis_results.get("compliance_report")
        
        # Process compliance report efficiently
        if compliance_report:
            if isinstance(compliance_report, dict):
                compliance_status = compliance_report.get('compliance_status', 'unknown')
                violations = compliance_report.get('violations', [])
            else:
                compliance_status = getattr(compliance_report, 'compliance_status', 'unknown')
                violations = getattr(compliance_report, 'violations', [])
            violations_count = len(violations)
        else:
            compliance_status = 'unknown'
            violations_count = 0
        
        # Generate alerts if high risk detected
        alerts = []
        if risk_level == "high" or risk_score > 0.8:
            alerts.append({
                "type": "ECONOMIC_WITHHOLDING",
                "severity": "high",
                "plant_id": plant_data.get("unit_id"),
                "risk_score": risk_score,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "description": f"High risk of economic withholding detected for plant {plant_data.get('unit_id')}"
            })
        elif risk_level == "medium" or risk_score > 0.6:
            alerts.append({
                "type": "ECONOMIC_WITHHOLDING",
                "severity": "medium", 
                "plant_id": plant_data.get("unit_id"),
                "risk_score": risk_score,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "description": f"Moderate risk of economic withholding detected for plant {plant_data.get('unit_id')}"
            })
        
        # Compile response
        response = {
            "analysis_type": "economic_withholding",
            "methodology": "arera_counterfactual_bayesian",
            "plant_id": plant_data.get("unit_id"),
            "risk_assessment": {
                "risk_level": risk_level,
                "risk_score": risk_score,
                "confidence": analysis_results.get("confidence", 0.0),
                "risk_probabilities": analysis_results.get("risk_probabilities", {})
            },
            "counterfactual_analysis": analysis_results.get("counterfactual_analysis", {}),
            "compliance_status": compliance_status,
            "violations_count": violations_count,
            "regulatory_rationale": analysis_results.get("regulatory_rationale", {}),
            "alerts": alerts,
            "evidence_sufficiency": analysis_results.get("evidence_sufficiency", {}),
            "analysis_metadata": analysis_results.get("analysis_metadata", {}),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Include full results if requested
        if data.get("include_full_results", False):
            response["full_analysis_results"] = analysis_results.get("full_analysis_results", {})
        
        logger.info(f"Economic withholding analysis completed for plant {plant_data.get('unit_id')} - Risk Level: {risk_level}")
        return jsonify(response)
        
    except ValueError as e:
        logger.error(
            f"Validation error in economic withholding analysis for plant {plant_data.get('unit_id', 'unknown')}: {str(e)}"
        )
        return jsonify({"error": f"Validation error: {str(e)}"}), 400
    except Exception as e:
        logger.error(
            f"Error in economic withholding analysis for plant {plant_data.get('unit_id', 'unknown')}: {str(e)}"
        )
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({"error": "Internal server error"}), 500


@app.route("/api/v1/alerts/history", methods=["GET"])
def get_alerts_history():
    """Get historical alerts"""
    try:
        limit = request.args.get("limit", 100, type=int)
        alert_type = request.args.get("type")

        alerts = alert_generator.get_historical_alerts(
            limit=limit, alert_type=alert_type
        )

        return jsonify(
            {
                "alerts": alerts,
                "count": len(alerts),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

    except Exception as e:
        logger.error(f"Error getting alerts history: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@app.route("/api/v1/export/stor/<alert_id>", methods=["POST"])
def export_stor_report(alert_id):
    """Export alert in STOR format"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data provided"}), 400

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
            if alert["id"] == alert_id:
                target_alert = alert
                break

        if not target_alert:
            return jsonify({"error": f"Alert {alert_id} not found"}), 404

        # Determine risk scores for the alert
        if target_alert["type"] == "INSIDER_DEALING":
            risk_scores = insider_dealing_score
        elif target_alert["type"] == "SPOOFING":
            risk_scores = spoofing_score
        else:
            risk_scores = {"overall_score": overall_risk}

        # Export STOR format
        stor_record = alert_generator.export_stor_report(
            target_alert, risk_scores, processed_data
        )

        return jsonify(
            {
                "stor_record": {
                    "record_id": stor_record.record_id,
                    "timestamp": stor_record.timestamp,
                    "entity_id": stor_record.entity_id,
                    "transaction_type": stor_record.transaction_type,
                    "risk_score": stor_record.risk_score,
                    "risk_level": stor_record.risk_level,
                    "narrative": stor_record.narrative,
                    "evidence_summary": stor_record.evidence_summary,
                    "regulatory_basis": stor_record.regulatory_basis,
                }
            }
        )

    except Exception as e:
        logger.error(f"Error exporting STOR report: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/v1/export/csv/<alert_id>", methods=["POST"])
def export_regulatory_csv(alert_id):
    """Export regulatory rationale as CSV"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data provided"}), 400

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
            if alert["id"] == alert_id:
                target_alert = alert
                break

        if not target_alert:
            return jsonify({"error": f"Alert {alert_id} not found"}), 404

        # Determine risk scores for the alert
        if target_alert["type"] == "INSIDER_DEALING":
            risk_scores = insider_dealing_score
        elif target_alert["type"] == "SPOOFING":
            risk_scores = spoofing_score
        else:
            risk_scores = {"overall_score": overall_risk}

        # Export CSV
        filename = alert_generator.export_regulatory_csv(
            target_alert, risk_scores, processed_data
        )

        return jsonify(
            {
                "csv_export": {
                    "filename": filename,
                    "message": f"Regulatory report exported to {filename}",
                }
            }
        )

    except Exception as e:
        logger.error(f"Error exporting regulatory CSV: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    server_config = config.get_server_config()

    port = server_config.get("port", 5000)
    host = server_config.get("host", "0.0.0.0")
    debug = server_config.get("debug", False)

    logger.info(
        f"Starting Korinsic Surveillance Platform on {host}:{port} (debug={debug})"
    )
    logger.info(f"Environment: {config.environment}")

    app.run(host=host, port=port, debug=debug)
