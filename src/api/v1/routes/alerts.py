"""
Alerts API routes for alert management.

This module contains endpoints for retrieving and managing market abuse alerts.
"""

from datetime import datetime

from flask import jsonify, request

from ....core.services.alert_service import AlertService
from .. import api_v1
from ..middleware.error_handling import handle_api_errors
from ..middleware.validation import validate_request
from ..schemas.response_schemas import AlertsResponseSchema

# Initialize services
alert_service = AlertService()


@api_v1.route("/alerts/history", methods=["GET"])
@handle_api_errors
def get_alerts_history():
    """
    Get historical alerts with optional filtering.

    Query Parameters:
        limit: Maximum number of alerts to return
        type: Alert type filter
        severity: Severity level filter
        trader_id: Filter by trader ID

    Returns:
        JSON response with historical alerts
    """
    # Extract query parameters
    limit = request.args.get("limit", 100, type=int)
    alert_type = request.args.get("type")
    severity = request.args.get("severity")
    trader_id = request.args.get("trader_id")

    # Build filters
    filters = {}
    if alert_type:
        filters["type"] = alert_type
    if severity:
        filters["severity"] = severity
    if trader_id:
        filters["trader_id"] = trader_id

    # Get alerts from service
    alerts = alert_service.get_historical_alerts(
        limit=limit, alert_type=alert_type, **filters
    )

    # Format response
    schema = AlertsResponseSchema()
    response = schema.build_response(alerts=alerts, count=len(alerts), filters=filters)

    return jsonify(response)


@api_v1.route("/alerts/<alert_id>", methods=["GET"])
@handle_api_errors
def get_alert_details(alert_id):
    """
    Get detailed information for a specific alert.

    Args:
        alert_id: ID of the alert to retrieve

    Returns:
        JSON response with alert details
    """
    # Get alert details from service
    alert_details = alert_service.get_alert_details(alert_id)

    if not alert_details:
        return jsonify({"error": f"Alert {alert_id} not found"}), 404

    response = {"timestamp": datetime.utcnow().isoformat(), "alert": alert_details}

    return jsonify(response)


@api_v1.route("/alerts/<alert_id>/status", methods=["PUT"])
@handle_api_errors
@validate_request()
def update_alert_status(alert_id):
    """
    Update the status of an alert.

    Args:
        alert_id: ID of the alert to update

    Returns:
        JSON response with updated alert status
    """
    data = request.get_json()
    new_status = data.get("status")
    notes = data.get("notes", "")

    if not new_status:
        return jsonify({"error": "Status is required"}), 400

    # Update alert status
    updated_alert = alert_service.update_alert_status(alert_id, new_status, notes)

    if not updated_alert:
        return jsonify({"error": f"Alert {alert_id} not found"}), 404

    response = {
        "timestamp": datetime.utcnow().isoformat(),
        "alert_id": alert_id,
        "status": new_status,
        "message": "Alert status updated successfully",
    }

    return jsonify(response)
