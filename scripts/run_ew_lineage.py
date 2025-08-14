#!/usr/bin/env python3
import json
import os
from datetime import datetime
from typing import Any, Dict, Tuple

import sys

BASE = os.path.abspath(os.path.dirname(__file__))
ROOT = os.path.abspath(os.path.join(BASE, '..'))
SRC = os.path.join(ROOT, 'src')
TESTS = os.path.join(ROOT, 'tests')

sys.path.insert(0, SRC)
sys.path.insert(0, TESTS)

from fixtures.economic_withholding_test_data import (
    get_compliant_gas_plant_data,
    get_flagged_gas_plant_data,
    get_sample_counterfactual_results,
    get_sample_cost_curve_analysis,
)
from core.evidence_mapper import map_economic_withholding_evidence
import core.evidence_mapper as em

# Patch missing mapper functions with safe defaults (state index 0)
if not hasattr(em, 'map_price_impact_ratio'):
    def map_price_impact_ratio(market_data: Dict[str, Any], *_args, **_kwargs) -> int:
        return 0
    em.map_price_impact_ratio = map_price_impact_ratio  # type: ignore

if not hasattr(em, 'map_volume_participation'):
    def map_volume_participation(trade_data: Dict[str, Any], market_data: Dict[str, Any]) -> int:
        return 0
    em.map_volume_participation = map_volume_participation  # type: ignore

if not hasattr(em, 'map_liquidity_context'):
    def map_liquidity_context(market_data: Dict[str, Any], venue_data: Dict[str, Any]) -> int:
        return 0
    em.map_liquidity_context = map_liquidity_context  # type: ignore

if not hasattr(em, 'map_order_clustering'):
    def map_order_clustering(order_data: Dict[str, Any], market_data: Dict[str, Any]) -> int:
        return 0
    em.map_order_clustering = map_order_clustering  # type: ignore

if not hasattr(em, 'map_benchmark_timing'):
    def map_benchmark_timing(trade_data: Dict[str, Any], market_data: Dict[str, Any]) -> int:
        return 0
    em.map_benchmark_timing = map_benchmark_timing  # type: ignore

# Minimal node state map (extracted from nodes.py)
NODE_STATES = {
    "price_impact_ratio": ["normal_impact", "elevated_impact", "excessive_impact"],
    "volume_participation": ["normal_participation", "high_participation", "dominant_participation"],
    "liquidity_context": ["liquid", "moderate", "illiquid"],
    "order_clustering": ["normal_distribution", "moderate_clustering", "high_clustering"],
    "benchmark_timing": ["outside_window", "near_window", "during_window"],
    "profit_motivation": ["normal_profit", "unusual_profit", "suspicious_profit"],
    "fuel_cost_variance": ["aligned", "moderate_variance", "high_variance"],
    "plant_efficiency": ["optimal", "suboptimal", "significantly_impaired"],
    "marginal_cost_deviation": ["cost_reflective", "moderate_markup", "excessive_markup"],
    "heat_rate_variance": ["consistent", "moderate_variance", "significant_variance"],
    "load_factor": ["low_demand", "normal_demand", "peak_demand"],
    "market_tightness": ["surplus", "balanced", "tight"],
    "competitive_context": ["competitive", "concentrated", "monopolistic"],
    "transmission_constraint": ["unconstrained", "moderate_constraints", "severe_constraints"],
    "bid_shape_anomaly": ["normal_curve", "stepped_curve", "manipulative_curve"],
    "offer_withdrawal_pattern": ["normal_availability", "selective_withdrawal", "systematic_withholding"],
    "cross_plant_coordination": ["independent_operation", "coordinated_operation", "systematic_coordination"],
    "capacity_utilization": ["full_utilization", "partial_utilization", "artificial_limitation"],
    "markup_consistency": ["consistent_markup", "variable_markup", "strategic_markup"],
    "opportunity_pricing": ["cost_based", "opportunistic", "exploitative"],
    "fuel_price_correlation": ["strong_correlation", "weak_correlation", "no_correlation"],
    "economic_withholding_risk": ["no_withholding", "potential_withholding", "clear_withholding"],
}

class SimpleARERAViolation(dict):
    @property
    def violation_type(self):
        return self.get('violation_type')
    @property
    def severity(self):
        return self.get('severity')
    @property
    def description(self):
        return self.get('description')
    @property
    def evidence(self):
        return self.get('evidence')
    @property
    def statistical_significance(self):
        return self.get('statistical_significance')
    @property
    def economic_significance(self):
        return self.get('economic_significance')
    @property
    def regulatory_reference(self):
        return self.get('regulatory_reference')

class SimpleARERAReport:
    def __init__(self, plant_id: str, violations: Any, compliance_status: str, confidence_level: float):
        self.analysis_id = f"simple_arera_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        self.plant_id = plant_id
        self.violations = [SimpleARERAViolation(v) for v in violations]
        self.compliance_status = compliance_status
        self.confidence_level = confidence_level

