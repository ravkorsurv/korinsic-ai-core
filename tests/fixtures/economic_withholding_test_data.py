"""
Test fixtures for Economic Withholding Detection model.

This module provides sample data for testing the economic withholding
detection model including plant characteristics, offers, market conditions,
and expected analysis results.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any


def get_compliant_gas_plant_data() -> Dict[str, Any]:
    """
    Get sample data for a compliant gas plant that should pass ARERA analysis.
    
    Returns:
        Dictionary containing plant data that represents compliant behavior
    """
    return {
        "plant_data": {
            "unit_id": "COMP_GAS_001",
            "plant_name": "Compliant Gas Plant 1",
            "fuel_type": "gas",
            "capacity_mw": 400.0,
            "heat_rate": 7200,  # BTU/kWh - good efficiency
            "efficiency": 0.47,  # 47% efficiency - good for gas
            "technical_availability": 0.95,
            "variable_costs": {
                "fuel_cost_ratio": 0.85,
                "vom_cost": 3.2,  # $/MWh
                "emission_cost": 1.1  # $/MWh
            },
            "location": "Northern Italy",
            "commissioning_date": "2018-03-15",
            "technology": "CCGT"  # Combined Cycle Gas Turbine
        },
        "offers": [
            {
                "timestamp": "2024-01-15T08:00:00Z",
                "price_eur_mwh": 52.5,
                "quantity_mw": 100.0,
                "product_block": "hour_09"
            },
            {
                "timestamp": "2024-01-15T08:00:00Z",
                "price_eur_mwh": 53.2,
                "quantity_mw": 200.0,
                "product_block": "hour_09"
            },
            {
                "timestamp": "2024-01-15T08:00:00Z",
                "price_eur_mwh": 54.1,
                "quantity_mw": 300.0,
                "product_block": "hour_09"
            },
            {
                "timestamp": "2024-01-15T08:00:00Z",
                "price_eur_mwh": 55.0,
                "quantity_mw": 400.0,
                "product_block": "hour_09"
            }
        ],
        "market_data": {
            "fuel_prices": {
                "gas": 48.0  # $/MMBtu
            },
            "system_load_mw": 25000,
            "load_factor": "normal_demand",
            "market_tightness": "balanced",
            "transmission_constraints": "unconstrained"
        },
        "expected_marginal_cost": 50.8,  # Should result in ~3-8% markup
        "expected_risk_level": "low",
        "expected_compliance_status": "compliant"
    }


def get_flagged_gas_plant_data() -> Dict[str, Any]:
    """
    Get sample data for a gas plant that should be flagged for economic withholding.
    Based on ARERA 2022 case style.
    
    Returns:
        Dictionary containing plant data that represents withholding behavior
    """
    return {
        "plant_data": {
            "unit_id": "FLAG_GAS_002",
            "plant_name": "Flagged Gas Plant 2",
            "fuel_type": "gas",
            "capacity_mw": 380.0,
            "heat_rate": 7800,  # BTU/kWh - declared lower efficiency
            "efficiency": 0.43,  # 43% efficiency - claimed degradation
            "technical_availability": 0.92,
            "variable_costs": {
                "fuel_cost_ratio": 0.88,  # Higher fuel cost claim
                "vom_cost": 4.1,  # $/MWh - higher O&M costs
                "emission_cost": 1.4  # $/MWh
            },
            "location": "Southern Italy",
            "commissioning_date": "2016-09-20",
            "technology": "CCGT"
        },
        "offers": [
            {
                "timestamp": "2024-01-15T18:00:00Z",  # Peak hour
                "price_eur_mwh": 68.5,  # High markup
                "quantity_mw": 95.0,
                "product_block": "hour_19"
            },
            {
                "timestamp": "2024-01-15T18:00:00Z",
                "price_eur_mwh": 72.3,  # Excessive markup
                "quantity_mw": 190.0,
                "product_block": "hour_19"
            },
            {
                "timestamp": "2024-01-15T18:00:00Z",
                "price_eur_mwh": 78.1,  # Very high markup
                "quantity_mw": 285.0,
                "product_block": "hour_19"
            },
            {
                "timestamp": "2024-01-15T18:00:00Z",
                "price_eur_mwh": 85.0,  # Extreme markup
                "quantity_mw": 380.0,
                "product_block": "hour_19"
            }
        ],
        "market_data": {
            "fuel_prices": {
                "gas": 49.5  # $/MMBtu - similar fuel prices
            },
            "system_load_mw": 28500,  # Higher load
            "load_factor": "peak_demand",
            "market_tightness": "tight",
            "transmission_constraints": "moderate_constraints"
        },
        "expected_marginal_cost": 54.2,  # Should result in 26-57% markup
        "expected_risk_level": "high",
        "expected_compliance_status": "non_compliant",
        "expected_violations": [
            "ECONOMIC_WITHHOLDING_EXCESSIVE_MARKUP",
            "ECONOMIC_WITHHOLDING_EXTREME_MARKUP"
        ]
    }


def get_coal_plant_data() -> Dict[str, Any]:
    """
    Get sample data for a coal plant for testing different fuel types.
    
    Returns:
        Dictionary containing coal plant test data
    """
    return {
        "plant_data": {
            "unit_id": "COAL_TEST_001",
            "plant_name": "Test Coal Plant",
            "fuel_type": "coal",
            "capacity_mw": 600.0,
            "heat_rate": 9200,  # BTU/kWh
            "efficiency": 0.37,  # 37% efficiency - typical for coal
            "technical_availability": 0.88,
            "variable_costs": {
                "fuel_cost_ratio": 0.78,
                "vom_cost": 4.8,  # $/MWh
                "emission_cost": 3.2  # $/MWh - higher emissions
            },
            "location": "Central Italy",
            "commissioning_date": "2010-05-12",
            "technology": "Pulverized Coal"
        },
        "offers": [
            {
                "timestamp": "2024-01-15T14:00:00Z",
                "price_eur_mwh": 45.2,
                "quantity_mw": 150.0,
                "product_block": "hour_15"
            },
            {
                "timestamp": "2024-01-15T14:00:00Z",
                "price_eur_mwh": 46.8,
                "quantity_mw": 300.0,
                "product_block": "hour_15"
            },
            {
                "timestamp": "2024-01-15T14:00:00Z",
                "price_eur_mwh": 48.5,
                "quantity_mw": 450.0,
                "product_block": "hour_15"
            },
            {
                "timestamp": "2024-01-15T14:00:00Z",
                "price_eur_mwh": 50.2,
                "quantity_mw": 600.0,
                "product_block": "hour_15"
            }
        ],
        "market_data": {
            "fuel_prices": {
                "coal": 28.5  # $/ton
            },
            "system_load_mw": 26800,
            "load_factor": "normal_demand",
            "market_tightness": "balanced",
            "transmission_constraints": "unconstrained"
        },
        "expected_marginal_cost": 42.1,
        "expected_risk_level": "low",
        "expected_compliance_status": "compliant"
    }


def get_market_conditions_scenarios() -> List[Dict[str, Any]]:
    """
    Get various market condition scenarios for testing.
    
    Returns:
        List of market condition dictionaries
    """
    return [
        {
            "scenario_name": "low_demand_surplus",
            "system_load_mw": 18000,
            "load_factor": "low_demand",
            "market_tightness": "surplus",
            "transmission_constraints": "unconstrained",
            "competitive_context": "competitive",
            "fuel_prices": {"gas": 45.0, "coal": 25.0, "oil": 65.0},
            "expected_markup_tolerance": 0.05  # 5% markup acceptable
        },
        {
            "scenario_name": "normal_demand_balanced",
            "system_load_mw": 25000,
            "load_factor": "normal_demand",
            "market_tightness": "balanced",
            "transmission_constraints": "unconstrained",
            "competitive_context": "competitive",
            "fuel_prices": {"gas": 50.0, "coal": 28.0, "oil": 70.0},
            "expected_markup_tolerance": 0.08  # 8% markup acceptable
        },
        {
            "scenario_name": "peak_demand_tight",
            "system_load_mw": 32000,
            "load_factor": "peak_demand",
            "market_tightness": "tight",
            "transmission_constraints": "moderate_constraints",
            "competitive_context": "concentrated",
            "fuel_prices": {"gas": 55.0, "coal": 32.0, "oil": 78.0},
            "expected_markup_tolerance": 0.12  # 12% markup acceptable during peak
        },
        {
            "scenario_name": "constrained_monopolistic",
            "system_load_mw": 29000,
            "load_factor": "peak_demand",
            "market_tightness": "tight",
            "transmission_constraints": "severe_constraints",
            "competitive_context": "monopolistic",
            "fuel_prices": {"gas": 52.0, "coal": 30.0, "oil": 75.0},
            "expected_markup_tolerance": 0.10,  # Still limited by regulation
            "expected_withholding_risk": "high"
        }
    ]


def get_sample_counterfactual_results() -> Dict[str, Any]:
    """
    Get sample counterfactual analysis results for testing.
    
    Returns:
        Dictionary containing expected counterfactual analysis results
    """
    return {
        "simulation_timestamp": "2024-01-15T10:30:00Z",
        "analysis_type": "arera_counterfactual",
        "scenarios_analyzed": 3,
        "actual_offers_count": 4,
        "comparisons": [
            {
                "benchmark_scenario": "min_cost",
                "benchmark_marginal_cost": 48.2,
                "average_markup": 0.18,  # 18% average markup
                "max_markup": 0.26,      # 26% max markup
                "markup_distribution": {
                    "mean": 0.18,
                    "median": 0.17,
                    "std": 0.04,
                    "percentiles": {
                        "75": 0.21,
                        "90": 0.24,
                        "95": 0.26
                    }
                },
                "price_impact_estimate": 0.045  # 4.5% price impact
            },
            {
                "benchmark_scenario": "median_cost",
                "benchmark_marginal_cost": 50.8,
                "average_markup": 0.15,  # 15% average markup
                "max_markup": 0.22,      # 22% max markup
                "markup_distribution": {
                    "mean": 0.15,
                    "median": 0.14,
                    "std": 0.035,
                    "percentiles": {
                        "75": 0.18,
                        "90": 0.20,
                        "95": 0.22
                    }
                },
                "price_impact_estimate": 0.038  # 3.8% price impact
            },
            {
                "benchmark_scenario": "max_cost",
                "benchmark_marginal_cost": 53.5,
                "average_markup": 0.12,  # 12% average markup
                "max_markup": 0.18,      # 18% max markup
                "markup_distribution": {
                    "mean": 0.12,
                    "median": 0.11,
                    "std": 0.03,
                    "percentiles": {
                        "75": 0.14,
                        "90": 0.16,
                        "95": 0.18
                    }
                },
                "price_impact_estimate": 0.030  # 3.0% price impact
            }
        ],
        "statistical_analysis": {
            "tests_performed": ["t_test_vs_zero", "shapiro_wilk_normality", "wilcoxon_signed_rank"],
            "hypothesis_test_results": {
                "t_test_vs_zero": {
                    "statistic": 4.23,
                    "p_value": 0.008,  # Statistically significant
                    "significant_at_05": True,
                    "significant_at_01": True
                },
                "normality_test": {
                    "statistic": 0.92,
                    "p_value": 0.15,
                    "is_normal_at_05": True
                },
                "wilcoxon_test": {
                    "statistic": 15.0,
                    "p_value": 0.012,
                    "significant_at_05": True
                }
            },
            "confidence_intervals": {
                "90%": {
                    "lower": 0.08,
                    "upper": 0.22,
                    "contains_zero": False
                },
                "95%": {
                    "lower": 0.06,
                    "upper": 0.24,
                    "contains_zero": False
                },
                "99%": {
                    "lower": 0.02,
                    "upper": 0.28,
                    "contains_zero": False
                }
            }
        },
        "risk_indicators": {
            "overall_risk_score": 0.82,  # High risk
            "markup_risk_score": 0.80,
            "statistical_significance_score": 0.85,
            "pattern_consistency_score": 0.78,
            "arera_compliance_flags": [
                "EXCESSIVE_MARKUP",
                "STATISTICALLY_SIGNIFICANT_MARKUP"
            ],
            "risk_level": "high"
        }
    }


def get_sample_arera_violations() -> List[Dict[str, Any]]:
    """
    Get sample ARERA compliance violations for testing.
    
    Returns:
        List of violation dictionaries
    """
    return [
        {
            "violation_type": "ECONOMIC_WITHHOLDING_EXCESSIVE_MARKUP",
            "severity": "high",
            "description": "Average markup of 18.0% exceeds ARERA threshold of 15.0% for scenario median_cost",
            "evidence": {
                "average_markup": 0.18,
                "max_markup": 0.26,
                "benchmark_scenario": "median_cost",
                "statistical_significance": 0.008,
                "threshold_exceeded": 0.03
            },
            "statistical_significance": 0.992,
            "economic_significance": 0.18,
            "regulatory_reference": "ARERA Resolution 111/06 and subsequent amendments",
            "timestamp": "2024-01-15T10:30:00Z"
        },
        {
            "violation_type": "ECONOMIC_WITHHOLDING_EXTREME_MARKUP",
            "severity": "high",
            "description": "Maximum markup of 26.0% indicates severe economic withholding",
            "evidence": {
                "max_markup": 0.26,
                "benchmark_scenario": "median_cost",
                "extreme_threshold": 0.30
            },
            "statistical_significance": 0.99,
            "economic_significance": 0.26,
            "regulatory_reference": "ARERA Resolution 111/06 and subsequent amendments",
            "timestamp": "2024-01-15T10:30:00Z"
        },
        {
            "violation_type": "ECONOMIC_WITHHOLDING_SYSTEMATIC_PATTERN",
            "severity": "medium",
            "description": "Systematic increase in markup with quantity (slope: 0.0023, R²: 0.847)",
            "evidence": {
                "slope": 0.0023,
                "r_squared": 0.847,
                "p_value": 0.003,
                "relationship_type": "quantity_dependent_markup"
            },
            "statistical_significance": 0.997,
            "economic_significance": 0.87,  # slope * capacity
            "regulatory_reference": "ARERA Resolution 111/06 and subsequent amendments",
            "timestamp": "2024-01-15T10:30:00Z"
        }
    ]


def get_sample_cost_curve_analysis() -> Dict[str, Any]:
    """
    Get sample cost curve analysis results for testing.
    
    Returns:
        Dictionary containing cost curve analysis results
    """
    return {
        "analysis_timestamp": "2024-01-15T10:30:00Z",
        "analysis_type": "offer_cost_relationship",
        "offers_analyzed": 4,
        "cost_basis": {
            "marginal_cost": 50.8,
            "fuel_cost": 49.5,
            "efficiency": 0.43,
            "vom_cost": 4.1,
            "emission_cost": 1.4
        },
        "relationships": {
            "linear": {
                "slope": 0.0023,
                "intercept": 0.142,
                "r_squared": 0.847,
                "t_statistic": 8.92,
                "p_value": 0.003,
                "significant_at_05": True,
                "relationship_strength": "strong"
            },
            "quadratic": {
                "intercept": 0.138,
                "linear_coefficient": 0.0019,
                "quadratic_coefficient": 0.0000012,
                "r_squared": 0.863,
                "curvature": "convex",
                "relationship_strength": "strong"
            },
            "step_function": {
                "steps_detected": 3,
                "step_details": [
                    {
                        "position": 1,
                        "quantity": 190.0,
                        "markup_change": 0.057,
                        "direction": "increase"
                    },
                    {
                        "position": 2,
                        "quantity": 285.0,
                        "markup_change": 0.080,
                        "direction": "increase"
                    },
                    {
                        "position": 3,
                        "quantity": 380.0,
                        "markup_change": 0.089,
                        "direction": "increase"
                    }
                ],
                "step_consistency": 0.76,
                "pattern_type": "stepped"
            },
            "capacity_utilization": {
                "correlation": 0.89,
                "p_value": 0.001,
                "significant_correlation": True,
                "capacity_bands": {
                    "low_utilization": {"range": [0.0, 0.3], "avg_markup": 0.12, "count": 1},
                    "medium_utilization": {"range": [0.3, 0.7], "avg_markup": 0.16, "count": 2},
                    "high_utilization": {"range": [0.7, 1.0], "avg_markup": 0.22, "count": 1}
                },
                "max_utilization": 1.0,
                "avg_utilization": 0.63
            }
        },
        "statistical_measures": {
            "markup_statistics": {
                "mean": 0.18,
                "median": 0.17,
                "std": 0.04,
                "min": 0.13,
                "max": 0.26,
                "percentiles": {
                    "25": 0.15,
                    "75": 0.21,
                    "90": 0.24,
                    "95": 0.26
                }
            },
            "price_statistics": {
                "mean": 75.97,
                "median": 75.20,
                "std": 6.85,
                "coefficient_of_variation": 0.090
            },
            "quantity_statistics": {
                "mean": 237.5,
                "median": 237.5,
                "std": 120.2,
                "total": 950.0
            },
            "normality_tests": {
                "shapiro_wilk": {
                    "statistic": 0.92,
                    "p_value": 0.15,
                    "is_normal": True
                }
            },
            "outlier_analysis": {
                "outlier_count": 0,
                "outlier_percentage": 0.0,
                "outlier_values": [],
                "iqr_bounds": {"lower": 0.09, "upper": 0.27}
            }
        },
        "anomaly_detection": {
            "fuel_cost_anomalies": [
                {
                    "type": "FUEL_COST_DEVIATION",
                    "declared_value": 49.5,
                    "market_benchmark": 50.0,
                    "deviation_percent": 1.0,
                    "severity": "low"
                }
            ],
            "efficiency_anomalies": [
                {
                    "type": "LOW_EFFICIENCY",
                    "declared_value": 0.43,
                    "benchmark_range": [0.35, 0.60],
                    "severity": "medium"
                }
            ],
            "vom_cost_anomalies": [],
            "overall_anomaly_score": 0.3
        },
        "regulatory_flags": [
            "ARERA_EXCESSIVE_AVERAGE_MARKUP",
            "ARERA_SYSTEMATIC_HIGH_MARKUP",
            "ARERA_QUANTITY_DEPENDENT_MARKUP"
        ]
    }


def get_monte_carlo_test_results() -> Dict[str, Any]:
    """
    Get sample Monte Carlo simulation results for testing.
    
    Returns:
        Dictionary containing Monte Carlo simulation results
    """
    return {
        "iterations": 1000,
        "marginal_cost_distribution": list(range(1000)),  # Placeholder - would be actual cost values
        "summary_statistics": {
            "mean": 51.2,
            "median": 51.0,
            "std": 2.8,
            "min": 45.1,
            "max": 58.9,
            "percentiles": {
                "5": 47.2,
                "25": 49.1,
                "75": 53.4,
                "95": 55.8
            }
        }
    }


# Test data for different scenarios
ECONOMIC_WITHHOLDING_TEST_SCENARIOS = {
    "compliant_gas_plant": get_compliant_gas_plant_data(),
    "flagged_gas_plant": get_flagged_gas_plant_data(),
    "coal_plant": get_coal_plant_data(),
    "market_conditions": get_market_conditions_scenarios(),
    "counterfactual_results": get_sample_counterfactual_results(),
    "arera_violations": get_sample_arera_violations(),
    "cost_curve_analysis": get_sample_cost_curve_analysis(),
    "monte_carlo_results": get_monte_carlo_test_results()
}


def get_test_scenario(scenario_name: str) -> Dict[str, Any]:
    """
    Get a specific test scenario by name.
    
    Args:
        scenario_name: Name of the test scenario
        
    Returns:
        Test scenario data
    """
    return ECONOMIC_WITHHOLDING_TEST_SCENARIOS.get(scenario_name, {})


def get_all_test_scenarios() -> Dict[str, Any]:
    """
    Get all available test scenarios.
    
    Returns:
        Dictionary of all test scenarios
    """
    return ECONOMIC_WITHHOLDING_TEST_SCENARIOS