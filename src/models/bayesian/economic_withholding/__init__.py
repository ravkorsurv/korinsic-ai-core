"""
Economic Withholding Detection Model Package.

This package contains the Bayesian network model for detecting
economic withholding in power markets using ARERA-style probabilistic analysis.

Economic withholding involves generators offering capacity at prices
significantly above marginal costs to manipulate market prices.
This model detects such patterns through counterfactual "what-if" simulation
and statistical analysis of cost-offer relationships.

Key Interfaces:
- EconomicWithholdingModel: Main entry point for withholding detection
- EconomicWithholdingConfig: Configuration interface for model parameters
- ScenarioSimulationEngine: Counterfactual analysis engine
- ARERAComplianceEngine: Regulatory compliance assessment

Dependencies:
- numpy>=1.20
- scipy>=1.7
- pandas>=1.3 (optional, for data processing)
- pgmpy>=0.1.19 (optional, for Bayesian networks)

Version: 1.0.0
"""

# Import modules with granular error handling
import logging
logger = logging.getLogger(__name__)

# Define modules with their criticality
MODULES_TO_IMPORT = {
    'config': {'module': 'EconomicWithholdingConfig', 'critical': True},
    'model': {'module': 'EconomicWithholdingModel', 'critical': True},
    'nodes': {'module': 'EconomicWithholdingNodes', 'critical': False},
    'scenario_engine': {'module': 'ScenarioSimulationEngine', 'critical': False},
    'cost_curve_analyzer': {'module': 'CostCurveAnalyzer', 'critical': False},
    'arera_compliance': {'module': 'ARERAComplianceEngine', 'critical': False},
}

modules = {}
import_errors = []
critical_failures = []

for module_name, module_info in MODULES_TO_IMPORT.items():
    try:
        import importlib
        module = importlib.import_module(f'.{module_name}', package=__name__)
        modules[module_name] = getattr(module, module_info['module'])
    except ImportError as e:
        modules[module_name] = None
        error_msg = f"{module_name}: {str(e)}"
        import_errors.append(error_msg)
        
        if module_info['critical']:
            critical_failures.append(error_msg)

# Make successfully imported modules available
EconomicWithholdingConfig = modules.get('config')
EconomicWithholdingModel = modules.get('model')
EconomicWithholdingNodes = modules.get('nodes')
ScenarioSimulationEngine = modules.get('scenario_engine')
CostCurveAnalyzer = modules.get('cost_curve_analyzer')
ARERAComplianceEngine = modules.get('arera_compliance')

# Raise error only if critical modules failed to import
if critical_failures:
    raise ImportError(f"Failed to import critical economic withholding modules: {'; '.join(critical_failures)}")

# Log non-critical import failures
if import_errors and not critical_failures:
    logger.warning(f"Some economic withholding modules could not be imported: {'; '.join(import_errors)}")

__all__ = [
    "EconomicWithholdingModel", 
    "EconomicWithholdingNodes", 
    "EconomicWithholdingConfig",
    "ScenarioSimulationEngine",
    "CostCurveAnalyzer", 
    "ARERAComplianceEngine"
]