def simple_arera_assess(analysis_results: Dict[str, Any], plant_data: Dict[str, Any], market_context: Dict[str, Any]) -> SimpleARERAReport:
    cf = analysis_results.get('counterfactual_analysis', {})
    stats = cf.get('statistical_analysis', {})
    comps = cf.get('comparisons', [])
    violations = []

    max_avg = 0.0
    max_markup = 0.0
    scen = 'unknown'
    for c in comps:
        avg = c.get('average_markup', 0.0)
        m = c.get('max_markup', 0.0)
        if avg > max_avg:
            max_avg = avg
            scen = c.get('benchmark_scenario', 'unknown')
        max_markup = max(max_markup, m)

    p_value = stats.get('hypothesis_test_results', {}).get('t_test_vs_zero', {}).get('p_value', 1.0)
    if max_avg > 0.15 and p_value < 0.05:
        violations.append({
            'violation_type': 'ECONOMIC_WITHHOLDING_EXCESSIVE_MARKUP',
            'severity': 'high' if max_avg > 0.25 else 'medium',
            'description': f"Average markup {max_avg:.1%} exceeds ARERA threshold 15% (scenario {scen})",
            'evidence': {'average_markup': max_avg, 'benchmark_scenario': scen, 'p_value': p_value},
            'statistical_significance': 1.0 - p_value,
            'economic_significance': max_avg,
            'regulatory_reference': 'ARERA Resolution 111/06'
        })

    if max_markup > 0.30:
        violations.append({
            'violation_type': 'ECONOMIC_WITHHOLDING_EXTREME_MARKUP',
            'severity': 'high',
            'description': f"Maximum markup {max_markup:.1%} indicates severe withholding",
            'evidence': {'max_markup': max_markup, 'scenario': scen},
            'statistical_significance': 0.99,
            'economic_significance': max_markup,
            'regulatory_reference': 'ARERA Resolution 111/06'
        })

    status = 'compliant' if not violations else ('non_compliant' if any(v['severity']=='high' for v in violations) else 'requires_investigation')
    confidence = 0.95 if status == 'compliant' else 0.9
    return SimpleARERAReport(plant_id=plant_data.get('unit_id','unknown'), violations=violations, compliance_status=status, confidence_level=confidence)

def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)

def to_string_states(numeric_evidence: Dict[str, int]) -> Dict[str, str]:
    string_evidence: Dict[str, str] = {}
    for node_name, idx in numeric_evidence.items():
        states = NODE_STATES.get(node_name)
        if states and 0 <= idx < len(states):
            string_evidence[node_name] = states[idx]
        else:
            string_evidence[node_name] = "unknown"
    return string_evidence

def fallback_risk_scores(numeric_evidence: Dict[str, int]) -> Dict[str, float]:
    high_risk_count = sum(1 for v in numeric_evidence.values() if v == 2)
    medium_risk_count = sum(1 for v in numeric_evidence.values() if v == 1)

    if high_risk_count >= 3:
        return {"no_withholding": 0.1, "potential_withholding": 0.2, "clear_withholding": 0.7}
    elif high_risk_count >= 1 or medium_risk_count >= 3:
        return {"no_withholding": 0.5, "potential_withholding": 0.4, "clear_withholding": 0.1}
    else:
        return {"no_withholding": 0.91, "potential_withholding": 0.08, "clear_withholding": 0.01}

def build_counterfactual_for_compliant() -> Dict[str, Any]:
    return {
        "simulation_timestamp": datetime.utcnow().isoformat(),
        "analysis_type": "arera_counterfactual",
        "scenarios_analyzed": 3,
        "actual_offers_count": 4,
        "comparisons": [
            {"benchmark_scenario": "median_cost", "benchmark_marginal_cost": 50.0, "average_markup": 0.04, "max_markup": 0.08, "markup_distribution": {"mean": 0.04, "median": 0.04, "std": 0.01, "percentiles": {"75": 0.05, "90": 0.06, "95": 0.08}}, "price_impact_estimate": 0.005}
        ],
        "statistical_analysis": {
            "tests_performed": ["t_test_vs_zero"],
            "hypothesis_test_results": {"t_test_vs_zero": {"statistic": 1.0, "p_value": 0.3, "significant_at_05": False, "significant_at_01": False}},
            "confidence_intervals": {"90%": {"lower": -0.01, "upper": 0.09, "contains_zero": True}},
        },
    }

