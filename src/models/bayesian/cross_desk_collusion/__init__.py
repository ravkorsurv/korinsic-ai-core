"""
Cross-Desk Collusion Detection Model Package.

This package provides a comprehensive Bayesian network model for detecting
collusive behavior between trading desks or entities in financial institutions.

Cross-desk collusion involves coordination between different trading desks or
departments to manipulate markets or gain unfair advantages. This model detects
such patterns through analysis of:
- Trading coordination patterns across desks
- Information sharing indicators
- Synchronized trading activities
- Communication and meeting correlation analysis

Design Rationale:
- Multi-entity relationship modeling using Bayesian networks
- Temporal correlation analysis for coordinated activities
- Risk scoring based on coordination strength and market impact
- Integration with organizational hierarchy and access control data

Version: 1.0.0 - Initial cross-desk collusion detection capabilities
Compliance: Designed for regulatory oversight of internal trading coordination
"""

# Wrap the imports in a try-except block to handle potential import failures gracefully
try:
    from .config import CrossDeskCollusionConfig
    from .model import CrossDeskCollusionModel
    from .nodes import CrossDeskCollusionNodes
except ImportError as e:
    raise ImportError(f"Failed to import required cross-desk collusion modules: {str(e)}")

__all__ = [
    "CrossDeskCollusionModel",
    "CrossDeskCollusionNodes",
    "CrossDeskCollusionConfig",
]
