"""
Centralized CPT (Conditional Probability Table) Library
This module provides a centralized, versioned, and regulatory-compliant
CPT library for all Bayesian risk models. It addresses the gaps identified
in the original analysis by providing:
1. Reusable CPT definitions by typology
2. Enforcement case references and regulatory justifications
3. Versioning and change management
4. Cross-typology shared components
5. Audit trails and compliance documentation
Key Components:
- CPTLibrary: Main library management class
- TypedCPT: Typed CPT definitions with metadata
- RegulatoryReference: Enforcement case and regulatory citations
- CPTVersionManager: Version control and change tracking
"""
from .library import CPTLibrary
from .typed_cpt import TypedCPT, CPTMetadata, CPTType, CPTStatus
from .regulatory_reference import RegulatoryReference, EnforcementCase, RegulatoryFramework, EnforcementLevel
from .version_manager import CPTVersionManager
from .typology_templates import TypologyTemplateManager
__version__ = "1.0.0"
__author__ = "Korinsic AI"
__description__ = "Centralized CPT Library with Regulatory Compliance"
__all__ = [
    "CPTLibrary",
    "TypedCPT",
    "CPTMetadata",
    "CPTType",
    "CPTStatus",
    "RegulatoryReference",
    "EnforcementCase",
    "RegulatoryFramework",
    "EnforcementLevel",
    "CPTVersionManager",
    "TypologyTemplateManager"
]
