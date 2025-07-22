"""
KDE-First Role-Aware Data Quality Strategy

Updated role-aware strategy that integrates with the new KDE-first DQ calculator.
Role affects which KDEs are in scope for assessment, not the scoring mechanics.
Different desks/roles may have different KDE coverage requirements.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from .kde_first_dq_calculator import KDEFirstDQCalculator

logger = logging.getLogger(__name__)


class KDEFirstRoleAwareStrategy:
    """
    Role-aware DQ strategy using KDE-first scoring framework.

    In the new framework:
    - Roles determine which KDEs are assessed (scope)
    - Scoring mechanics remain consistent across roles
    - Trust bucket thresholds stay the same
    - Different roles may have different baseline requirements
    """

    def __init__(self, config_path: str = "config/dq_config.yaml", redis_client=None):
        """
        Initialize KDE-first role-aware strategy.

        Args:
            config_path: Path to DQ configuration
            redis_client: Redis client for golden source lookups
        """
        self.dq_calculator = KDEFirstDQCalculator(config_path, redis_client)
        self.config = self.dq_calculator.config
        logger.info("KDE-First role-aware DQ strategy initialized")

    def calculate_dq_score(
        self,
        evidence: Dict[str, Any],
        baseline_data: Dict[str, Any] = None,
        user_role: str = "analyst",
        alert_timestamp: datetime = None,
        desk_id: str = None,
    ) -> Dict[str, Any]:
        """
        Calculate DQ score with role-aware KDE scope filtering.

        Args:
            evidence: Raw evidence data with KDE values
            baseline_data: Historical baseline for coverage calculations
            user_role: User role determining KDE scope
            alert_timestamp: Alert timestamp for timeliness calculations
            desk_id: Desk identifier for desk-specific baselines

        Returns:
            Dictionary containing DQSI score with role-aware metadata
        """
        try:
            # Get role-specific baseline data if available
            role_baseline = self._get_role_baseline(baseline_data, user_role, desk_id)

            # Calculate DQSI using KDE-first approach with role filtering
            result = self.dq_calculator.calculate_dqsi(
                evidence=evidence,
                baseline_data=role_baseline,
                user_role=user_role,
                alert_timestamp=alert_timestamp,
            )

            # Add role-aware metadata
            result["dq_strategy"] = "kde_first_role_aware"
            result["role_metadata"] = self._get_role_metadata(
                user_role, evidence, result
            )

            # Validate against role-specific requirements
            role_validation = self._validate_role_requirements(result, user_role)
            result["role_validation"] = role_validation

            logger.info(
                f"KDE-First role-aware DQ calculated for {user_role}: "
                f"score={result['dqsi_score']:.3f}, "
                f"kdes_in_scope={len(result['applicable_kdes'])}, "
                f"role_compliance={role_validation['compliant']}"
            )

            return result

        except Exception as e:
            logger.error(f"Error in KDE-First role-aware DQ calculation: {e}")
            return self._get_default_result(user_role)

    def _get_role_baseline(
        self, baseline_data: Dict[str, Any], user_role: str, desk_id: str = None
    ) -> Dict[str, Any]:
        """
        Get role-specific baseline data for coverage calculations.

        Different roles/desks may have different historical patterns.
        """
        if not baseline_data:
            return None

        # Use desk-specific baseline if available
        if desk_id and f"desk_{desk_id}" in baseline_data:
            return baseline_data[f"desk_{desk_id}"]

        # Use role-specific baseline if available
        if f"role_{user_role}" in baseline_data:
            return baseline_data[f"role_{user_role}"]

        # Fall back to general baseline
        return baseline_data

    def _get_role_metadata(
        self, user_role: str, evidence: Dict[str, Any], result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate role-specific metadata for the assessment."""
        role_scope = self.config["role_kde_scope"].get(user_role, [])
        applicable_kdes = result["applicable_kdes"]

        return {
            "role_kde_scope": role_scope,
            "scope_coverage": (
                len(applicable_kdes) / len(role_scope) if role_scope else 0.0
            ),
            "missing_kdes": [kde for kde in role_scope if kde not in evidence],
            "out_of_scope_kdes": [
                kde for kde in evidence.keys() if kde not in role_scope
            ],
            "role_requirements": self._get_role_requirements(user_role),
            "assessment_completeness": self._assess_role_completeness(
                user_role, applicable_kdes
            ),
        }

    def _get_role_requirements(self, user_role: str) -> Dict[str, Any]:
        """
        Get specific requirements for the user role.

        Different roles have different risk tolerance and coverage needs.
        """
        role_requirements = {
            "analyst": {
                "min_kde_coverage": 0.70,
                "critical_kdes": ["trader_id", "notional", "trade_date"],
                "preferred_dimensions": ["completeness", "timeliness", "coverage"],
                "risk_tolerance": "moderate",
            },
            "trader_role": {
                "min_kde_coverage": 0.60,
                "critical_kdes": ["trader_id", "notional", "price", "quantity"],
                "preferred_dimensions": ["completeness", "timeliness"],
                "risk_tolerance": "high",
            },
            "compliance": {
                "min_kde_coverage": 0.90,
                "critical_kdes": [
                    "trader_id",
                    "notional",
                    "trade_date",
                    "counterparty",
                ],
                "preferred_dimensions": ["completeness", "accuracy", "consistency"],
                "risk_tolerance": "low",
            },
            "auditor": {
                "min_kde_coverage": 0.95,
                "critical_kdes": [
                    "trader_id",
                    "notional",
                    "trade_date",
                    "counterparty",
                    "timestamp",
                ],
                "preferred_dimensions": [
                    "completeness",
                    "accuracy",
                    "consistency",
                    "uniqueness",
                ],
                "risk_tolerance": "very_low",
            },
            "risk_manager": {
                "min_kde_coverage": 0.85,
                "critical_kdes": ["trader_id", "notional", "price", "product_code"],
                "preferred_dimensions": ["completeness", "accuracy", "timeliness"],
                "risk_tolerance": "low",
            },
        }

        return role_requirements.get(user_role, role_requirements["analyst"])

    def _assess_role_completeness(
        self, user_role: str, applicable_kdes: List[str]
    ) -> Dict[str, Any]:
        """Assess how complete the assessment is for the given role."""
        requirements = self._get_role_requirements(user_role)
        role_scope = self.config["role_kde_scope"].get(user_role, [])
        critical_kdes = requirements.get("critical_kdes", [])

        # Check critical KDE coverage
        critical_present = [kde for kde in critical_kdes if kde in applicable_kdes]
        critical_coverage = (
            len(critical_present) / len(critical_kdes) if critical_kdes else 1.0
        )

        # Check overall scope coverage
        scope_coverage = len(applicable_kdes) / len(role_scope) if role_scope else 0.0

        # Determine completeness level
        if critical_coverage >= 1.0 and scope_coverage >= requirements.get(
            "min_kde_coverage", 0.7
        ):
            completeness_level = "complete"
        elif critical_coverage >= 0.8 and scope_coverage >= 0.6:
            completeness_level = "adequate"
        elif critical_coverage >= 0.6:
            completeness_level = "partial"
        else:
            completeness_level = "insufficient"

        return {
            "completeness_level": completeness_level,
            "critical_kde_coverage": round(critical_coverage, 3),
            "scope_coverage": round(scope_coverage, 3),
            "critical_kdes_present": critical_present,
            "critical_kdes_missing": [
                kde for kde in critical_kdes if kde not in applicable_kdes
            ],
        }

    def _validate_role_requirements(
        self, result: Dict[str, Any], user_role: str
    ) -> Dict[str, Any]:
        """Validate assessment results against role-specific requirements."""
        requirements = self._get_role_requirements(user_role)
        role_metadata = result["role_metadata"]

        validations = []
        compliant = True

        # Check minimum KDE coverage
        min_coverage = requirements.get("min_kde_coverage", 0.7)
        kde_coverage = role_metadata["scope_coverage"]
        if kde_coverage < min_coverage:
            validations.append(
                {
                    "check": "minimum_kde_coverage",
                    "required": min_coverage,
                    "actual": kde_coverage,
                    "passed": False,
                    "message": f"KDE coverage {kde_coverage:.1%} below minimum {min_coverage:.1%}",
                }
            )
            compliant = False
        else:
            validations.append(
                {
                    "check": "minimum_kde_coverage",
                    "required": min_coverage,
                    "actual": kde_coverage,
                    "passed": True,
                    "message": f"KDE coverage {kde_coverage:.1%} meets minimum {min_coverage:.1%}",
                }
            )

        # Check critical KDE presence
        critical_coverage = role_metadata["assessment_completeness"][
            "critical_kde_coverage"
        ]
        if critical_coverage < 1.0:
            validations.append(
                {
                    "check": "critical_kde_presence",
                    "required": 1.0,
                    "actual": critical_coverage,
                    "passed": False,
                    "message": f"Missing critical KDEs: {role_metadata['assessment_completeness']['critical_kdes_missing']}",
                }
            )
            compliant = False
        else:
            validations.append(
                {
                    "check": "critical_kde_presence",
                    "required": 1.0,
                    "actual": critical_coverage,
                    "passed": True,
                    "message": "All critical KDEs present",
                }
            )

        # Check trust bucket alignment with risk tolerance
        trust_bucket = result["dqsi_trust_bucket"]
        risk_tolerance = requirements.get("risk_tolerance", "moderate")

        bucket_acceptable = self._check_trust_bucket_alignment(
            trust_bucket, risk_tolerance
        )
        validations.append(
            {
                "check": "trust_bucket_alignment",
                "required": risk_tolerance,
                "actual": trust_bucket,
                "passed": bucket_acceptable,
                "message": f"Trust bucket '{trust_bucket}' {'aligns with' if bucket_acceptable else 'conflicts with'} {risk_tolerance} risk tolerance",
            }
        )

        if not bucket_acceptable:
            compliant = False

        return {
            "compliant": compliant,
            "validations": validations,
            "compliance_score": sum(1 for v in validations if v["passed"])
            / len(validations),
            "risk_tolerance": risk_tolerance,
            "overall_assessment": self._get_overall_assessment(
                compliant, trust_bucket, role_metadata
            ),
        }

    def _check_trust_bucket_alignment(
        self, trust_bucket: str, risk_tolerance: str
    ) -> bool:
        """Check if trust bucket aligns with role's risk tolerance."""
        alignment_rules = {
            "very_low": ["High"],  # Auditors need High trust
            "low": [
                "High",
                "Moderate",
            ],  # Compliance/Risk managers need High or Moderate
            "moderate": ["High", "Moderate", "Low"],  # Analysts accept any
            "high": ["High", "Moderate", "Low"],  # Traders accept any
        }

        acceptable_buckets = alignment_rules.get(
            risk_tolerance, ["High", "Moderate", "Low"]
        )
        return trust_bucket in acceptable_buckets

    def _get_overall_assessment(
        self, compliant: bool, trust_bucket: str, role_metadata: Dict[str, Any]
    ) -> str:
        """Generate overall assessment summary."""
        if compliant and trust_bucket == "High":
            return "Excellent - Full compliance with high data quality confidence"
        elif compliant and trust_bucket == "Moderate":
            return "Good - Compliant with acceptable data quality confidence"
        elif compliant and trust_bucket == "Low":
            return "Acceptable - Compliant but with low data quality confidence"
        elif not compliant and trust_bucket in ["High", "Moderate"]:
            return "Needs attention - Quality good but missing required coverage"
        else:
            return "Insufficient - Does not meet role requirements"

    def get_supported_roles(self) -> List[str]:
        """Get list of supported user roles."""
        return list(self.config["role_kde_scope"].keys())

    def get_role_kde_scope(self, user_role: str) -> List[str]:
        """Get KDE scope for specific role."""
        return self.config["role_kde_scope"].get(user_role, [])

    def _get_default_result(self, user_role: str) -> Dict[str, Any]:
        """Get default result when calculation fails."""
        return {
            "dqsi_score": 0.0,
            "dqsi_trust_bucket": "Low",
            "dq_framework": "kde_first_v2",
            "dq_strategy": "kde_first_role_aware",
            "user_role": user_role,
            "kde_scores": {},
            "synthetic_scores": {"timeliness": 0.0, "coverage": 0.0},
            "score_breakdown": {
                "total_weighted_score": 0.0,
                "total_weights": 0.0,
                "foundational_weighted_score": 0.0,
                "enhanced_weighted_score": 0.0,
            },
            "applicable_kdes": [],
            "dimension_summary": {},
            "role_metadata": {
                "role_kde_scope": self.config["role_kde_scope"].get(user_role, []),
                "scope_coverage": 0.0,
                "missing_kdes": [],
                "assessment_completeness": {"completeness_level": "insufficient"},
            },
            "role_validation": {
                "compliant": False,
                "validations": [],
                "compliance_score": 0.0,
                "overall_assessment": "Calculation failed",
            },
            "error": "Calculation failed",
        }
