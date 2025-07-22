"""
Fallback Data Quality Strategy

Implements fallback data quality scoring when primary DQ calculations fail
or when minimal data is available. Ensures dqsi_trust_bucket is always included.
"""

import logging
from typing import Any, Dict, List, Optional

from .dq_sufficiency_index import DQSufficiencyIndex

logger = logging.getLogger(__name__)


class FallbackDQStrategy:
    """
    Fallback data quality strategy that provides conservative DQ scoring
    when primary calculations fail or when data is insufficient.

    This strategy ensures that scoring always includes DQSI trust bucket
    categorization, even under degraded conditions.
    """

    def __init__(self):
        """Initialize fallback DQ strategy."""
        self.dqsi_calculator = DQSufficiencyIndex()
        logger.info("Fallback DQ strategy initialized")

    def calculate_dq_score(
        self,
        evidence: Dict[str, Any] = None,
        data_quality_metrics: Dict[str, float] = None,
        imputation_usage: Dict[str, bool] = None,
        kde_presence: Dict[str, bool] = None,
        fallback_reason: str = "insufficient_data",
    ) -> Dict[str, Any]:
        """
        Calculate data quality score using fallback logic.

        Args:
            evidence: Raw evidence data (may be minimal or None)
            data_quality_metrics: Quality metrics for data sources (optional)
            imputation_usage: Whether imputation was used (optional)
            kde_presence: Presence of Key Data Elements (optional)
            fallback_reason: Reason for using fallback strategy

        Returns:
            Dictionary containing conservative DQ score with DQSI trust bucket
        """
        try:
            logger.warning(f"Using fallback DQ strategy due to: {fallback_reason}")

            # Attempt to calculate with available data
            if evidence or data_quality_metrics or kde_presence:
                dqsi_result = self._calculate_conservative_dqsi(
                    evidence, data_quality_metrics, imputation_usage, kde_presence
                )
            else:
                dqsi_result = self._get_minimal_dqsi_result()

            # Apply fallback adjustments (more conservative)
            adjusted_result = self._apply_fallback_adjustments(
                dqsi_result, fallback_reason
            )

            # Add strategy metadata
            adjusted_result["dq_strategy"] = "fallback"
            adjusted_result["fallback_reason"] = fallback_reason
            adjusted_result["is_degraded_mode"] = True

            logger.info(
                f"Fallback DQ score calculated: "
                f"confidence={adjusted_result['dqsi_confidence_index']:.3f}, "
                f"trust_bucket={adjusted_result['dqsi_trust_bucket']}"
            )

            return adjusted_result

        except Exception as e:
            logger.error(f"Error in fallback DQ calculation: {e}")
            return self._get_emergency_result(fallback_reason)

    def _calculate_conservative_dqsi(
        self,
        evidence: Dict[str, Any] = None,
        data_quality_metrics: Dict[str, float] = None,
        imputation_usage: Dict[str, bool] = None,
        kde_presence: Dict[str, bool] = None,
    ) -> Dict[str, Any]:
        """
        Calculate DQSI with conservative assumptions for missing data.

        Args:
            evidence: Available evidence data
            data_quality_metrics: Available quality metrics
            imputation_usage: Available imputation info
            kde_presence: Available KDE presence info

        Returns:
            Conservative DQSI result
        """
        # Fill in missing parameters with conservative defaults
        if evidence is None:
            evidence = {}

        if data_quality_metrics is None:
            # Assume low reliability for unknown sources
            data_quality_metrics = {"unknown_source": 0.3}

        if imputation_usage is None:
            # Assume high imputation when unknown
            imputation_usage = {"unknown_data": True}

        if kde_presence is None:
            # Assume missing KDEs when unknown
            kde_presence = {"critical_kde": False}

        # Calculate with conservative assumptions
        result = self.dqsi_calculator.calculate_dqsi(
            evidence, data_quality_metrics, imputation_usage, kde_presence
        )

        return result

    def _apply_fallback_adjustments(
        self, dqsi_result: Dict[str, Any], fallback_reason: str
    ) -> Dict[str, Any]:
        """
        Apply fallback-specific adjustments to make scoring more conservative.

        Args:
            dqsi_result: Base DQSI calculation result
            fallback_reason: Reason for fallback

        Returns:
            Adjusted DQSI result with more conservative scoring
        """
        # Define fallback adjustment factors (all more conservative)
        fallback_adjustments = {
            "insufficient_data": 0.70,  # Major penalty for insufficient data
            "calculation_error": 0.75,  # Penalty for calculation issues
            "missing_sources": 0.80,  # Penalty for missing data sources
            "timeout": 0.85,  # Minor penalty for timeout
            "system_degraded": 0.65,  # Major penalty for system issues
            "data_corruption": 0.60,  # Severe penalty for data corruption
            "network_error": 0.85,  # Minor penalty for network issues
            "unknown": 0.70,  # Default conservative adjustment
        }

        adjustment_factor = fallback_adjustments.get(fallback_reason, 0.70)

        # Adjust the DQSI confidence index
        original_confidence = dqsi_result["dqsi_confidence_index"]
        adjusted_confidence = original_confidence * adjustment_factor

        # Update confidence index and recalculate trust bucket
        dqsi_result["dqsi_confidence_index"] = round(adjusted_confidence, 3)
        dqsi_result["dqsi_trust_bucket"] = self.dqsi_calculator._get_trust_bucket(
            adjusted_confidence
        )

        # Add fallback metadata
        dqsi_result["fallback_adjustment_factor"] = adjustment_factor
        dqsi_result["original_confidence_index"] = round(original_confidence, 3)
        dqsi_result["degradation_level"] = self._get_degradation_level(
            adjustment_factor
        )

        logger.debug(
            f"Applied fallback adjustment for {fallback_reason}: "
            f"{original_confidence:.3f} -> {adjusted_confidence:.3f}"
        )

        return dqsi_result

    def _get_degradation_level(self, adjustment_factor: float) -> str:
        """
        Get degradation level based on adjustment factor.

        Args:
            adjustment_factor: Fallback adjustment factor

        Returns:
            Degradation level label
        """
        if adjustment_factor >= 0.80:
            return "Minor"
        elif adjustment_factor >= 0.70:
            return "Moderate"
        elif adjustment_factor >= 0.60:
            return "Severe"
        else:
            return "Critical"

    def _get_minimal_dqsi_result(self) -> Dict[str, Any]:
        """
        Get minimal DQSI result when no data is available.

        Returns:
            Minimal DQSI result with low confidence
        """
        return {
            "dqsi_confidence_index": 0.1,  # Very low confidence for minimal data
            "dqsi_trust_bucket": "Low",
            "data_quality_components": {
                "data_availability": 0.1,
                "imputation_ratio": 0.9,  # Assume high imputation
                "kde_coverage": 0.1,  # Assume minimal KDE coverage
                "temporal_consistency": 0.2,
                "source_reliability": 0.2,
            },
            "quality_summary": {
                "total_data_points": 0,
                "imputation_count": 1,  # Assume some imputation
                "missing_kdes": 1,  # Assume missing KDEs
                "reliability_score": "Low",
            },
        }

    def _get_emergency_result(self, fallback_reason: str) -> Dict[str, Any]:
        """
        Get emergency result when even fallback calculation fails.

        Args:
            fallback_reason: Reason for fallback

        Returns:
            Emergency DQ result with DQSI trust bucket
        """
        return {
            "dqsi_confidence_index": 0.0,
            "dqsi_trust_bucket": "Low",
            "dq_strategy": "fallback",
            "fallback_reason": fallback_reason,
            "is_degraded_mode": True,
            "is_emergency_mode": True,
            "fallback_adjustment_factor": 0.0,
            "original_confidence_index": 0.0,
            "degradation_level": "Critical",
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

    def can_handle_scenario(
        self,
        evidence: Dict[str, Any] = None,
        data_quality_metrics: Dict[str, float] = None,
        kde_presence: Dict[str, bool] = None,
    ) -> bool:
        """
        Check if fallback strategy can handle the given scenario.

        Args:
            evidence: Available evidence
            data_quality_metrics: Available quality metrics
            kde_presence: Available KDE presence info

        Returns:
            True if fallback can handle scenario, False otherwise
        """
        # Fallback strategy can handle any scenario, even with no data
        return True

    def get_supported_fallback_reasons(self) -> List[str]:
        """
        Get list of supported fallback reasons.

        Returns:
            List of supported fallback reason codes
        """
        return [
            "insufficient_data",
            "calculation_error",
            "missing_sources",
            "timeout",
            "system_degraded",
            "data_corruption",
            "network_error",
            "unknown",
        ]
