"""
Trading Data API Routes

This module provides API endpoints for accessing comprehensive raw trading data
for analyst investigations of market abuse alerts.
"""

import csv
import io
import json
import logging
from datetime import datetime

from flask import Blueprint, jsonify, request, send_file

from core.alert_generator import AlertGenerator
from core.bayesian_engine import BayesianEngine
from core.data_processor import DataProcessor
from core.risk_calculator import RiskCalculator
from core.trading_data_service import TradingDataService

logger = logging.getLogger(__name__)

# Create blueprint
trading_data_bp = Blueprint("trading_data", __name__)

# Initialize services
trading_data_service = TradingDataService()
data_processor = DataProcessor()
alert_generator = AlertGenerator()
bayesian_engine = BayesianEngine()
risk_calculator = RiskCalculator()


@trading_data_bp.route("/raw-data/alert/<alert_id>", methods=["POST"])
def get_raw_data_for_alert(alert_id):
    """
    Get comprehensive raw trading data for a specific alert

    This endpoint provides analysts with detailed raw trading data including:
    - Execution timestamps
    - Traded prices
    - Instruments
    - Direction (buy/sell)
    - Quantities
    - Market context
    - Risk indicators
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Process the data to get the context
        processed_data = data_processor.process(data)

        # Get comprehensive raw trading data
        raw_data = trading_data_service.get_raw_trading_data_for_alert(
            alert_id, processed_data
        )

        response = {
            "status": "success",
            "alert_id": alert_id,
            "raw_trading_data": raw_data,
            "timestamp": datetime.utcnow().isoformat(),
        }

        logger.info(f"Retrieved raw trading data for alert {alert_id}")
        return jsonify(response)

    except Exception as e:
        logger.error(f"Error getting raw trading data for alert {alert_id}: {str(e)}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500


@trading_data_bp.route("/raw-data/trader/<trader_id>", methods=["GET"])
def get_raw_data_for_trader(trader_id):
    """
    Get raw trading data for a specific trader within a date range

    Query parameters:
    - start_date: Start date (ISO format)
    - end_date: End date (ISO format)
    """
    try:
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")

        if not start_date or not end_date:
            return (
                jsonify({"error": "start_date and end_date parameters required"}),
                400,
            )

        # Get raw trading data for trader
        raw_data = trading_data_service.get_raw_trading_data_for_trader(
            trader_id, start_date, end_date
        )

        response = {
            "status": "success",
            "trader_id": trader_id,
            "date_range": {"start": start_date, "end": end_date},
            "raw_trading_data": raw_data,
            "timestamp": datetime.utcnow().isoformat(),
        }

        logger.info(f"Retrieved raw trading data for trader {trader_id}")
        return jsonify(response)

    except Exception as e:
        logger.error(f"Error getting raw trading data for trader {trader_id}: {str(e)}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500


@trading_data_bp.route("/raw-data/summary/<alert_id>", methods=["POST"])
def get_trading_data_summary(alert_id):
    """
    Get trading data summary for a specific alert

    Provides aggregated metrics and analysis of trading activity
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Process the data
        processed_data = data_processor.process(data)

        # Extract raw data first
        raw_trades = trading_data_service.extract_raw_trades_for_alert(
            alert_id, processed_data
        )
        raw_orders = trading_data_service.extract_raw_orders_for_alert(
            alert_id, processed_data
        )

        # Generate summary
        summary = trading_data_service.generate_trading_data_summary(
            alert_id, raw_trades, raw_orders
        )

        response = {
            "status": "success",
            "alert_id": alert_id,
            "summary": summary.to_dict(),
            "timestamp": datetime.utcnow().isoformat(),
        }

        logger.info(f"Generated trading data summary for alert {alert_id}")
        return jsonify(response)

    except Exception as e:
        logger.error(
            f"Error getting trading data summary for alert {alert_id}: {str(e)}"
        )
        return jsonify({"error": "Internal server error", "details": str(e)}), 500