def run_case(case_name: str, case_data: Dict[str, Any], flagged: bool) -> Dict[str, Any]:
    plant_data = case_data["plant_data"]
    offers = case_data["offers"]
    market_data = case_data["market_data"].copy()
    fuel_prices = case_data["market_data"].get("fuel_prices", {})

    if flagged:
        counterfactual = get_sample_counterfactual_results()
        cost_analysis = get_sample_cost_curve_analysis()
        bid_shape_analysis = {"anomaly_score": 0.72, "anomaly_flags": ["HOCKEY_STICK_PATTERN"]}
    else:
        counterfactual = build_counterfactual_for_compliant()
        cost_analysis = {
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "analysis_type": "offer_cost_relationship",
            "offers_analyzed": len(offers),
            "cost_basis": {"marginal_cost": 50.0},
            "relationships": {"linear": {"slope": 0.0005, "r_squared": 0.05, "p_value": 0.4, "significant_at_05": False}},
            "statistical_measures": {"markup_statistics": {"mean": 0.04, "max": 0.08, "percentiles": {"95": 0.08}}},
            "anomaly_detection": {"overall_anomaly_score": 0.1},
        }
        bid_shape_analysis = {"anomaly_score": 0.15, "anomaly_flags": []}

    ew_data = {
        "plant_data": plant_data,
        "market_data": {k: v for k, v in market_data.items() if k != "fuel_prices"},
        "cost_analysis": cost_analysis,
        "counterfactual_results": counterfactual,
        "operational_data": {},
        "bid_analysis": {},
        "withdrawal_data": {},
        "coordination_data": {},
        "pricing_data": {},
        "fuel_prices": fuel_prices,
    }
    numeric_evidence = map_economic_withholding_evidence(ew_data)
    string_evidence = to_string_states(numeric_evidence)

    risk_probs = fallback_risk_scores(numeric_evidence)
    max_state = max(risk_probs, key=risk_probs.get)
    confidence = risk_probs[max_state]

    compliance_report = simple_arera_assess({
        'counterfactual_analysis': counterfactual,
        'cost_curve_analysis': cost_analysis,
        'bid_shape_analysis': bid_shape_analysis,
        'bayesian_analysis': {'risk_scores': {'risk_probabilities': risk_probs, 'max_risk_state': max_state, 'confidence': confidence}}
    }, plant_data, market_data)

    alert = False
    alert_reasons = []
    if getattr(compliance_report, 'compliance_status', 'compliant') in ('non_compliant', 'requires_investigation'):
        alert = True
        alert_reasons.append(f"ARERA status: {compliance_report.compliance_status}")
    if max_state == 'clear_withholding' and confidence >= 0.6:
        alert = True
        alert_reasons.append(f"Model risk: {max_state} @ {confidence:.2f}")

    high_states = {n: s for n, s in string_evidence.items() if s in ("excessive_markup", "tight", "peak_demand", "manipulative_curve", "systematic_withholding", "systematic_coordination", "artificial_limitation")}

    alert_commentary = (
        "Alert generated due to " + "; ".join(alert_reasons) + ". "
        + (f"High-risk indicators: {', '.join(f'{k}={v}' for k,v in high_states.items())}" if high_states else "")
    ) if alert else "No alert: compliant and low model risk."

    lineage = {
        "case": case_name,
        "timestamp": datetime.utcnow().isoformat(),
        "raw_input_summary": {
            "plant_data": {k: plant_data.get(k) for k in ("unit_id", "fuel_type", "capacity_mw", "heat_rate", "efficiency")},
            "offers_count": len(offers),
            "market_data": {k: market_data.get(k) for k in ("system_load_mw", "load_factor", "market_tightness", "transmission_constraints")},
            "fuel_prices": fuel_prices,
        },
        "evidence": {
            "numeric": numeric_evidence,
            "states": string_evidence,
        },
        "risk_assessment": {
            "probabilities": risk_probs,
            "max_state": max_state,
            "confidence": confidence,
        },
        "arera_compliance": {
            "status": getattr(compliance_report, 'compliance_status', 'unknown'),
            "violations": [
                {
                    "type": v.violation_type,
                    "severity": v.severity,
                    "description": v.description,
                    "evidence": v.evidence,
                    "statistical_significance": v.statistical_significance,
                    "economic_significance": v.economic_significance,
                    "reference": v.regulatory_reference,
                }
                for v in getattr(compliance_report, 'violations', [])
            ],
            "confidence_level": getattr(compliance_report, 'confidence_level', 0.0),
        },
        "alert": {
            "triggered": alert,
            "commentary": alert_commentary,
        },
    }

    return lineage

def main() -> None:
    os.makedirs('outputs', exist_ok=True)

    cases: Tuple[Tuple[str, Dict[str, Any], bool], ...] = (
        ("compliant_gas_plant", get_compliant_gas_plant_data(), False),
        ("flagged_gas_plant", get_flagged_gas_plant_data(), True),
    )

    results = {}
    for name, data, is_flagged in cases:
        lineage = run_case(name, data, is_flagged)
        results[name] = lineage
        out_path = os.path.join('outputs', f'ew_lineage_{name}.json')
        with open(out_path, 'w') as f:
            json.dump(lineage, f, indent=2)
        print(f"Written: {out_path}")

    print(json.dumps({"summary": {k: {"alert": v["alert"], "arera_status": v["arera_compliance"]["status"], "risk": v["risk_assessment"]["max_state"], "confidence": v["risk_assessment"]["confidence"]} for k, v in results.items()}}, indent=2))

if __name__ == '__main__':
    main()