"""
Role-Aware Data Quality Scoring Strategy

Full-featured DQSI strategy for banks and regulated institutions.
Includes KDE scoring by producer/consumer role, reconciliation, and accuracy validation.
"""

import logging
from typing import Any, Dict, List, Optional

from .dq_strategy_base import DQConfig, DQScoringStrategy, KDEResult

logger = logging.getLogger(__name__)


class RoleAwareDQScoringStrategy(DQScoringStrategy):
    """
    Role-aware strategy for comprehensive DQSI scoring

    Features:
    - KDE scoring by producer/consumer role
    - Reconciliation against reference sources
    - Accuracy validation
    - Enhanced scoring for regulated environments
    """

    def __init__(self, config: DQConfig):
        super().__init__(config)
        logger.info("Initialized Role-Aware DQ Scoring Strategy")

    def get_strategy_name(self) -> str:
        return "role_aware"

    def score_kdes(
        self, data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None
    ) -> List[KDEResult]:
        """
        Score KDEs using role-aware approach

        Args:
            data: Input data containing KDEs
            metadata: Metadata including role information and reference data

        Returns:
            List of KDE scoring results
        """
        kde_results = []

        # Extract role information from metadata
        role = metadata.get("role", "consumer") if metadata else "consumer"
        reference_data = metadata.get("reference_data", {}) if metadata else {}
        reconciliation_data = (
            metadata.get("reconciliation_data", {}) if metadata else {}
        )

        # Score each KDE present in data
        for kde_name, kde_value in data.items():
            if kde_name in self.config.kde_risk_tiers:
                kde_result = self._score_single_kde_role_aware(
                    kde_name, kde_value, role, reference_data, reconciliation_data
                )
                kde_results.append(kde_result)

        # Add synthetic KDEs
        synthetic_kdes = self.create_synthetic_kdes(data, metadata)
        kde_results.extend(synthetic_kdes)

        logger.debug(
            f"Scored {len(kde_results)} KDEs using role-aware strategy for role: {role}"
        )
        return kde_results

    def _score_single_kde_role_aware(
        self,
        kde_name: str,
        kde_value: Any,
        role: str,
        reference_data: Dict[str, Any],
        reconciliation_data: Dict[str, Any],
    ) -> KDEResult:
        """
        Score a single KDE using role-aware logic

        Args:
            kde_name: Name of the KDE
            kde_value: Value of the KDE
            role: Role ('producer' or 'consumer')
            reference_data: Reference data for validation
            reconciliation_data: Data for reconciliation checks

        Returns:
            KDEResult for this KDE
        """
        # Get KDE metadata
        risk_tier = self.config.kde_risk_tiers.get(kde_name, "low")
        risk_weight = self.config.risk_weights.get(risk_tier, 1)
        dimension = self._get_kde_dimension(kde_name)
        tier = self._get_dimension_tier(dimension)

        # Calculate score based on role and available checks
        score_components = self._calculate_role_aware_score(
            kde_name, kde_value, role, reference_data, reconciliation_data
        )

        # Aggregate score components
        final_score = self._aggregate_score_components(score_components, role)
        imputed = score_components.get("imputed", False)

        return KDEResult(
            kde_name=kde_name,
            score=final_score,
            risk_tier=risk_tier,
            risk_weight=risk_weight,
            dimension=dimension,
            tier=tier,
            is_synthetic=False,
            imputed=imputed,
            details={
                "strategy": "role_aware",
                "role": role,
                "score_components": score_components,
                "checks_performed": list(score_components.keys()),
            },
        )

    def _calculate_role_aware_score(
        self,
        kde_name: str,
        kde_value: Any,
        role: str,
        reference_data: Dict[str, Any],
        reconciliation_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive score components for a KDE

        Args:
            kde_name: Name of the KDE
            kde_value: Value of the KDE
            role: Role ('producer' or 'consumer')
            reference_data: Reference data for validation
            reconciliation_data: Data for reconciliation

        Returns:
            Dictionary of score components
        """
        components = {}

        # 1. Basic completeness check
        components["completeness"] = self._check_completeness(kde_value)

        # 2. Conformity check (format/type validation)
        components["conformity"] = self._check_conformity(kde_name, kde_value)

        # 3. Role-specific checks
        if role == "producer":
            # Producer responsibilities: comprehensive validation
            components.update(
                self._producer_specific_checks(
                    kde_name, kde_value, reference_data, reconciliation_data
                )
            )
        else:
            # Consumer responsibilities: consumption-focused validation
            components.update(
                self._consumer_specific_checks(kde_name, kde_value, reference_data)
            )

        # 4. Enhanced tier checks (if applicable)
        dimension = self._get_kde_dimension(kde_name)
        tier = self._get_dimension_tier(dimension)

        if tier == "enhanced":
            components.update(
                self._enhanced_tier_checks(
                    kde_name, kde_value, reference_data, reconciliation_data
                )
            )

        return components

    def _check_completeness(self, kde_value: Any) -> float:
        """Check if KDE value is present and non-null"""
        if kde_value is None or kde_value == "":
            return 0.0
        elif isinstance(kde_value, str) and kde_value.lower() in [
            "unknown",
            "n/a",
            "null",
            "missing",
        ]:
            return 0.6  # Imputed value
        else:
            return 1.0

    def _check_conformity(self, kde_name: str, kde_value: Any) -> float:
        """Check if KDE value conforms to expected format/type"""
        if kde_value is None or kde_value == "":
            return 0.0

        # Use the same format validation as fallback strategy
        if kde_name in ["trader_id", "client_id", "desk_id"]:
            return self._score_id_field(kde_value)
        elif kde_name in ["trade_time", "order_timestamp", "timestamp"]:
            return self._score_timestamp_field(kde_value)
        elif kde_name in ["notional", "quantity", "price"]:
            return self._score_numeric_field(kde_value)
        elif kde_name in ["instrument"]:
            return self._score_string_field(kde_value)
        else:
            return 1.0 if kde_value is not None else 0.0

    def _producer_specific_checks(
        self,
        kde_name: str,
        kde_value: Any,
        reference_data: Dict[str, Any],
        reconciliation_data: Dict[str, Any],
    ) -> Dict[str, float]:
        """Perform producer-specific validation checks"""
        checks = {}

        # Accuracy check against reference data
        if kde_name in reference_data:
            checks["accuracy"] = self._check_accuracy_against_reference(
                kde_value, reference_data[kde_name]
            )

        # Reconciliation check
        if kde_name in reconciliation_data:
            checks["reconciliation"] = self._check_reconciliation(
                kde_value, reconciliation_data[kde_name]
            )

        # Producer-specific business rules
        checks["business_rules"] = self._check_producer_business_rules(
            kde_name, kde_value
        )

        return checks

    def _consumer_specific_checks(
        self, kde_name: str, kde_value: Any, reference_data: Dict[str, Any]
    ) -> Dict[str, float]:
        """Perform consumer-specific validation checks"""
        checks = {}

        # Basic reference validation (lighter than producer)
        if kde_name in reference_data:
            checks["reference_validation"] = self._check_basic_reference(
                kde_value, reference_data[kde_name]
            )

        # Consumer-specific business rules (lighter validation)
        checks["basic_rules"] = self._check_consumer_business_rules(kde_name, kde_value)

        return checks

    def _enhanced_tier_checks(
        self,
        kde_name: str,
        kde_value: Any,
        reference_data: Dict[str, Any],
        reconciliation_data: Dict[str, Any],
    ) -> Dict[str, float]:
        """Perform enhanced tier validation checks"""
        checks = {}

        # Uniqueness check (for enhanced tier)
        checks["uniqueness"] = self._check_uniqueness(
            kde_name, kde_value, reconciliation_data
        )

        # Consistency check (cross-system validation)
        checks["consistency"] = self._check_consistency(
            kde_name, kde_value, reconciliation_data
        )

        return checks

    def _check_accuracy_against_reference(
        self, kde_value: Any, reference_value: Any
    ) -> float:
        """Check accuracy against reference data"""
        if kde_value is None or reference_value is None:
            return 0.0

        # Exact match check
        if kde_value == reference_value:
            return 1.0

        # For numeric values, check tolerance
        if isinstance(kde_value, (int, float)) and isinstance(
            reference_value, (int, float)
        ):
            try:
                tolerance = abs(reference_value * 0.001)  # 0.1% tolerance
                if abs(kde_value - reference_value) <= tolerance:
                    return 0.95
                elif abs(kde_value - reference_value) <= tolerance * 10:
                    return 0.8
                else:
                    return 0.3
            except (ValueError, ZeroDivisionError):
                return 0.3

        # For strings, check similarity
        if isinstance(kde_value, str) and isinstance(reference_value, str):
            if kde_value.lower() == reference_value.lower():
                return 0.9  # Case mismatch
            elif (
                kde_value.replace(" ", "").lower()
                == reference_value.replace(" ", "").lower()
            ):
                return 0.8  # Spacing differences
            else:
                return 0.2  # Different values

        return 0.2  # No match

    def _check_reconciliation(self, kde_value: Any, recon_value: Any) -> float:
        """Check reconciliation against another source"""
        return self._check_accuracy_against_reference(kde_value, recon_value)

    def _check_basic_reference(self, kde_value: Any, reference_value: Any) -> float:
        """Basic reference check for consumers (lighter validation)"""
        if kde_value is None:
            return 0.0

        # Lighter validation - just check if it's in expected format/range
        if reference_value is None:
            return 0.5  # No reference available

        # Basic type compatibility
        if type(kde_value) == type(reference_value):
            return 0.8
        else:
            return 0.6

    def _check_producer_business_rules(self, kde_name: str, kde_value: Any) -> float:
        """Check producer-specific business rules"""
        # Comprehensive business rule validation for producers

        if kde_name == "trader_id":
            # Must be valid trader ID format
            if kde_value and isinstance(kde_value, str) and len(kde_value) >= 3:
                return 1.0
            else:
                return 0.3

        elif kde_name in ["notional", "quantity"]:
            # Must be positive for most trading scenarios
            try:
                value = float(kde_value)
                if value > 0:
                    return 1.0
                elif value == 0:
                    return 0.6  # Zero might be valid but flagged
                else:
                    return 0.2  # Negative suspicious
            except (ValueError, TypeError):
                return 0.0

        elif kde_name == "price":
            # Must be positive
            try:
                value = float(kde_value)
                if value > 0:
                    return 1.0
                else:
                    return 0.1  # Zero or negative price is problematic
            except (ValueError, TypeError):
                return 0.0

        else:
            return 1.0  # Default pass for unknown fields

    def _check_consumer_business_rules(self, kde_name: str, kde_value: Any) -> float:
        """Check consumer-specific business rules (lighter validation)"""
        # Basic business rule validation for consumers

        if kde_value is None or kde_value == "":
            return 0.0

        # Basic format checks only
        if kde_name in ["trader_id", "client_id"]:
            return 0.8 if isinstance(kde_value, str) and len(kde_value) > 0 else 0.2

        elif kde_name in ["notional", "quantity", "price"]:
            try:
                float(kde_value)
                return 0.9
            except (ValueError, TypeError):
                return 0.2

        else:
            return 1.0

    def _check_uniqueness(
        self, kde_name: str, kde_value: Any, reconciliation_data: Dict[str, Any]
    ) -> float:
        """Check uniqueness constraints"""
        # This would typically check against a database of known values
        # For now, return a default score
        return 0.9 if kde_value is not None else 0.0

    def _check_consistency(
        self, kde_name: str, kde_value: Any, reconciliation_data: Dict[str, Any]
    ) -> float:
        """Check consistency across systems"""
        # This would check consistency across multiple data sources
        # For now, return a default score
        return 0.8 if kde_value is not None else 0.0

    def _aggregate_score_components(
        self, components: Dict[str, Any], role: str
    ) -> float:
        """Aggregate individual score components into final score"""
        if not components:
            return 0.0

        # Define weights for different components based on role
        if role == "producer":
            weights = {
                "completeness": 0.25,
                "conformity": 0.20,
                "accuracy": 0.25,
                "reconciliation": 0.15,
                "business_rules": 0.10,
                "uniqueness": 0.03,
                "consistency": 0.02,
            }
        else:  # consumer
            weights = {
                "completeness": 0.40,
                "conformity": 0.30,
                "reference_validation": 0.20,
                "basic_rules": 0.10,
            }

        # Calculate weighted average
        total_score = 0.0
        total_weight = 0.0

        for component, score in components.items():
            if isinstance(score, (int, float)) and component in weights:
                weight = weights[component]
                total_score += score * weight
                total_weight += weight

        # Handle imputation flag
        if components.get("imputed", False):
            return 0.6  # Imputed values get fixed score

        return total_score / total_weight if total_weight > 0 else 0.0

    # Reuse scoring methods from fallback strategy
    def _score_id_field(self, value: Any) -> float:
        """Score ID fields"""
        if not value:
            return 0.0

        str_value = str(value).strip()

        if len(str_value) < 2:
            return 0.3
        elif len(str_value) > 50:
            return 0.7
        elif str_value.isalnum() or "_" in str_value or "-" in str_value:
            return 1.0
        else:
            return 0.5

    def _score_timestamp_field(self, value: Any) -> float:
        """Score timestamp fields"""
        if not value:
            return 0.0

        try:
            from datetime import datetime

            str_value = str(value)

            formats = [
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%d %H:%M:%S.%f",
                "%Y-%m-%dT%H:%M:%S.%f",
                "%Y-%m-%dT%H:%M:%SZ",
                "%Y-%m-%dT%H:%M:%S.%fZ",
            ]

            for fmt in formats:
                try:
                    datetime.strptime(str_value[:19], fmt[:19])
                    return 1.0
                except ValueError:
                    continue

            try:
                datetime.fromisoformat(str_value.replace("Z", "+00:00"))
                return 1.0
            except ValueError:
                pass

            return 0.3

        except Exception:
            return 0.0

    def _score_numeric_field(self, value: Any) -> float:
        """Score numeric fields"""
        if value is None:
            return 0.0

        try:
            float_value = float(value)

            if float_value < 0:
                return 0.2
            elif float_value == 0:
                return 0.6
            elif float_value > 1e12:
                return 0.7
            else:
                return 1.0

        except (ValueError, TypeError):
            return 0.1

    def _score_string_field(self, value: Any) -> float:
        """Score string fields"""
        if not value:
            return 0.0

        str_value = str(value).strip()

        if len(str_value) == 0:
            return 0.0
        elif len(str_value) < 2:
            return 0.4
        elif len(str_value) > 100:
            return 0.6
        else:
            return 1.0

    def _get_kde_dimension(self, kde_name: str) -> str:
        """Map KDE to its primary dimension"""
        kde_dimension_map = {
            "trader_id": "completeness",
            "trade_time": "timeliness",
            "order_timestamp": "timeliness",
            "timestamp": "timeliness",
            "notional": "completeness",
            "quantity": "completeness",
            "price": "completeness",
            "desk_id": "completeness",
            "instrument": "completeness",
            "client_id": "completeness",
        }

        return kde_dimension_map.get(kde_name, "completeness")

    def _get_dimension_tier(self, dimension: str) -> str:
        """Get tier for a dimension"""
        for tier, dimensions in self.config.dimensions.items():
            if dimension in dimensions:
                return tier
        return "foundational"