@trading_data_bp.route("/raw-data/export/csv/<alert_id>", methods=["POST"])
def export_raw_data_csv(alert_id):
    """
    Export raw trading data as CSV for analyst investigation

    Provides downloadable CSV file with comprehensive trading data
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Process the data
        processed_data = data_processor.process(data)

        # Get raw trading data
        raw_data = trading_data_service.get_raw_trading_data_for_alert(
            alert_id, processed_data
        )

        # Create CSV content
        csv_content = _create_csv_content(raw_data)

        # Create in-memory file
        output = io.StringIO()
        output.write(csv_content)
        output.seek(0)

        # Convert to bytes for download
        csv_bytes = io.BytesIO()
        csv_bytes.write(output.getvalue().encode("utf-8"))
        csv_bytes.seek(0)

        filename = f"raw_trading_data_{alert_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"

        return send_file(
            csv_bytes, mimetype="text/csv", as_attachment=True, download_name=filename
        )

    except Exception as e:
        logger.error(
            f"Error exporting raw trading data CSV for alert {alert_id}: {str(e)}"
        )
        return jsonify({"error": "Internal server error", "details": str(e)}), 500


@trading_data_bp.route("/raw-data/export/json/<alert_id>", methods=["POST"])
def export_raw_data_json(alert_id):
    """
    Export raw trading data as JSON for analyst investigation

    Provides downloadable JSON file with comprehensive trading data
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Process the data
        processed_data = data_processor.process(data)

        # Get raw trading data
        raw_data = trading_data_service.get_raw_trading_data_for_alert(
            alert_id, processed_data
        )

        # Create JSON content
        json_content = json.dumps(raw_data, indent=2, default=str)

        # Create in-memory file
        json_bytes = io.BytesIO()
        json_bytes.write(json_content.encode("utf-8"))
        json_bytes.seek(0)

        filename = f"raw_trading_data_{alert_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"

        return send_file(
            json_bytes,
            mimetype="application/json",
            as_attachment=True,
            download_name=filename,
        )

    except Exception as e:
        logger.error(
            f"Error exporting raw trading data JSON for alert {alert_id}: {str(e)}"
        )
        return jsonify({"error": "Internal server error", "details": str(e)}), 500


