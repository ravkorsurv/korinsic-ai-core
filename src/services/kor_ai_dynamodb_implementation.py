"""
Kor.ai DynamoDB Data Access Layer
Modern NoSQL implementation with access patterns optimization
"""

import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any, Dict, List, Optional

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class KorAiDynamoDBRepository:
    """
    Modern DynamoDB repository for Kor.ai surveillance platform
    Implements single-table design with strategic GSI usage
    """

    def __init__(
        self, table_name: str = "kor-ai-surveillance", region: str = "us-east-1"
    ):
        self.table_name = table_name
        self.dynamodb = boto3.resource("dynamodb", region_name=region)
        self.table = self.dynamodb.Table(table_name)

    def _convert_floats_to_decimal(self, obj: Any) -> Any:
        """Convert float values to Decimal for DynamoDB compatibility"""
        if isinstance(obj, float):
            return Decimal(str(obj))
        elif isinstance(obj, dict):
            return {k: self._convert_floats_to_decimal(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_floats_to_decimal(item) for item in obj]
        return obj

    def _convert_decimals_to_float(self, obj: Any) -> Any:
        """Convert Decimal values back to float for application use"""
        if isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, dict):
            return {k: self._convert_decimals_to_float(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_decimals_to_float(item) for item in obj]
        return obj

    # ============ TRADER OPERATIONS ============

    def save_trader_profile(self, trader_data: Dict[str, Any]) -> None:
        """
        Save trader profile using single-table design
        Access Pattern: Direct key access
        """
        try:
            ttl = int(
                (datetime.now(timezone.utc) + timedelta(days=5 * 365)).timestamp()
            )

            item = {
                "PK": f"TRADER#{trader_data['trader_id']}",
                "SK": "PROFILE",
                "EntityType": "TRADER_PROFILE",
                "TraderID": trader_data["trader_id"],
                "Name": trader_data["name"],
                "Role": trader_data["role"],
                "Department": trader_data.get("department", ""),
                "AccessLevel": trader_data.get("access_level", "standard"),
                "StartDate": trader_data.get("start_date", ""),
                "Supervisors": trader_data.get("supervisors", []),
                "Status": trader_data.get("status", "active"),
                "LastUpdated": datetime.now(timezone.utc).isoformat(),
                "RiskProfile": trader_data.get("risk_profile", {}),
                "TradingMetrics": trader_data.get("trading_metrics", {}),
                "TTL": ttl,
            }

            item = self._convert_floats_to_decimal(item)
            self.table.put_item(Item=item)
            logger.info(f"Saved trader profile: {trader_data['trader_id']}")

        except Exception as e:
            logger.error(f"Error saving trader profile: {str(e)}")
            raise

    def get_trader_profile(self, trader_id: str) -> Optional[Dict[str, Any]]:
        """
        Get trader profile by ID
        Access Pattern: Direct key access - most efficient
        """
        try:
            response = self.table.get_item(
                Key={"PK": f"TRADER#{trader_id}", "SK": "PROFILE"}
            )

            if "Item" in response:
                return self._convert_decimals_to_float(response["Item"])
            return None

        except Exception as e:
            logger.error(f"Error getting trader profile: {str(e)}")
            raise

    def get_trader_with_recent_activity(
        self, trader_id: str, days: int = 30
    ) -> Dict[str, Any]:
        """
        Get trader profile with recent activity summary
        Access Pattern: Profile + GSI1 query for recent activity
        """
        try:
            # Get trader profile
            trader_profile = self.get_trader_profile(trader_id)
            if not trader_profile:
                return {}

            # Get recent alerts using GSI1
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
            alerts = self.get_trader_alerts(trader_id, since=cutoff_date)

            # Get recent trades using GSI2 (date-based)
            recent_trades = self.get_trader_recent_trades(trader_id, days=days)

            return {
                "trader_profile": trader_profile,
                "recent_alerts": alerts,
                "recent_trades": recent_trades,
                "activity_summary": {
                    "alert_count": len(alerts),
                    "trade_count": len(recent_trades),
                    "high_risk_alerts": len(
                        [a for a in alerts if a.get("Severity") == "HIGH"]
                    ),
                },
            }

        except Exception as e:
            logger.error(f"Error getting trader with activity: {str(e)}")
            raise

    # ============ TRADING ACTIVITY OPERATIONS ============

    def save_trade(self, trade_data: Dict[str, Any]) -> None:
        """
        Save trade with denormalized trader info
        Access Pattern: Multiple access via PK and GSIs
        """
        try:
            ttl = int(
                (datetime.now(timezone.utc) + timedelta(days=7 * 365)).timestamp()
            )
            timestamp = trade_data["timestamp"]
            trader_id = trade_data["trader_id"]

            # Parse timestamp for GSI keys
            dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            date_str = dt.strftime("%Y-%m-%d")
            time_str = dt.strftime("%H:%M:%S")

            item = {
                "PK": f"TRADER#{trader_id}",
                "SK": f"TRADE#{timestamp}#{trade_data['trade_id']}",
                "EntityType": "TRADE",
                "TradeID": trade_data["trade_id"],
                "Timestamp": timestamp,
                "Instrument": trade_data["instrument"],
                "Volume": trade_data["volume"],
                "Price": trade_data["price"],
                "Side": trade_data["side"],
                "Value": trade_data["volume"] * trade_data["price"],
                "TraderInfo": trade_data.get("trader_info", {}),
                "RiskIndicators": trade_data.get("risk_indicators", {}),
                "RelatedEvents": trade_data.get("related_events", []),
                "ProcessedMetrics": trade_data.get("processed_metrics", {}),
                # GSI keys for different access patterns
                "GSI1PK": f"INSTRUMENT#{trade_data['instrument']}",
                "GSI1SK": f"TRADE#{timestamp}",
                "GSI2PK": f"DATE#{date_str}",
                "GSI2SK": f"TRADE#{time_str}#{trader_id}",
                "TTL": ttl,
            }

            item = self._convert_floats_to_decimal(item)
            self.table.put_item(Item=item)
            logger.info(f"Saved trade: {trade_data['trade_id']}")

        except Exception as e:
            logger.error(f"Error saving trade: {str(e)}")
            raise

    def get_trader_recent_trades(
        self, trader_id: str, days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Get recent trades for a trader
        Access Pattern: PK query with SK prefix
        """
        try:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
            cutoff_str = cutoff_date.isoformat()

            response = self.table.query(
                KeyConditionExpression="PK = :pk AND begins_with(SK, :sk) AND SK >= :cutoff",
                ExpressionAttributeValues={
                    ":pk": f"TRADER#{trader_id}",
                    ":sk": "TRADE#",
                    ":cutoff": f"TRADE#{cutoff_str}",
                },
            )

            return [self._convert_decimals_to_float(item) for item in response["Items"]]

        except Exception as e:
            logger.error(f"Error getting trader trades: {str(e)}")
            raise

    def get_instrument_trades(
        self, instrument: str, start_date: datetime, end_date: datetime
    ) -> List[Dict[str, Any]]:
        """
        Get all trades for an instrument in date range
        Access Pattern: GSI1 query (instrument-based)
        """
        try:
            response = self.table.query(
                IndexName="GSI1",
                KeyConditionExpression="GSI1PK = :pk AND GSI1SK BETWEEN :start AND :end",
                ExpressionAttributeValues={
                    ":pk": f"INSTRUMENT#{instrument}",
                    ":start": f"TRADE#{start_date.isoformat()}",
                    ":end": f"TRADE#{end_date.isoformat()}",
                },
            )

            return [self._convert_decimals_to_float(item) for item in response["Items"]]

        except Exception as e:
            logger.error(f"Error getting instrument trades: {str(e)}")
            raise

    # ============ ALERT OPERATIONS ============

    def save_alert(self, alert_data: Dict[str, Any]) -> None:
        """
        Save alert with comprehensive denormalized data
        Access Pattern: Multiple GSIs for different query patterns
        """
        try:
            ttl = int(
                (datetime.now(timezone.utc) + timedelta(days=3 * 365)).timestamp()
            )
            timestamp = alert_data["timestamp"]
            alert_id = alert_data["alert_id"]

            item = {
                "PK": f"ALERT#{alert_id}",
                "SK": "METADATA",
                "EntityType": "ALERT",
                "AlertID": alert_id,
                "Type": alert_data["type"],
                "Severity": alert_data["severity"],
                "Timestamp": timestamp,
                "Status": alert_data.get("status", "ACTIVE"),
                "RiskScore": alert_data["risk_score"],
                "TraderInfo": alert_data["trader_info"],
                "Description": alert_data["description"],
                "Evidence": alert_data["evidence"],
                "ESI": alert_data.get("esi", {}),
                "Instruments": alert_data.get("instruments", []),
                "Timeframe": alert_data.get("timeframe", ""),
                "NewsContext": alert_data.get("news_context", 2),
                "HighNodes": alert_data.get("high_nodes", []),
                "CriticalNodes": alert_data.get("critical_nodes", []),
                "RecommendedActions": alert_data.get("recommended_actions", []),
                "AssignedTo": alert_data.get("assigned_to", ""),
                "Investigation": alert_data.get("investigation", {}),
                # GSI keys for different access patterns
                "GSI1PK": f"TRADER#{alert_data['trader_info']['TraderID']}",
                "GSI1SK": f"ALERT#{timestamp}#{alert_data['severity']}",
                "GSI2PK": f"SEVERITY#{alert_data['severity']}",
                "GSI2SK": f"ALERT#{timestamp}",
                "GSI3PK": f"TYPE#{alert_data['type']}",
                "GSI3SK": f"ALERT#{timestamp}",
                "TTL": ttl,
            }

            item = self._convert_floats_to_decimal(item)
            self.table.put_item(Item=item)
            logger.info(f"Saved alert: {alert_id}")

        except Exception as e:
            logger.error(f"Error saving alert: {str(e)}")
            raise

    def get_alert(self, alert_id: str) -> Optional[Dict[str, Any]]:
        """
        Get alert by ID
        Access Pattern: Direct key access
        """
        try:
            response = self.table.get_item(
                Key={"PK": f"ALERT#{alert_id}", "SK": "METADATA"}
            )

            if "Item" in response:
                return self._convert_decimals_to_float(response["Item"])
            return None

        except Exception as e:
            logger.error(f"Error getting alert: {str(e)}")
            raise

    def get_trader_alerts(
        self, trader_id: str, since: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all alerts for a trader
        Access Pattern: GSI1 query (trader-based)
        """
        try:
            key_condition = "GSI1PK = :pk"
            expression_values = {":pk": f"TRADER#{trader_id}"}

            if since:
                key_condition += " AND GSI1SK >= :since"
                expression_values[":since"] = f"ALERT#{since.isoformat()}"

            response = self.table.query(
                IndexName="GSI1",
                KeyConditionExpression=key_condition,
                ExpressionAttributeValues=expression_values,
            )

            return [self._convert_decimals_to_float(item) for item in response["Items"]]

        except Exception as e:
            logger.error(f"Error getting trader alerts: {str(e)}")
            raise

    def get_high_severity_alerts(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get high severity alerts
        Access Pattern: GSI2 query (severity-based)
        """
        try:
            response = self.table.query(
                IndexName="GSI2",
                KeyConditionExpression="GSI2PK = :pk",
                ExpressionAttributeValues={":pk": "SEVERITY#HIGH"},
                Limit=limit,
                ScanIndexForward=False,  # Most recent first
            )

            return [self._convert_decimals_to_float(item) for item in response["Items"]]

        except Exception as e:
            logger.error(f"Error getting high severity alerts: {str(e)}")
            raise

    def get_alerts_by_type(
        self, alert_type: str, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get alerts by type (INSIDER_DEALING, SPOOFING)
        Access Pattern: GSI3 query (type-based)
        """
        try:
            response = self.table.query(
                IndexName="GSI3",
                KeyConditionExpression="GSI3PK = :pk",
                ExpressionAttributeValues={":pk": f"TYPE#{alert_type}"},
                Limit=limit,
                ScanIndexForward=False,  # Most recent first
            )

            return [self._convert_decimals_to_float(item) for item in response["Items"]]

        except Exception as e:
            logger.error(f"Error getting alerts by type: {str(e)}")
            raise

    # ============ RISK SCORE OPERATIONS ============

    def save_risk_score(self, risk_data: Dict[str, Any]) -> None:
        """
        Save risk score with full Bayesian analysis
        Access Pattern: Multiple GSIs for analysis queries
        """
        try:
            ttl = int(
                (datetime.now(timezone.utc) + timedelta(days=2 * 365)).timestamp()
            )
            timestamp = risk_data["timestamp"]
            trader_id = risk_data["trader_id"]

            # Parse timestamp for GSI keys
            dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            date_str = dt.strftime("%Y-%m-%d")
            time_str = dt.strftime("%H:%M:%S")

            # Determine risk level for GSI
            risk_level = "LOW"
            if risk_data["overall_score"] >= 0.8:
                risk_level = "CRITICAL"
            elif risk_data["overall_score"] >= 0.6:
                risk_level = "HIGH"
            elif risk_data["overall_score"] >= 0.4:
                risk_level = "MEDIUM"

            item = {
                "PK": f"TRADER#{trader_id}",
                "SK": f"RISK_SCORE#{timestamp}",
                "EntityType": "RISK_SCORE",
                "RiskID": f"risk_{trader_id}_{timestamp.replace(':', '').replace('-', '')}",
                "Timestamp": timestamp,
                "TraderID": trader_id,
                "ModelType": risk_data["model_type"],
                "OverallScore": risk_data["overall_score"],
                "RiskProbabilities": risk_data.get("risk_probabilities", {}),
                "EvidenceFactors": risk_data.get("evidence_factors", {}),
                "BayesianAnalysis": risk_data.get("bayesian_analysis", {}),
                "ContextualFactors": risk_data.get("contextual_factors", {}),
                "ESI": risk_data.get("esi", {}),
                "NewsContext": risk_data.get("news_context", 2),
                "Explanation": risk_data.get("explanation", ""),
                # GSI keys for analysis queries
                "GSI1PK": f"DATE#{date_str}",
                "GSI1SK": f"RISK_SCORE#{time_str}#{trader_id}",
                "GSI2PK": f"RISK_LEVEL#{risk_level}",
                "GSI2SK": f"RISK_SCORE#{timestamp}",
                "TTL": ttl,
            }

            item = self._convert_floats_to_decimal(item)
            self.table.put_item(Item=item)
            logger.info(f"Saved risk score: {risk_data['trader_id']}")

        except Exception as e:
            logger.error(f"Error saving risk score: {str(e)}")
            raise

    def get_risk_scores_by_date(self, date: datetime) -> List[Dict[str, Any]]:
        """
        Get all risk scores for a specific date
        Access Pattern: GSI1 query (date-based)
        """
        try:
            date_str = date.strftime("%Y-%m-%d")

            response = self.table.query(
                IndexName="GSI1",
                KeyConditionExpression="GSI1PK = :pk AND begins_with(GSI1SK, :sk)",
                ExpressionAttributeValues={
                    ":pk": f"DATE#{date_str}",
                    ":sk": "RISK_SCORE#",
                },
            )

            return [self._convert_decimals_to_float(item) for item in response["Items"]]

        except Exception as e:
            logger.error(f"Error getting risk scores by date: {str(e)}")
            raise

    def get_high_risk_scores(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get high risk scores for monitoring
        Access Pattern: GSI2 query (risk level-based)
        """
        try:
            response = self.table.query(
                IndexName="GSI2",
                KeyConditionExpression="GSI2PK = :pk",
                ExpressionAttributeValues={":pk": "RISK_LEVEL#HIGH"},
                Limit=limit,
                ScanIndexForward=False,  # Most recent first
            )

            return [self._convert_decimals_to_float(item) for item in response["Items"]]

        except Exception as e:
            logger.error(f"Error getting high risk scores: {str(e)}")
            raise

    # ============ REGULATORY OPERATIONS ============

    def save_regulatory_rationale(self, rationale_data: Dict[str, Any]) -> None:
        """
        Save regulatory rationale linked to alert
        Access Pattern: Alert-based queries and compliance workflows
        """
        try:
            ttl = int(
                (datetime.now(timezone.utc) + timedelta(days=3 * 365)).timestamp()
            )
            alert_id = rationale_data["alert_id"]

            item = {
                "PK": f"ALERT#{alert_id}",
                "SK": "RATIONALE",
                "EntityType": "REGULATORY_RATIONALE",
                "AlertID": alert_id,
                "RationaleID": rationale_data["rationale_id"],
                "Timestamp": rationale_data["timestamp"],
                "DeterministicNarrative": rationale_data["deterministic_narrative"],
                "InferencePaths": rationale_data["inference_paths"],
                "VOIAnalysis": rationale_data.get("voi_analysis", {}),
                "SensitivityReport": rationale_data.get("sensitivity_report", {}),
                "RegulatoryFrameworks": rationale_data.get("regulatory_frameworks", []),
                "AuditTrail": rationale_data.get("audit_trail", {}),
                "ComplianceMetadata": rationale_data.get("compliance_metadata", {}),
                # GSI for compliance workflow
                "GSI1PK": f"COMPLIANCE#{rationale_data.get('compliance_metadata', {}).get('status', 'PENDING')}",
                "GSI1SK": f"RATIONALE#{rationale_data['timestamp']}",
                "TTL": ttl,
            }

            item = self._convert_floats_to_decimal(item)
            self.table.put_item(Item=item)
            logger.info(f"Saved regulatory rationale: {alert_id}")

        except Exception as e:
            logger.error(f"Error saving regulatory rationale: {str(e)}")
            raise

    def get_regulatory_rationale(self, alert_id: str) -> Optional[Dict[str, Any]]:
        """
        Get regulatory rationale for an alert
        Access Pattern: Direct key access
        """
        try:
            response = self.table.get_item(
                Key={"PK": f"ALERT#{alert_id}", "SK": "RATIONALE"}
            )

            if "Item" in response:
                return self._convert_decimals_to_float(response["Item"])
            return None

        except Exception as e:
            logger.error(f"Error getting regulatory rationale: {str(e)}")
            raise

    def get_pending_compliance_reviews(self) -> List[Dict[str, Any]]:
        """
        Get all pending compliance reviews
        Access Pattern: GSI1 query (compliance status-based)
        """
        try:
            response = self.table.query(
                IndexName="GSI1",
                KeyConditionExpression="GSI1PK = :pk",
                ExpressionAttributeValues={":pk": "COMPLIANCE#PENDING"},
            )

            return [self._convert_decimals_to_float(item) for item in response["Items"]]

        except Exception as e:
            logger.error(f"Error getting pending compliance reviews: {str(e)}")
            raise

    # ============ STOR RECORD OPERATIONS ============

    def save_stor_record(self, stor_data: Dict[str, Any]) -> None:
        """
        Save STOR record for regulatory reporting
        Access Pattern: Regulatory queries and compliance reporting
        """
        try:
            ttl = int(
                (datetime.now(timezone.utc) + timedelta(days=10 * 365)).timestamp()
            )
            record_id = stor_data["record_id"]

            item = {
                "PK": f"STOR#{record_id}",
                "SK": "RECORD",
                "EntityType": "STOR_RECORD",
                "RecordID": record_id,
                "AlertID": stor_data["alert_id"],
                "Timestamp": stor_data["timestamp"],
                "TraderID": stor_data["trader_id"],
                "Instrument": stor_data["instrument"],
                "TransactionType": stor_data["transaction_type"],
                "SuspiciousIndicators": stor_data["suspicious_indicators"],
                "RiskScore": stor_data["risk_score"],
                "RegulatoryRationale": stor_data["regulatory_rationale"],
                "EvidenceDetails": stor_data["evidence_details"],
                "ComplianceOfficerNotes": stor_data.get("compliance_officer_notes", ""),
                "ReportingStatus": stor_data.get("reporting_status", "PENDING"),
                "RegulatoryBody": stor_data.get("regulatory_body", ""),
                "SubmissionDate": stor_data.get("submission_date", ""),
                # GSI for regulatory reporting
                "GSI1PK": f"REGULATORY#{stor_data.get('reporting_status', 'PENDING')}",
                "GSI1SK": f"STOR#{stor_data['timestamp']}",
                "TTL": ttl,
            }

            item = self._convert_floats_to_decimal(item)
            self.table.put_item(Item=item)
            logger.info(f"Saved STOR record: {record_id}")

        except Exception as e:
            logger.error(f"Error saving STOR record: {str(e)}")
            raise

    def get_stor_records_by_status(self, status: str) -> List[Dict[str, Any]]:
        """
        Get STOR records by submission status
        Access Pattern: GSI1 query (status-based)
        """
        try:
            response = self.table.query(
                IndexName="GSI1",
                KeyConditionExpression="GSI1PK = :pk",
                ExpressionAttributeValues={":pk": f"REGULATORY#{status}"},
            )

            return [self._convert_decimals_to_float(item) for item in response["Items"]]

        except Exception as e:
            logger.error(f"Error getting STOR records by status: {str(e)}")
            raise

    # ============ BATCH OPERATIONS ============

    def batch_get_items(self, keys: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """
        Batch get multiple items efficiently
        Access Pattern: Optimized multi-item retrieval
        """
        try:
            response = self.dynamodb.batch_get_item(
                RequestItems={self.table_name: {"Keys": keys}}
            )

            items = response.get("Responses", {}).get(self.table_name, [])
            return [self._convert_decimals_to_float(item) for item in items]

        except Exception as e:
            logger.error(f"Error in batch get items: {str(e)}")
            raise

    def batch_write_items(self, items: List[Dict[str, Any]]) -> None:
        """
        Batch write multiple items efficiently
        Access Pattern: Optimized multi-item writes
        """
        try:
            # Convert items and chunk into batches of 25 (DynamoDB limit)
            converted_items = [self._convert_floats_to_decimal(item) for item in items]

            for i in range(0, len(converted_items), 25):
                batch = converted_items[i : i + 25]

                request_items = {
                    self.table_name: [{"PutRequest": {"Item": item}} for item in batch]
                }

                self.dynamodb.batch_write_item(RequestItems=request_items)

            logger.info(f"Batch wrote {len(items)} items")

        except Exception as e:
            logger.error(f"Error in batch write items: {str(e)}")
            raise

    # ============ DASHBOARD QUERIES ============

    def get_surveillance_dashboard_data(self) -> Dict[str, Any]:
        """
        Get comprehensive dashboard data using optimized queries
        Access Pattern: Multiple GSI queries for dashboard metrics
        """
        try:
            # Get high severity alerts
            high_alerts = self.get_high_severity_alerts(limit=10)

            # Get critical alerts
            critical_response = self.table.query(
                IndexName="GSI2",
                KeyConditionExpression="GSI2PK = :pk",
                ExpressionAttributeValues={":pk": "SEVERITY#CRITICAL"},
                Limit=10,
                ScanIndexForward=False,
            )
            critical_alerts = [
                self._convert_decimals_to_float(item)
                for item in critical_response["Items"]
            ]

            # Get pending compliance items
            pending_compliance = self.get_pending_compliance_reviews()

            # Get today's risk scores
            today_risks = self.get_risk_scores_by_date(datetime.now(timezone.utc))

            return {
                "high_severity_alerts": high_alerts,
                "critical_alerts": critical_alerts,
                "pending_compliance": pending_compliance,
                "today_risk_scores": today_risks,
                "summary": {
                    "high_alert_count": len(high_alerts),
                    "critical_alert_count": len(critical_alerts),
                    "pending_compliance_count": len(pending_compliance),
                    "total_risk_scores_today": len(today_risks),
                },
            }

        except Exception as e:
            logger.error(f"Error getting dashboard data: {str(e)}")
            raise

    # ============ ANALYTICS QUERIES ============

    def get_trader_risk_trends(self, trader_id: str, days: int = 30) -> Dict[str, Any]:
        """
        Get risk trend analysis for a trader
        Access Pattern: PK query with date range filtering
        """
        try:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
            cutoff_str = cutoff_date.isoformat()

            response = self.table.query(
                KeyConditionExpression="PK = :pk AND begins_with(SK, :sk) AND SK >= :cutoff",
                ExpressionAttributeValues={
                    ":pk": f"TRADER#{trader_id}",
                    ":sk": "RISK_SCORE#",
                    ":cutoff": f"RISK_SCORE#{cutoff_str}",
                },
            )

            risk_scores = [
                self._convert_decimals_to_float(item) for item in response["Items"]
            ]

            # Calculate trends
            if risk_scores:
                avg_score = sum(r["OverallScore"] for r in risk_scores) / len(
                    risk_scores
                )
                max_score = max(r["OverallScore"] for r in risk_scores)
                min_score = min(r["OverallScore"] for r in risk_scores)

                return {
                    "trader_id": trader_id,
                    "period_days": days,
                    "risk_scores": risk_scores,
                    "trends": {
                        "average_score": avg_score,
                        "maximum_score": max_score,
                        "minimum_score": min_score,
                        "total_assessments": len(risk_scores),
                        "high_risk_count": len(
                            [r for r in risk_scores if r["OverallScore"] >= 0.6]
                        ),
                    },
                }

            return {"trader_id": trader_id, "risk_scores": [], "trends": {}}

        except Exception as e:
            logger.error(f"Error getting trader risk trends: {str(e)}")
            raise


# ============ USAGE EXAMPLES ============


def example_usage():
    """
    Example usage of the DynamoDB repository
    """
    # Initialize repository
    repo = KorAiDynamoDBRepository()

    # Example 1: Save trader profile
    trader_data = {
        "trader_id": "trader_001",
        "name": "John Doe",
        "role": "senior_trader",
        "department": "Energy Trading",
        "access_level": "high",
        "risk_profile": {
            "current_risk_level": "MEDIUM",
            "total_alerts": 15,
            "high_risk_alerts": 3,
        },
        "trading_metrics": {
            "avg_daily_volume": 150000,
            "avg_daily_trades": 45,
            "primary_instruments": ["ENERGY_CORP", "OIL_FUTURE_X"],
        },
    }
    repo.save_trader_profile(trader_data)

    # Example 2: Save trade with risk indicators
    trade_data = {
        "trade_id": "trade_001",
        "timestamp": "2024-12-15T14:30:22Z",
        "trader_id": "trader_001",
        "instrument": "ENERGY_CORP",
        "volume": 100000,
        "price": 50.25,
        "side": "buy",
        "trader_info": {
            "TraderID": "trader_001",
            "Name": "John Doe",
            "Role": "senior_trader",
            "AccessLevel": "high",
        },
        "risk_indicators": {
            "pre_event_trade": True,
            "unusual_volume": True,
            "price_impact": 0.025,
            "timing_score": 0.8,
        },
    }
    repo.save_trade(trade_data)

    # Example 3: Save alert with comprehensive evidence
    alert_data = {
        "alert_id": "alert_20241215_143022",
        "timestamp": "2024-12-15T14:30:22Z",
        "type": "INSIDER_DEALING",
        "severity": "HIGH",
        "risk_score": 0.85,
        "trader_info": {
            "TraderID": "trader_001",
            "Name": "John Doe",
            "Role": "senior_trader",
            "AccessLevel": "high",
        },
        "description": "Potential insider dealing detected",
        "evidence": {
            "risk_scores": {"overall_score": 0.85},
            "bayesian_nodes": {"MaterialInfo": {"State": "Clear access"}},
            "trading_metrics": {"trades_count": 15},
        },
    }
    repo.save_alert(alert_data)

    # Example 4: Query patterns

    # Get trader with activity
    trader_with_activity = repo.get_trader_with_recent_activity("trader_001")
    print(f"Trader activity: {trader_with_activity}")

    # Get high severity alerts
    high_alerts = repo.get_high_severity_alerts()
    print(f"High alerts: {len(high_alerts)}")

    # Get dashboard data
    dashboard_data = repo.get_surveillance_dashboard_data()
    print(f"Dashboard summary: {dashboard_data['summary']}")

    # Get trader risk trends
    risk_trends = repo.get_trader_risk_trends("trader_001", days=30)
    print(f"Risk trends: {risk_trends.get('trends', {})}")


if __name__ == "__main__":
    example_usage()
