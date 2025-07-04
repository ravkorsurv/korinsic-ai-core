"""
Model Construction for Kor.ai Bayesian Risk Engine
Assembles Bayesian Networks for specific use cases (e.g., Insider Dealing) using the node library and pgmpy.
"""

from pgmpy.models import BayesianNetwork
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination
from .node_library import (
    EvidenceNode, RiskFactorNode, OutcomeNode, CommsIntentNode, VarianceTunedIndicatorNode,
    LatentIntentNode, ProfitMotivationNode, AccessPatternNode, OrderBehaviorNode, CommsMetadataNode,
    normalize_cpt
)

def build_insider_dealing_bn_with_latent_intent():
    """
    Build Insider Dealing Bayesian Network with latent intent modeling.
    This implements the Kor.ai approach of hidden causality through latent nodes.
    """
    # Define evidence nodes (observable variables)
    trade_pattern = EvidenceNode("trade_pattern", ["normal", "suspicious"], description="Trade pattern evidence")
    comms_intent = CommsIntentNode("comms_intent", description="Comms intent evidence")
    pnl_drift = VarianceTunedIndicatorNode("pnl_drift", description="PnL drift indicator")
    
    # NEW: Converging evidence paths for latent intent inference
    profit_motivation = ProfitMotivationNode("profit_motivation", description="Profit motivation evidence")
    access_pattern = AccessPatternNode("access_pattern", description="Access pattern evidence")
    order_behavior = OrderBehaviorNode("order_behavior", description="Order behavior evidence")
    comms_metadata = CommsMetadataNode("comms_metadata", description="Communications metadata")
    
    # NEW: Latent intent node (unobservable core abusive intent)
    latent_intent = LatentIntentNode("latent_intent", description="Latent intent to manipulate")
    
    # Intermediate risk factor
    risk_factor = RiskFactorNode("risk_factor", ["low", "medium", "high"], description="Latent risk factor")
    
    # Outcome node
    insider_dealing = OutcomeNode("insider_dealing", ["no", "yes"], description="Insider dealing outcome")

    # Define network structure with latent intent
    edges = [
        # Evidence paths converging on latent intent
        ("profit_motivation", "latent_intent"),
        ("access_pattern", "latent_intent"),
        ("order_behavior", "latent_intent"),
        ("comms_metadata", "latent_intent"),
        
        # Traditional evidence paths
        ("trade_pattern", "risk_factor"),
        ("comms_intent", "risk_factor"),
        ("pnl_drift", "risk_factor"),
        
        # Latent intent influences risk factor
        ("latent_intent", "risk_factor"),
        
        # Risk factor influences outcome
        ("risk_factor", "insider_dealing"),
    ]

    model = BayesianNetwork(edges, latents={"latent_intent"})

    # Define CPTs for evidence nodes
    cpd_trade_pattern = TabularCPD(variable="trade_pattern", variable_card=2, values=[[0.95], [0.05]])
    cpd_comms_intent = TabularCPD(variable="comms_intent", variable_card=3, values=[[0.8], [0.15], [0.05]])
    cpd_pnl_drift = TabularCPD(variable="pnl_drift", variable_card=2, values=[[0.9], [0.1]])
    
    # NEW: CPTs for converging evidence paths
    cpd_profit_motivation = TabularCPD(variable="profit_motivation", variable_card=3, values=[[0.85], [0.12], [0.03]])
    cpd_access_pattern = TabularCPD(variable="access_pattern", variable_card=3, values=[[0.9], [0.08], [0.02]])
    cpd_order_behavior = TabularCPD(variable="order_behavior", variable_card=3, values=[[0.88], [0.1], [0.02]])
    cpd_comms_metadata = TabularCPD(variable="comms_metadata", variable_card=3, values=[[0.92], [0.06], [0.02]])

    # NEW: Latent intent CPT - P(latent_intent | profit_motivation, access_pattern, order_behavior, comms_metadata)
    # This models how converging evidence paths influence the unobservable intent
    # 3^4 = 81 combinations for 4 evidence variables with 3 states each
    cpd_latent_intent = TabularCPD(
        variable="latent_intent",
        variable_card=3,
        evidence=["profit_motivation", "access_pattern", "order_behavior", "comms_metadata"],
        evidence_card=[3, 3, 3, 3],
        values=[
            # P(no_intent | evidence combinations) - 81 values
            [0.95] * 81,
            
            # P(potential_intent | evidence combinations) - 81 values  
            [0.04] * 81,
            
            # P(clear_intent | evidence combinations) - 81 values
            [0.01] * 81
        ]
    )

    # Updated risk factor CPT - now includes latent intent
    # 2 * 3 * 2 * 3 = 36 combinations for evidence variables
    cpd_risk_factor = TabularCPD(
        variable="risk_factor",
        variable_card=3,
        evidence=["trade_pattern", "comms_intent", "pnl_drift", "latent_intent"],
        evidence_card=[2, 3, 2, 3],
        values=[
            # P(low_risk | evidence combinations) - 36 values
            [0.95] * 36,
            
            # P(medium_risk | evidence combinations) - 36 values
            [0.04] * 36,
            
            # P(high_risk | evidence combinations) - 36 values
            [0.01] * 36
        ]
    )

    # Outcome CPT
    cpd_insider_dealing = TabularCPD(
        variable="insider_dealing",
        variable_card=2,
        evidence=["risk_factor"],
        evidence_card=[3],
        values=[[0.99, 0.7, 0.2], [0.01, 0.3, 0.8]]
    )

    # Add all CPDs to the model
    model.add_cpds(
        cpd_trade_pattern,
        cpd_comms_intent,
        cpd_pnl_drift,
        cpd_profit_motivation,
        cpd_access_pattern,
        cpd_order_behavior,
        cpd_comms_metadata,
        cpd_latent_intent,
        cpd_risk_factor,
        cpd_insider_dealing
    )

    # Validate the model
    assert model.check_model(), "Bayesian Network structure or CPDs are invalid."

    return model

# Keep the original function for backward compatibility
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
# model = build_insider_dealing_bn_with_latent_intent()
# infer = VariableElimination(model)
# result = infer.query(variables=["insider_dealing"], evidence={"trade_pattern": 1, "comms_intent": 2, "pnl_drift": 1})
# print(result) 