@trading_data_bp.route("/raw-data/analyze/<alert_id>", methods=["POST"])
def analyze_raw_data_with_context(alert_id):
    """
    Analyze raw trading data with full context and risk assessment

    Provides comprehensive analysis including:
    - Raw trading data
    - Risk scores
    - Alert generation
    - Regulatory context
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Process the data
        processed_data = data_processor.process(data)

        # Calculate risk scores
        use_latent_intent = data.get("use_latent_intent", False)
        # Use latent intent method if available, otherwise use standard method
        if use_latent_intent and hasattr(
            bayesian_engine, "calculate_insider_dealing_risk_with_latent_intent"
        ):
            insider_dealing_score = (
                bayesian_engine.calculate_insider_dealing_risk_with_latent_intent(
                    processed_data
                )
            )
        else:
            insider_dealing_score = bayesian_engine.calculate_insider_dealing_risk(
                processed_data
            )
        spoofing_score = bayesian_engine.calculate_spoofing_risk(processed_data)

        # Calculate overall risk
        overall_risk = risk_calculator.calculate_overall_risk(
            insider_dealing_score, spoofing_score, processed_data
        )

        # Generate alerts
        alerts = alert_generator.generate_alerts(
            processed_data, insider_dealing_score, spoofing_score, overall_risk
        )

        # Get raw trading data
        raw_data = trading_data_service.get_raw_trading_data_for_alert(
            alert_id, processed_data
        )

        # Generate regulatory rationale if requested
        include_regulatory_rationale = data.get("include_regulatory_rationale", False)
        regulatory_rationales = []

        if include_regulatory_rationale and alerts:
            for alert in alerts:
                try:
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
                                    "node_name": path.node_name,
                                    "evidence_value": path.evidence_value,
                                    "probability": path.probability,
                                    "contribution": path.contribution,
                                    "rationale": path.rationale,
                                    "confidence": path.confidence,
                                    "regulatory_relevance": path.regulatory_relevance,
                                }
                                for path in rationale.inference_paths
                            ],
                            "voi_analysis": rationale.voi_analysis,
                            "sensitivity_report": rationale.sensitivity_report,
                            "regulatory_frameworks": rationale.regulatory_frameworks,
                            "audit_trail": rationale.audit_trail,
                        }
                    )
                except Exception as e:
                    logger.error(
                        f"Error generating regulatory rationale for alert {alert['id']}: {str(e)}"
                    )

        response = {
            "status": "success",
            "alert_id": alert_id,
            "analysis_id": f"analysis_{alert_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            "raw_trading_data": raw_data,
            "risk_scores": {
                "insider_dealing": insider_dealing_score,
                "spoofing": spoofing_score,
                "overall_risk": overall_risk,
            },
            "alerts": alerts,
            "regulatory_rationales": regulatory_rationales,
            "timestamp": datetime.utcnow().isoformat(),
        }

        logger.info(f"Completed comprehensive analysis for alert {alert_id}")
        return jsonify(response)

    except Exception as e:
        logger.error(f"Error analyzing raw data for alert {alert_id}: {str(e)}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500


@trading_data_bp.route("/raw-data/search", methods=["POST"])
def search_raw_trading_data():
    """
    Search raw trading data based on criteria

    Request body should contain search criteria:
    - trader_id: Trader identifier
    - instrument: Instrument filter
    - start_date: Start date
    - end_date: End date
    - direction: Trade direction (buy/sell)
    - min_quantity: Minimum quantity
    - max_quantity: Maximum quantity
    - min_price: Minimum price
    - max_price: Maximum price
    """
    try:
        search_criteria = request.get_json()

        if not search_criteria:
            return jsonify({"error": "No search criteria provided"}), 400

        # Extract search parameters
        trader_id = search_criteria.get("trader_id")
        instrument = search_criteria.get("instrument")
        start_date = search_criteria.get("start_date")
        end_date = search_criteria.get("end_date")
        direction = search_criteria.get("direction")
        min_quantity = search_criteria.get("min_quantity")
        max_quantity = search_criteria.get("max_quantity")
        min_price = search_criteria.get("min_price")
        max_price = search_criteria.get("max_price")

        # Search through cached data
        matching_trades = []
        matching_orders = []

        for alert_id, trades in trading_data_service.raw_trades_cache.items():
            for trade in trades:
                if _matches_criteria(trade, search_criteria):
                    matching_trades.append(trade.to_dict())

        for alert_id, orders in trading_data_service.raw_orders_cache.items():
            for order in orders:
                if _matches_order_criteria(order, search_criteria):
                    matching_orders.append(order.to_dict())

        response = {
            "status": "success",
            "search_criteria": search_criteria,
            "results": {
                "trades": matching_trades,
                "orders": matching_orders,
                "total_trades": len(matching_trades),
                "total_orders": len(matching_orders),
            },
            "timestamp": datetime.utcnow().isoformat(),
        }

        logger.info(
            f"Search completed: {len(matching_trades)} trades, {len(matching_orders)} orders found"
        )
        return jsonify(response)

    except Exception as e:
        logger.error(f"Error searching raw trading data: {str(e)}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500


def _create_csv_content(raw_data):
    """Create CSV content from raw trading data"""
    output = io.StringIO()

    # Write trades data
    if raw_data["raw_trades"]:
        output.write("=== TRADES DATA ===\n")
        trade_fieldnames = raw_data["raw_trades"][0].keys()
        writer = csv.DictWriter(output, fieldnames=trade_fieldnames)
        writer.writeheader()
        writer.writerows(raw_data["raw_trades"])
        output.write("\n")

    # Write orders data
    if raw_data["raw_orders"]:
        output.write("=== ORDERS DATA ===\n")
        order_fieldnames = raw_data["raw_orders"][0].keys()
        writer = csv.DictWriter(output, fieldnames=order_fieldnames)
        writer.writeheader()
        writer.writerows(raw_data["raw_orders"])
        output.write("\n")

    # Write summary
    output.write("=== SUMMARY ===\n")
    summary_data = raw_data["summary"]
    for key, value in summary_data.items():
        output.write(f"{key},{value}\n")

    return output.getvalue()


def _matches_criteria(trade, criteria):
    """Check if trade matches search criteria"""
    if criteria.get("trader_id") and trade.trader_id != criteria["trader_id"]:
        return False

    if criteria.get("instrument") and trade.instrument != criteria["instrument"]:
        return False

    if (
        criteria.get("start_date")
        and trade.execution_timestamp < criteria["start_date"]
    ):
        return False

    if criteria.get("end_date") and trade.execution_timestamp > criteria["end_date"]:
        return False

    if criteria.get("direction") and trade.direction.value != criteria["direction"]:
        return False

    if criteria.get("min_quantity") and trade.quantity < criteria["min_quantity"]:
        return False

    if criteria.get("max_quantity") and trade.quantity > criteria["max_quantity"]:
        return False

    if criteria.get("min_price") and trade.executed_price < criteria["min_price"]:
        return False

    if criteria.get("max_price") and trade.executed_price > criteria["max_price"]:
        return False

    return True


def _matches_order_criteria(order, criteria):
    """Check if order matches search criteria"""
    if criteria.get("trader_id") and order.trader_id != criteria["trader_id"]:
        return False

    if criteria.get("instrument") and order.instrument != criteria["instrument"]:
        return False

    if criteria.get("start_date") and order.order_timestamp < criteria["start_date"]:
        return False

    if criteria.get("end_date") and order.order_timestamp > criteria["end_date"]:
        return False

    if criteria.get("direction") and order.side.value != criteria["direction"]:
        return False

    if criteria.get("min_quantity") and order.quantity < criteria["min_quantity"]:
        return False

    if criteria.get("max_quantity") and order.quantity > criteria["max_quantity"]:
        return False

    return True
