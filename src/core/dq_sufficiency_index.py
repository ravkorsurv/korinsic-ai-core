"""
Data Quality Sufficiency Index (DQSI) Module

Calculates data quality fitness for alerts and cases in the Kor.ai Surveillance platform.
Provides trust bucket categorization to prevent misinterpretation under conditions of
low data availability, high imputation, or missing critical KDEs.
"""

import logging
from collections import defaultdict
from typing import Any, Dict, List, Tuple

import numpy as np

logger = logging.getLogger(__name__)


class DQSufficiencyIndex:
    """
    Data Quality Sufficiency Index calculator that evaluates data quality fitness
    and provides trust bucket categorization for scoring outputs.

    This system complements risk scores by indicating the trustworthiness of the
    underlying data quality supporting those scores.
    """

    def __init__(self, weights: Dict[str, float] = None):
        """
        Initialize DQSI calculator with configurable weights.

        Args:
            weights: Dictionary of weights for DQSI components
        """
        self.weights = weights or {
            "data_availability": 0.30,  # Completeness of required data
            "imputation_ratio": 0.25,  # Level of data imputation used
            "kde_coverage": 0.20,  # Coverage of critical KDEs
            "temporal_consistency": 0.15,  # Data consistency over time
            "source_reliability": 0.10,  # Reliability of data sources
        }

        logger.info("DQ Sufficiency Index calculator initialized")

    def calculate_dqsi(
        self,
        evidence: Dict[str, Any],
        data_quality_metrics: Dict[str, float] = None,
        imputation_usage: Dict[str, bool] = None,
        kde_presence: Dict[str, bool] = None,
    ) -> Dict[str, Any]:
        """
        Calculate the Data Quality Sufficiency Index.

        Args:
            evidence: Raw evidence data
            data_quality_metrics: Quality metrics for data sources
            imputation_usage: Whether imputation was used for each data element
            kde_presence: Presence of Key Data Elements

        Returns:
            Dictionary containing DQSI score, confidence index, and trust bucket
        """
        try:
            # Calculate individual components
            data_availability = self._calculate_data_availability(evidence)
            imputation_ratio = self._calculate_imputation_ratio(imputation_usage)
            kde_coverage = self._calculate_kde_coverage(kde_presence)
            temporal_consistency = self._calculate_temporal_consistency(evidence)
            source_reliability = self._calculate_source_reliability(
                data_quality_metrics
            )

            # Calculate weighted DQSI confidence index
            dqsi_confidence_index = (
                self.weights["data_availability"] * data_availability
                + self.weights["imputation_ratio"] * (1 - imputation_ratio)
                + self.weights["kde_coverage"] * kde_coverage
                + self.weights["temporal_consistency"] * temporal_consistency
                + self.weights["source_reliability"] * source_reliability
            )

            # Ensure confidence index is within [0, 1] range
            dqsi_confidence_index = max(0.0, min(1.0, dqsi_confidence_index))

            # Determine trust bucket based on confidence index
            dqsi_trust_bucket = self._get_trust_bucket(dqsi_confidence_index)

            result = {
                "dqsi_confidence_index": round(dqsi_confidence_index, 3),
                "dqsi_trust_bucket": dqsi_trust_bucket,
                "data_quality_components": {
                    "data_availability": round(data_availability, 3),
                    "imputation_ratio": round(imputation_ratio, 3),
                    "kde_coverage": round(kde_coverage, 3),
                    "temporal_consistency": round(temporal_consistency, 3),
                    "source_reliability": round(source_reliability, 3),
                },
                "quality_summary": {
                    "total_data_points": len(evidence) if evidence else 0,
                    "imputation_count": sum(
                        1 for used in (imputation_usage or {}).values() if used
                    ),
                    "missing_kdes": sum(
                        1 for present in (kde_presence or {}).values() if not present
                    ),
                    "reliability_score": self._get_reliability_label(
                        source_reliability
                    ),
                },
            }

            logger.info(
                f"DQSI calculated: confidence_index={dqsi_confidence_index:.3f}, "
                f"trust_bucket={dqsi_trust_bucket}"
            )
            return result

        except Exception as e:
            logger.error(f"Error calculating DQSI: {e}")
            return self._get_default_dqsi_result()

    def _calculate_data_availability(self, evidence: Dict[str, Any]) -> float:
        """Calculate data availability ratio."""
        if not evidence:
            return 0.0

        # Count non-null, meaningful data points
        available_count = 0
        total_count = 0

        for key, value in evidence.items():
            total_count += 1
            if value is not None and value != "" and value != "Unknown":
                available_count += 1

        return available_count / total_count if total_count > 0 else 0.0

    def _calculate_imputation_ratio(self, imputation_usage: Dict[str, bool]) -> float:
        """Calculate ratio of data points that required imputation."""
        if not imputation_usage:
            return 0.0

        imputed_count = sum(1 for used in imputation_usage.values() if used)
        return imputed_count / len(imputation_usage)

    def _calculate_kde_coverage(self, kde_presence: Dict[str, bool]) -> float:
        """Calculate coverage of Key Data Elements."""
        if not kde_presence:
            return 0.5  # Default moderate coverage when unknown

        present_count = sum(1 for present in kde_presence.values() if present)
        return present_count / len(kde_presence)

    def _calculate_temporal_consistency(self, evidence: Dict[str, Any]) -> float:
        """Calculate temporal consistency of data."""
        # Simplified temporal consistency calculation
        # In a real implementation, this would analyze timestamp gaps,
        # data freshness, and temporal alignment
        if not evidence:
            return 0.0

        # Mock calculation based on data recency and completeness
        # This would be replaced with actual temporal analysis
        consistency_score = 0.7  # Default moderate consistency

        # Adjust based on evidence volume (more data often means better consistency)
        if len(evidence) >= 10:
            consistency_score = 0.8
        elif len(evidence) >= 5:
            consistency_score = 0.7
        else:
            consistency_score = 0.5

        return consistency_score

    def _calculate_source_reliability(
        self, data_quality_metrics: Dict[str, float]
    ) -> float:
        """Calculate reliability of data sources."""
        if not data_quality_metrics:
            return 0.5  # Default moderate reliability

        # Average reliability across all sources
        reliability_scores = list(data_quality_metrics.values())
        return np.mean(reliability_scores) if reliability_scores else 0.5

    def _get_trust_bucket(self, dqsi_confidence_index: float) -> str:
        """
        Map DQSI confidence index to trust bucket category.

        Args:
            dqsi_confidence_index: Confidence index value (0.0 to 1.0)

        Returns:
            Trust bucket label: "High", "Moderate", or "Low"
        """
        if dqsi_confidence_index >= 0.85:
            return "High"
        elif dqsi_confidence_index >= 0.65:
            return "Moderate"
        else:
            return "Low"

    def _get_reliability_label(self, reliability_score: float) -> str:
        """Get human-readable reliability label."""
        if reliability_score >= 0.8:
            return "High"
        elif reliability_score >= 0.6:
            return "Medium"
        else:
            return "Low"

    def _get_default_dqsi_result(self) -> Dict[str, Any]:
        """Return default DQSI result when calculation fails."""
        return {
            "dqsi_confidence_index": 0.0,
            "dqsi_trust_bucket": "Low",
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

    def validate_trust_bucket(self, trust_bucket: str) -> bool:
        """
        Validate that trust bucket value is one of the allowed values.

        Args:
            trust_bucket: Trust bucket value to validate

        Returns:
            True if valid, False otherwise
        """
        valid_buckets = {"High", "Moderate", "Low"}
        return trust_bucket in valid_buckets

    def get_boundary_test_cases(self) -> Dict[str, Dict[str, Any]]:
        """
        Get test cases for boundary values to ensure correct bucket assignment.

        Returns:
            Dictionary of test cases with confidence values and expected buckets
        """
        return {
            "high_boundary": {
                "confidence_index": 0.85,
                "expected_bucket": "High",
                "description": "Exact threshold for High bucket",
            },
            "high_above": {
                "confidence_index": 0.86,
                "expected_bucket": "High",
                "description": "Just above High threshold",
            },
            "moderate_boundary": {
                "confidence_index": 0.65,
                "expected_bucket": "Moderate",
                "description": "Exact threshold for Moderate bucket",
            },
            "moderate_above": {
                "confidence_index": 0.66,
                "expected_bucket": "Moderate",
                "description": "Just above Moderate threshold",
            },
            "moderate_below": {
                "confidence_index": 0.64,
                "expected_bucket": "Low",
                "description": "Just below Moderate threshold",
            },
            "low_boundary": {
                "confidence_index": 0.0,
                "expected_bucket": "Low",
                "description": "Minimum confidence value",
            },
            "maximum": {
                "confidence_index": 1.0,
                "expected_bucket": "High",
                "description": "Maximum confidence value",
            },
        }
