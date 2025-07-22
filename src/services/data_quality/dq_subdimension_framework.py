"""
Data Quality Sub-Dimension Framework

Defines the complete mapping of Sub-Dimensions → Measurement Types → Comparison Types
for the DQSI scoring system. This is the foundation that drives strategy implementation.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class ComparisonType(Enum):
    """Comparison types for sub-dimension validation"""

    NONE = "None"
    REFERENCE_TABLE = "Reference Table"
    GOLDEN_SOURCE = "Golden Source"
    CROSS_SYSTEM = "Cross-System"
    TREND = "Trend"


class MeasurementType(Enum):
    """Measurement types for sub-dimension scoring"""

    TYPE_CHECK = "type_check"
    LENGTH_CHECK = "length_check"
    FORMAT_CHECK = "format_check"
    RANGE_CHECK = "range_check"
    NULL_CHECK = "null_check"
    DUPLICATE_CHECK = "duplicate_check"
    CONSISTENCY_CHECK = "consistency_check"
    FRESHNESS_CHECK = "freshness_check"
    VOLUME_CHECK = "volume_check"
    ACCURACY_CHECK = "accuracy_check"
    PRECISION_CHECK = "precision_check"
    REFERENTIAL_CHECK = "referential_check"


@dataclass
class SubDimensionDefinition:
    """Definition of a sub-dimension with its measurement and comparison types"""

    name: str
    measurement_type: MeasurementType
    comparison_type: ComparisonType
    dimension: str
    tier: str  # 'foundational' or 'enhanced'
    rationale: str
    required_for_fallback: bool = False
    required_for_consumer: bool = False
    required_for_producer: bool = False


class DQSubDimensionFramework:
    """Framework defining all sub-dimensions and their relationships"""

    def __init__(self):
        """Initialize the complete sub-dimension framework"""
        self.sub_dimensions = self._define_all_sub_dimensions()
        self.dimension_mapping = self._create_dimension_mapping()

    def _define_all_sub_dimensions(self) -> Dict[str, SubDimensionDefinition]:
        """Define all sub-dimensions with their measurement types and comparison types"""

        sub_dims = {}

        # COMPLETENESS DIMENSION (Foundational)
        sub_dims["null_presence"] = SubDimensionDefinition(
            name="null_presence",
            measurement_type=MeasurementType.NULL_CHECK,
            comparison_type=ComparisonType.NONE,
            dimension="completeness",
            tier="foundational",
            rationale="Basic null/missing value detection; no external reference needed",
            required_for_fallback=True,
            required_for_consumer=True,
            required_for_producer=True,
        )

        sub_dims["field_population"] = SubDimensionDefinition(
            name="field_population",
            measurement_type=MeasurementType.NULL_CHECK,
            comparison_type=ComparisonType.REFERENCE_TABLE,
            dimension="completeness",
            tier="foundational",
            rationale="Check against expected field population rules if defined",
            required_for_fallback=False,
            required_for_consumer=True,
            required_for_producer=True,
        )

        # CONFORMITY DIMENSION (Foundational)
        sub_dims["data_type"] = SubDimensionDefinition(
            name="data_type",
            measurement_type=MeasurementType.TYPE_CHECK,
            comparison_type=ComparisonType.NONE,
            dimension="conformity",
            tier="foundational",
            rationale="Surveillance only checks parsing failures (e.g. timestamp not a date); no upstream reference needed",
            required_for_fallback=True,
            required_for_consumer=True,
            required_for_producer=True,
        )

        sub_dims["length"] = SubDimensionDefinition(
            name="length",
            measurement_type=MeasurementType.LENGTH_CHECK,
            comparison_type=ComparisonType.REFERENCE_TABLE,
            dimension="conformity",
            tier="foundational",
            rationale="If length rules are declared by master system; otherwise None if inferred",
            required_for_fallback=False,
            required_for_consumer=True,
            required_for_producer=True,
        )

        sub_dims["format"] = SubDimensionDefinition(
            name="format",
            measurement_type=MeasurementType.FORMAT_CHECK,
            comparison_type=ComparisonType.REFERENCE_TABLE,
            dimension="conformity",
            tier="foundational",
            rationale="Based on pattern config (e.g. regex); no golden source but declared standard",
            required_for_fallback=True,
            required_for_consumer=True,
            required_for_producer=True,
        )

        sub_dims["range"] = SubDimensionDefinition(
            name="range",
            measurement_type=MeasurementType.RANGE_CHECK,
            comparison_type=ComparisonType.REFERENCE_TABLE,
            dimension="conformity",
            tier="foundational",
            rationale="If range is defined (e.g. hours, product type), can be enforced; else None",
            required_for_fallback=False,
            required_for_consumer=True,
            required_for_producer=True,
        )

        # TIMELINESS DIMENSION (Foundational)
        sub_dims["freshness"] = SubDimensionDefinition(
            name="freshness",
            measurement_type=MeasurementType.FRESHNESS_CHECK,
            comparison_type=ComparisonType.NONE,
            dimension="timeliness",
            tier="foundational",
            rationale="Time-based freshness check against current time; no external reference needed",
            required_for_fallback=True,
            required_for_consumer=True,
            required_for_producer=True,
        )

        sub_dims["lag_detection"] = SubDimensionDefinition(
            name="lag_detection",
            measurement_type=MeasurementType.FRESHNESS_CHECK,
            comparison_type=ComparisonType.TREND,
            dimension="timeliness",
            tier="foundational",
            rationale="Compare against historical patterns to detect unusual delays",
            required_for_fallback=False,
            required_for_consumer=False,
            required_for_producer=True,
        )

        # COVERAGE DIMENSION (Foundational)
        sub_dims["volume_profile"] = SubDimensionDefinition(
            name="volume_profile",
            measurement_type=MeasurementType.VOLUME_CHECK,
            comparison_type=ComparisonType.NONE,
            dimension="coverage",
            tier="foundational",
            rationale="Basic volume profiling without external baseline",
            required_for_fallback=True,
            required_for_consumer=True,
            required_for_producer=False,  # Producer needs reconciliation
        )

        sub_dims["volume_reconciliation"] = SubDimensionDefinition(
            name="volume_reconciliation",
            measurement_type=MeasurementType.VOLUME_CHECK,
            comparison_type=ComparisonType.CROSS_SYSTEM,
            dimension="coverage",
            tier="foundational",
            rationale="Producer must reconcile volumes against upstream systems, not just profile",
            required_for_fallback=False,
            required_for_consumer=False,
            required_for_producer=True,
        )

        sub_dims["coverage_baseline"] = SubDimensionDefinition(
            name="coverage_baseline",
            measurement_type=MeasurementType.VOLUME_CHECK,
            comparison_type=ComparisonType.TREND,
            dimension="coverage",
            tier="foundational",
            rationale="Compare against historical baselines to detect drops",
            required_for_fallback=False,
            required_for_consumer=True,
            required_for_producer=True,
        )

        # ACCURACY DIMENSION (Enhanced)
        sub_dims["precision"] = SubDimensionDefinition(
            name="precision",
            measurement_type=MeasurementType.PRECISION_CHECK,
            comparison_type=ComparisonType.GOLDEN_SOURCE,
            dimension="accuracy",
            tier="enhanced",
            rationale="Compare against authoritative golden source for precision validation",
            required_for_fallback=False,
            required_for_consumer=False,
            required_for_producer=True,
        )

        sub_dims["value_accuracy"] = SubDimensionDefinition(
            name="value_accuracy",
            measurement_type=MeasurementType.ACCURACY_CHECK,
            comparison_type=ComparisonType.GOLDEN_SOURCE,
            dimension="accuracy",
            tier="enhanced",
            rationale="Direct value comparison against golden source system",
            required_for_fallback=False,
            required_for_consumer=False,
            required_for_producer=True,
        )

        sub_dims["referential_accuracy"] = SubDimensionDefinition(
            name="referential_accuracy",
            measurement_type=MeasurementType.REFERENTIAL_CHECK,
            comparison_type=ComparisonType.REFERENCE_TABLE,
            dimension="accuracy",
            tier="enhanced",
            rationale="Validate against reference tables for referential integrity",
            required_for_fallback=False,
            required_for_consumer=False,
            required_for_producer=True,
        )

        # UNIQUENESS DIMENSION (Enhanced)
        sub_dims["duplicate_detection"] = SubDimensionDefinition(
            name="duplicate_detection",
            measurement_type=MeasurementType.DUPLICATE_CHECK,
            comparison_type=ComparisonType.NONE,
            dimension="uniqueness",
            tier="enhanced",
            rationale="Internal duplicate detection within dataset; no external reference needed",
            required_for_fallback=False,
            required_for_consumer=False,
            required_for_producer=True,
        )

        sub_dims["cross_system_uniqueness"] = SubDimensionDefinition(
            name="cross_system_uniqueness",
            measurement_type=MeasurementType.DUPLICATE_CHECK,
            comparison_type=ComparisonType.CROSS_SYSTEM,
            dimension="uniqueness",
            tier="enhanced",
            rationale="Check for duplicates across multiple systems and feeds",
            required_for_fallback=False,
            required_for_consumer=False,
            required_for_producer=True,
        )

        # CONSISTENCY DIMENSION (Enhanced)
        sub_dims["internal_consistency"] = SubDimensionDefinition(
            name="internal_consistency",
            measurement_type=MeasurementType.CONSISTENCY_CHECK,
            comparison_type=ComparisonType.NONE,
            dimension="consistency",
            tier="enhanced",
            rationale="Internal logical consistency checks within record",
            required_for_fallback=False,
            required_for_consumer=False,
            required_for_producer=True,
        )

        sub_dims["cross_system_consistency"] = SubDimensionDefinition(
            name="cross_system_consistency",
            measurement_type=MeasurementType.CONSISTENCY_CHECK,
            comparison_type=ComparisonType.CROSS_SYSTEM,
            dimension="consistency",
            tier="enhanced",
            rationale="Consistency validation across multiple systems and data sources",
            required_for_fallback=False,
            required_for_consumer=False,
            required_for_producer=True,
        )

        return sub_dims

    def _create_dimension_mapping(self) -> Dict[str, List[str]]:
        """Create mapping of dimensions to their sub-dimensions"""
        mapping = {}
        for sub_dim_name, sub_dim_def in self.sub_dimensions.items():
            dimension = sub_dim_def.dimension
            if dimension not in mapping:
                mapping[dimension] = []
            mapping[dimension].append(sub_dim_name)
        return mapping

    def get_sub_dimensions_for_strategy(
        self, strategy: str, role: Optional[str] = None
    ) -> List[str]:
        """Get required sub-dimensions for a specific strategy and role"""
        required_sub_dims = []

        for sub_dim_name, sub_dim_def in self.sub_dimensions.items():
            include = False

            if strategy == "fallback":
                include = sub_dim_def.required_for_fallback
            elif strategy == "role_aware":
                if role == "consumer":
                    include = sub_dim_def.required_for_consumer
                elif role == "producer":
                    include = sub_dim_def.required_for_producer
                else:
                    # Default to consumer if role not specified
                    include = sub_dim_def.required_for_consumer

            if include:
                required_sub_dims.append(sub_dim_name)

        return required_sub_dims

    def get_dimensions_for_strategy(
        self, strategy: str, role: Optional[str] = None
    ) -> List[str]:
        """Get required dimensions for a specific strategy and role"""
        sub_dims = self.get_sub_dimensions_for_strategy(strategy, role)
        dimensions = set()

        for sub_dim_name in sub_dims:
            sub_dim_def = self.sub_dimensions[sub_dim_name]
            dimensions.add(sub_dim_def.dimension)

        return sorted(list(dimensions))

    def get_comparison_type_for_sub_dimension(
        self, sub_dim_name: str
    ) -> ComparisonType:
        """Get comparison type for a specific sub-dimension"""
        if sub_dim_name in self.sub_dimensions:
            return self.sub_dimensions[sub_dim_name].comparison_type
        return ComparisonType.NONE

    def get_measurement_type_for_sub_dimension(
        self, sub_dim_name: str
    ) -> MeasurementType:
        """Get measurement type for a specific sub-dimension"""
        if sub_dim_name in self.sub_dimensions:
            return self.sub_dimensions[sub_dim_name].measurement_type
        return MeasurementType.TYPE_CHECK

    def print_framework_summary(self):
        """Print a summary of the complete framework"""
        print("DATA QUALITY SUB-DIMENSION FRAMEWORK")
        print("=" * 60)
        print()

        # Group by dimension
        for dimension in [
            "completeness",
            "conformity",
            "timeliness",
            "coverage",
            "accuracy",
            "uniqueness",
            "consistency",
        ]:
            if dimension in self.dimension_mapping:
                sub_dims = self.dimension_mapping[dimension]
                tier = self.sub_dimensions[sub_dims[0]].tier
                print(f"{dimension.upper()} ({tier} tier):")

                for sub_dim_name in sub_dims:
                    sub_dim = self.sub_dimensions[sub_dim_name]
                    print(f"  {sub_dim.name}:")
                    print(f"    Measurement Type: {sub_dim.measurement_type.value}")
                    print(f"    Comparison Type: {sub_dim.comparison_type.value}")
                    print(f"    Rationale: {sub_dim.rationale}")

                    # Show strategy requirements
                    req_parts = []
                    if sub_dim.required_for_fallback:
                        req_parts.append("Fallback")
                    if sub_dim.required_for_consumer:
                        req_parts.append("Consumer")
                    if sub_dim.required_for_producer:
                        req_parts.append("Producer")

                    print(
                        f"    Required for: {', '.join(req_parts) if req_parts else 'None'}"
                    )
                    print()
                print()

    def print_strategy_summary(self):
        """Print summary of what each strategy includes"""
        print("STRATEGY REQUIREMENTS SUMMARY")
        print("=" * 40)
        print()

        strategies = [
            ("fallback", None),
            ("role_aware", "consumer"),
            ("role_aware", "producer"),
        ]

        for strategy, role in strategies:
            strategy_name = f"{strategy}" + (f" ({role})" if role else "")
            print(f"{strategy_name.upper()}:")

            dimensions = self.get_dimensions_for_strategy(strategy, role)
            sub_dims = self.get_sub_dimensions_for_strategy(strategy, role)

            print(f"  Dimensions: {', '.join(dimensions)}")
            print(f"  Sub-dimensions ({len(sub_dims)}):")

            for sub_dim_name in sub_dims:
                sub_dim = self.sub_dimensions[sub_dim_name]
                print(
                    f"    - {sub_dim.name} ({sub_dim.dimension}) [{sub_dim.comparison_type.value}]"
                )
            print()


def main():
    """Demo the framework"""
    framework = DQSubDimensionFramework()
    framework.print_framework_summary()
    framework.print_strategy_summary()


if __name__ == "__main__":
    main()
