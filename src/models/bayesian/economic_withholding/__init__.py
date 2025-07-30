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
modules = {}
import_errors = []

try:
    from .config import EconomicWithholdingConfig
    modules['config'] = EconomicWithholdingConfig
except ImportError as e:
    modules['config'] = None
    import_errors.append(f"config: {str(e)}")

try:
    from .model import EconomicWithholdingModel
    modules['model'] = EconomicWithholdingModel
except ImportError as e:
    modules['model'] = None
    import_errors.append(f"model: {str(e)}")

try:
    from .nodes import EconomicWithholdingNodes
    modules['nodes'] = EconomicWithholdingNodes
except ImportError as e:
    modules['nodes'] = None
    import_errors.append(f"nodes: {str(e)}")

try:
    from .scenario_engine import ScenarioSimulationEngine
    modules['scenario_engine'] = ScenarioSimulationEngine
except ImportError as e:
    modules['scenario_engine'] = None
    import_errors.append(f"scenario_engine: {str(e)}")

try:
    from .cost_curve_analyzer import CostCurveAnalyzer
    modules['cost_curve_analyzer'] = CostCurveAnalyzer
except ImportError as e:
    modules['cost_curve_analyzer'] = None
    import_errors.append(f"cost_curve_analyzer: {str(e)}")

try:
    from .arera_compliance import ARERAComplianceEngine
    modules['arera_compliance'] = ARERAComplianceEngine
except ImportError as e:
    modules['arera_compliance'] = None
    import_errors.append(f"arera_compliance: {str(e)}")

# Make successfully imported modules available
EconomicWithholdingConfig = modules.get('config')
EconomicWithholdingModel = modules.get('model')
EconomicWithholdingNodes = modules.get('nodes')
ScenarioSimulationEngine = modules.get('scenario_engine')
CostCurveAnalyzer = modules.get('cost_curve_analyzer')
ARERAComplianceEngine = modules.get('arera_compliance')

# Raise error only if critical modules failed to import
critical_modules = ['config', 'model']
critical_failures = [error for error in import_errors if any(critical in error for critical in critical_modules)]

if critical_failures:
    raise ImportError(f"Failed to import critical economic withholding modules: {'; '.join(critical_failures)}")

# Warn about non-critical import failures
if import_errors and not critical_failures:
    import warnings
    warnings.warn(f"Some economic withholding modules could not be imported: {'; '.join(import_errors)}")

__all__ = [
    "EconomicWithholdingModel", 
    "EconomicWithholdingNodes", 
    "EconomicWithholdingConfig",
    "ScenarioSimulationEngine",
    "CostCurveAnalyzer", 
    "ARERAComplianceEngine"
]