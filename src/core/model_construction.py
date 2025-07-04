"""
Model Construction for Kor.ai Bayesian Risk Engine
Assembles Bayesian Networks for specific use cases (e.g., Insider Dealing) using the node library and pgmpy.
"""

from pgmpy.models import BayesianNetwork
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination
from .node_library import EvidenceNode, RiskFactorNode, OutcomeNode, CommsIntentNode, VarianceTunedIndicatorNode, normalize_cpt

# Example: Build the Insider Dealing Bayesian Network

def build_insider_dealing_bn():
    # Define nodes (names and states should match your MVP model design)
    trade_pattern = EvidenceNode("trade_pattern", ["normal", "suspicious"], description="Trade pattern evidence")
    comms_intent = CommsIntentNode("comms_intent", description="Comms intent evidence")
    pnl_drift = VarianceTunedIndicatorNode("pnl_drift", description="PnL drift indicator")
    risk_factor = RiskFactorNode("risk_factor", ["low", "medium", "high"], description="Latent risk factor")
    insider_dealing = OutcomeNode("insider_dealing", ["no", "yes"], description="Insider dealing outcome")

    # Define network structure (edges)
    edges = [
        ("trade_pattern", "risk_factor"),
        ("comms_intent", "risk_factor"),
        ("pnl_drift", "risk_factor"),
        ("risk_factor", "insider_dealing"),
    ]

    model = BayesianNetwork(edges)

    # Define CPTs (placeholder values, replace with real ones from your model design)
    cpd_trade_pattern = TabularCPD(variable="trade_pattern", variable_card=2, values=[[0.95], [0.05]])
    cpd_comms_intent = TabularCPD(variable="comms_intent", variable_card=3, values=[[0.8], [0.15], [0.05]])
    cpd_pnl_drift = TabularCPD(variable="pnl_drift", variable_card=2, values=[[0.9], [0.1]])

    # risk_factor: P(risk_factor | trade_pattern, comms_intent, pnl_drift)
    # For simplicity, use uniform CPT (replace with real CPT from model design)
    cpd_risk_factor = TabularCPD(
        variable="risk_factor",
        variable_card=3,
        evidence=["trade_pattern", "comms_intent", "pnl_drift"],
        evidence_card=[2, 3, 2],
        values=[[1/3]*12, [1/3]*12, [1/3]*12]
    )

    # insider_dealing: P(insider_dealing | risk_factor)
    cpd_insider_dealing = TabularCPD(
        variable="insider_dealing",
        variable_card=2,
        evidence=["risk_factor"],
        evidence_card=[3],
        values=[[0.99, 0.7, 0.2], [0.01, 0.3, 0.8]]
    )

    # Add CPDs to the model
    model.add_cpds(
        cpd_trade_pattern,
        cpd_comms_intent,
        cpd_pnl_drift,
        cpd_risk_factor,
        cpd_insider_dealing
    )

    # Validate the model
    assert model.check_model(), "Bayesian Network structure or CPDs are invalid."

    return model

# Example usage:
# model = build_insider_dealing_bn()
# infer = VariableElimination(model)
# result = infer.query(variables=["insider_dealing"], evidence={"trade_pattern": 1, "comms_intent": 2, "pnl_drift": 1})
# print(result) 