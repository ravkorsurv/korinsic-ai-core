"""
Economic Withholding Detection Model Package.

This package contains the Bayesian network model for detecting
economic withholding in power markets using ARERA-style probabilistic analysis.

Economic withholding involves generators offering capacity at prices
significantly above marginal costs to manipulate market prices.
This model detects such patterns through counterfactual "what-if" simulation
and statistical analysis of cost-offer relationships.
"""

# Wrap the imports in a try-except block to handle potential import failures gracefully
try:
    from .config import EconomicWithholdingConfig
    from .model import EconomicWithholdingModel
    from .nodes import EconomicWithholdingNodes
    from .scenario_engine import ScenarioSimulationEngine
    from .cost_curve_analyzer import CostCurveAnalyzer
    from .arera_compliance import ARERAComplianceEngine
except ImportError as e:
    raise ImportError(f"Failed to import required economic withholding modules: {str(e)}")

__all__ = [
    "EconomicWithholdingModel", 
    "EconomicWithholdingNodes", 
    "EconomicWithholdingConfig",
    "ScenarioSimulationEngine",
    "CostCurveAnalyzer", 
    "ARERAComplianceEngine"
]