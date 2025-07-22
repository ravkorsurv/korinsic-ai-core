"""
Role-Aware Data Quality Strategy

Implements role-aware data quality scoring that includes DQSI trust bucket
categorization for improved analyst interpretation and filtering.
"""

import logging
from typing import Any, Dict, List

from .dq_sufficiency_index import DQSufficiencyIndex

logger = logging.getLogger(__name__)


class RoleAwareDQStrategy:
    """
    Role-aware data quality strategy that adjusts scoring based on user roles
    and includes DQSI trust bucket categorization in output.

    This strategy ensures that different user roles receive appropriately
    calibrated data quality assessments based on their risk tolerance and
    regulatory requirements.
    """

    def __init__(self):
        """Initialize role-aware DQ strategy."""
        self.dqsi_calculator = DQSufficiencyIndex()
        logger.info("Role-aware DQ strategy initialized")

    def calculate_dq_score(
        self,
        evidence: Dict[str, Any],
        data_quality_metrics: Dict[str, float] = None,
        imputation_usage: Dict[str, bool] = None,
        kde_presence: Dict[str, bool] = None,
        user_role: str = "analyst",
    ) -> Dict[str, Any]:
        """
        Calculate data quality score with role-aware adjustments.

        Args:
            evidence: Raw evidence data
            data_quality_metrics: Quality metrics for data sources
            imputation_usage: Whether imputation was used for each data element
            kde_presence: Presence of Key Data Elements
            user_role: User role for role-aware scoring

        Returns:
            Dictionary containing DQ score with DQSI trust bucket
        """
        try:
            # Calculate base DQSI score
            dqsi_result = self.dqsi_calculator.calculate_dqsi(
                evidence, data_quality_metrics, imputation_usage, kde_presence
            )

            # Apply role-aware adjustments
            adjusted_result = self._apply_role_adjustments(dqsi_result, user_role)

            # Add strategy metadata
            adjusted_result["dq_strategy"] = "role_aware"
            adjusted_result["user_role"] = user_role

            logger.info(
                f"Role-aware DQ score calculated for {user_role}: "
                f"confidence={adjusted_result['dqsi_confidence_index']:.3f}, "
                f"trust_bucket={adjusted_result['dqsi_trust_bucket']}"
            )

            return adjusted_result

        except Exception as e:
            logger.error(f"Error in role-aware DQ calculation: {e}")
            return self._get_default_result(user_role)

    def _apply_role_adjustments(
        self, dqsi_result: Dict[str, Any], user_role: str
    ) -> Dict[str, Any]:
        """
        Apply role-specific adjustments to DQSI result.

        Different roles have different risk tolerances:
        - Compliance officers need higher confidence thresholds
        - Traders may accept moderate confidence for speed
        - Auditors require highest confidence levels

        Args:
            dqsi_result: Base DQSI calculation result
            user_role: User role for adjustments

        Returns:
            Adjusted DQSI result
        """
        role_adjustments = {
            "analyst": 1.0,  # No adjustment for analysts (baseline)
            "senior_analyst": 0.98,  # Slightly more conservative
            "supervisor": 0.95,  # More conservative for supervisors
            "compliance": 0.90,  # Conservative for compliance officers
            "auditor": 0.85,  # Most conservative for auditors
            "trader": 1.05,  # Slightly less conservative for traders
            "portfolio_manager": 0.96,  # Conservative for portfolio managers
            "risk_manager": 0.92,  # Conservative for risk managers
            "regulatory": 0.88,  # Very conservative for regulatory roles
        }

        adjustment_factor = role_adjustments.get(user_role, 1.0)

        # Adjust the DQSI confidence index
        original_confidence = dqsi_result["dqsi_confidence_index"]
        adjusted_confidence = min(
            original_confidence * adjustment_factor, 1.0
        )  # Cap at 1.0

        # Update confidence index and recalculate trust bucket
        dqsi_result["dqsi_confidence_index"] = round(adjusted_confidence, 3)
        dqsi_result["dqsi_trust_bucket"] = self.dqsi_calculator._get_trust_bucket(
            adjusted_confidence
        )

        # Add role-specific metadata
        dqsi_result["role_adjustment_factor"] = adjustment_factor
        dqsi_result["original_confidence_index"] = round(original_confidence, 3)
        dqsi_result["role_based_threshold"] = self._get_role_threshold(user_role)

        logger.debug(
            f"Applied {user_role} adjustment: {original_confidence:.3f} -> {adjusted_confidence:.3f}"
        )

        return dqsi_result

    def _get_role_threshold(self, user_role: str) -> Dict[str, float]:
        """
        Get role-specific thresholds for trust bucket assignment.

        Args:
            user_role: User role

        Returns:
            Dictionary with high and moderate thresholds for the role
        """
        role_thresholds = {
            "analyst": {"high": 0.85, "moderate": 0.65},
            "senior_analyst": {"high": 0.87, "moderate": 0.67},
            "supervisor": {"high": 0.88, "moderate": 0.68},
            "compliance": {"high": 0.90, "moderate": 0.72},
            "auditor": {"high": 0.92, "moderate": 0.75},
            "trader": {"high": 0.83, "moderate": 0.63},
            "portfolio_manager": {"high": 0.87, "moderate": 0.67},
            "risk_manager": {"high": 0.89, "moderate": 0.70},
            "regulatory": {"high": 0.91, "moderate": 0.74},
        }

        return role_thresholds.get(user_role, {"high": 0.85, "moderate": 0.65})

    def get_supported_roles(self) -> List[str]:
        """
        Get list of supported user roles.

        Returns:
            List of supported role names
        """
        return [
            "analyst",
            "senior_analyst",
            "supervisor",
            "compliance",
            "auditor",
            "trader",
            "portfolio_manager",
            "risk_manager",
            "regulatory",
        ]

    def get_role_requirements(self, user_role: str) -> Dict[str, Any]:
        """
        Get data quality requirements for specific role.

        Args:
            user_role: User role to get requirements for

        Returns:
            Dictionary of role-specific DQ requirements
        """
        role_requirements = {
            "analyst": {
                "min_confidence": 0.60,
                "require_kde_coverage": 0.70,
                "max_imputation_ratio": 0.30,
                "min_data_availability": 0.75,
            },
            "compliance": {
                "min_confidence": 0.80,
                "require_kde_coverage": 0.90,
                "max_imputation_ratio": 0.15,
                "min_data_availability": 0.90,
            },
            "auditor": {
                "min_confidence": 0.85,
                "require_kde_coverage": 0.95,
                "max_imputation_ratio": 0.10,
                "min_data_availability": 0.95,
            },
            "trader": {
                "min_confidence": 0.55,
                "require_kde_coverage": 0.60,
                "max_imputation_ratio": 0.40,
                "min_data_availability": 0.70,
            },
        }

        return role_requirements.get(user_role, role_requirements["analyst"])

    def _get_default_result(self, user_role: str) -> Dict[str, Any]:
        """
        Get default result when calculation fails.

        Args:
            user_role: User role for the result

        Returns:
            Default DQ result with DQSI trust bucket
        """
        default_result = {
            "dqsi_confidence_index": 0.0,
            "dqsi_trust_bucket": "Low",
            "dq_strategy": "role_aware",
            "user_role": user_role,
            "role_adjustment_factor": 1.0,
            "original_confidence_index": 0.0,
            "role_based_threshold": self._get_role_threshold(user_role),
            "data_quality_components": {
                "data_availability": 0.0,
                "imputation_ratio": 1.0,
                "kde_coverage": 0.0,
                "temporal_consistency": 0.0,
                "source_reliability": 0.0,
            },
            "quality_summary": {
                "total_data_points": 0,
                "imputation_count": 0,
                "missing_kdes": 0,
                "reliability_score": "Low",
            },
        }

        return default_result
