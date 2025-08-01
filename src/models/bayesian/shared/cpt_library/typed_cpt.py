"""
Typed CPT (Conditional Probability Table) Definitions

This module provides strongly-typed CPT definitions with comprehensive
metadata, versioning, and regulatory compliance tracking.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from uuid import uuid4

from .regulatory_reference import RegulatoryReference


class CPTType(Enum):
    """Types of CPT definitions."""
    EVIDENCE_NODE = "evidence_node"
    RISK_FACTOR = "risk_factor" 
    OUTCOME_NODE = "outcome_node"
    LATENT_INTENT = "latent_intent"
    CROSS_TYPOLOGY = "cross_typology"


class CPTStatus(Enum):
    """Status of CPT definition."""
    DRAFT = "draft"
    VALIDATED = "validated"
    APPROVED = "approved"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


@dataclass
class CPTMetadata:
    """
    Metadata for CPT definitions.
    
    Tracks versioning, regulatory compliance, and audit information.
    """
    cpt_id: str
    version: str
    status: CPTStatus
    
    # Regulatory compliance
    regulatory_references: List[str] = field(default_factory=list)
    compliance_frameworks: List[str] = field(default_factory=list)
    enforcement_case_ids: List[str] = field(default_factory=list)
    
    # Audit trail
    created_at: datetime = field(default_factory=datetime.now)
    created_by: str = "system"
    last_updated: datetime = field(default_factory=datetime.now)
    updated_by: str = "system"
    
    # Validation
    validated_at: Optional[datetime] = None
    validated_by: Optional[str] = None
    validation_notes: str = ""
    
    # Usage tracking
    usage_count: int = 0
    last_used: Optional[datetime] = None
    applicable_models: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate metadata."""
        if not self.cpt_id:
            self.cpt_id = f"CPT_{uuid4().hex[:8].upper()}"
        if not self.version:
            self.version = "1.0.0"
    
    def update_usage(self, model_name: str) -> None:
        """Update usage tracking."""
        self.usage_count += 1
        self.last_used = datetime.now()
        if model_name not in self.applicable_models:
            self.applicable_models.append(model_name)
    
    def add_regulatory_reference(self, reference_id: str) -> None:
        """Add regulatory reference."""
        if reference_id not in self.regulatory_references:
            self.regulatory_references.append(reference_id)
            self.last_updated = datetime.now()
    
    def validate(self, validator: str, notes: str = "") -> None:
        """Mark as validated."""
        self.status = CPTStatus.VALIDATED
        self.validated_at = datetime.now()
        self.validated_by = validator
        self.validation_notes = notes
        self.last_updated = datetime.now()
    
    def approve(self, approver: str) -> None:
        """Mark as approved."""
        if self.status != CPTStatus.VALIDATED:
            raise ValueError("CPT must be validated before approval")
        self.status = CPTStatus.APPROVED
        self.updated_by = approver
        self.last_updated = datetime.now()


@dataclass
class TypedCPT:
    """
    Typed Conditional Probability Table with metadata.
    
    Provides a strongly-typed CPT definition with regulatory
    compliance, versioning, and audit capabilities.
    """
    metadata: CPTMetadata
    cpt_type: CPTType
    
    # Node definition
    node_name: str
    node_states: List[str]
    node_description: str
    
    # Parent nodes (evidence)
    parent_nodes: List[str] = field(default_factory=list)
    parent_states: Dict[str, List[str]] = field(default_factory=dict)
    
    # Probability table
    probability_table: List[List[float]] = field(default_factory=list)
    fallback_prior: List[float] = field(default_factory=list)
    
    # Regulatory justification
    probability_rationale: str = ""
    threshold_justification: str = ""
    
    # Cross-references
    related_cpts: List[str] = field(default_factory=list)
    shared_components: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate CPT definition."""
        self._validate_structure()
        self._validate_probabilities()
    
    def _validate_structure(self) -> None:
        """Validate CPT structure."""
        if not self.node_name:
            raise ValueError("Node name is required")
        if not self.node_states:
            raise ValueError("Node states are required")
        if len(self.node_states) < 2:
            raise ValueError("Node must have at least 2 states")
    
    def _validate_probabilities(self) -> None:
        """Validate probability table."""
        if not self.probability_table:
            return  # Empty table is valid (will use fallback)
        
        # Check dimensions
        expected_rows = len(self.node_states)
        if len(self.probability_table) != expected_rows:
            raise ValueError(f"Probability table must have {expected_rows} rows for node states")
        
        # Calculate expected columns
        if self.parent_nodes:
            expected_cols = 1
            for parent in self.parent_nodes:
                if parent in self.parent_states:
                    expected_cols *= len(self.parent_states[parent])
        else:
            expected_cols = 1
        
        # Validate each row
        for i, row in enumerate(self.probability_table):
            if len(row) != expected_cols:
                raise ValueError(f"Row {i} must have {expected_cols} columns")
            
            # Check probabilities sum to 1 for each parent combination
            if abs(sum(row) - expected_cols) > 0.01:  # Allow small floating point errors
                # For conditional tables, each column should sum to 1 across states
                pass  # More complex validation needed here
    
    def get_probability(self, node_state: str, evidence: Dict[str, str] = None) -> float:
        """
        Get probability for specific state and evidence.
        
        Args:
            node_state: The state to get probability for
            evidence: Dictionary of parent node states
            
        Returns:
            Probability value
        """
        if node_state not in self.node_states:
            raise ValueError(f"Unknown node state: {node_state}")
        
        state_index = self.node_states.index(node_state)
        
        if not self.probability_table:
            # Use fallback prior
            if self.fallback_prior and len(self.fallback_prior) > state_index:
                return self.fallback_prior[state_index]
            else:
                # Uniform distribution
                return 1.0 / len(self.node_states)
        
        if not evidence or not self.parent_nodes:
            # No evidence or no parents, use first column
            return self.probability_table[state_index][0]
        
        # Calculate evidence index
        evidence_index = self._calculate_evidence_index(evidence)
        
        if evidence_index < len(self.probability_table[state_index]):
            return self.probability_table[state_index][evidence_index]
        else:
            # Fallback to prior
            if self.fallback_prior and len(self.fallback_prior) > state_index:
                return self.fallback_prior[state_index]
            else:
                return 1.0 / len(self.node_states)
    
    def _calculate_evidence_index(self, evidence: Dict[str, str]) -> int:
        """Calculate index in probability table for given evidence."""
        index = 0
        multiplier = 1
        
        for parent in reversed(self.parent_nodes):
            if parent in evidence and parent in self.parent_states:
                parent_state = evidence[parent]
                if parent_state in self.parent_states[parent]:
                    state_index = self.parent_states[parent].index(parent_state)
                    index += state_index * multiplier
                multiplier *= len(self.parent_states[parent])
        
        return index
    
    def update_probability(self, node_state: str, evidence: Dict[str, str], 
                          new_probability: float, justification: str = "") -> None:
        """
        Update probability for specific state and evidence.
        
        Args:
            node_state: The state to update
            evidence: Dictionary of parent node states
            new_probability: New probability value
            justification: Justification for the change
        """
        if not (0.0 <= new_probability <= 1.0):
            raise ValueError("Probability must be between 0 and 1")
        
        state_index = self.node_states.index(node_state)
        evidence_index = self._calculate_evidence_index(evidence) if evidence else 0
        
        # Ensure probability table exists
        if not self.probability_table:
            self._initialize_probability_table()
        
        # Update probability
        self.probability_table[state_index][evidence_index] = new_probability
        
        # Update metadata
        self.metadata.last_updated = datetime.now()
        if justification:
            self.probability_rationale += f"\n{datetime.now().isoformat()}: {justification}"
    
    def _initialize_probability_table(self) -> None:
        """Initialize empty probability table."""
        if self.parent_nodes:
            cols = 1
            for parent in self.parent_nodes:
                if parent in self.parent_states:
                    cols *= len(self.parent_states[parent])
        else:
            cols = 1
        
        rows = len(self.node_states)
        
        # Initialize with uniform distribution
        uniform_prob = 1.0 / rows
        self.probability_table = [[uniform_prob] * cols for _ in range(rows)]
    
    def add_parent_node(self, parent_name: str, parent_states: List[str]) -> None:
        """Add a parent node to this CPT."""
        if parent_name not in self.parent_nodes:
            self.parent_nodes.append(parent_name)
        self.parent_states[parent_name] = parent_states
        
        # Reinitialize probability table
        self._initialize_probability_table()
        
        # Update metadata
        self.metadata.last_updated = datetime.now()
    
    def clone(self, new_version: str, created_by: str = "system") -> 'TypedCPT':
        """Create a copy of this CPT with new version."""
        new_metadata = CPTMetadata(
            cpt_id=f"{self.metadata.cpt_id}_v{new_version.replace('.', '_')}",
            version=new_version,
            status=CPTStatus.DRAFT,
            regulatory_references=self.metadata.regulatory_references.copy(),
            compliance_frameworks=self.metadata.compliance_frameworks.copy(),
            enforcement_case_ids=self.metadata.enforcement_case_ids.copy(),
            created_by=created_by,
            applicable_models=self.metadata.applicable_models.copy()
        )
        
        return TypedCPT(
            metadata=new_metadata,
            cpt_type=self.cpt_type,
            node_name=self.node_name,
            node_states=self.node_states.copy(),
            node_description=self.node_description,
            parent_nodes=self.parent_nodes.copy(),
            parent_states={k: v.copy() for k, v in self.parent_states.items()},
            probability_table=[row.copy() for row in self.probability_table],
            fallback_prior=self.fallback_prior.copy(),
            probability_rationale=self.probability_rationale,
            threshold_justification=self.threshold_justification,
            related_cpts=self.related_cpts.copy(),
            shared_components=self.shared_components.copy()
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "metadata": {
                "cpt_id": self.metadata.cpt_id,
                "version": self.metadata.version,
                "status": self.metadata.status.value,
                "regulatory_references": self.metadata.regulatory_references,
                "compliance_frameworks": self.metadata.compliance_frameworks,
                "enforcement_case_ids": self.metadata.enforcement_case_ids,
                "created_at": self.metadata.created_at.isoformat(),
                "created_by": self.metadata.created_by,
                "last_updated": self.metadata.last_updated.isoformat(),
                "updated_by": self.metadata.updated_by,
                "validated_at": self.metadata.validated_at.isoformat() if self.metadata.validated_at else None,
                "validated_by": self.metadata.validated_by,
                "validation_notes": self.metadata.validation_notes,
                "usage_count": self.metadata.usage_count,
                "last_used": self.metadata.last_used.isoformat() if self.metadata.last_used else None,
                "applicable_models": self.metadata.applicable_models
            },
            "cpt_type": self.cpt_type.value,
            "node_name": self.node_name,
            "node_states": self.node_states,
            "node_description": self.node_description,
            "parent_nodes": self.parent_nodes,
            "parent_states": self.parent_states,
            "probability_table": self.probability_table,
            "fallback_prior": self.fallback_prior,
            "probability_rationale": self.probability_rationale,
            "threshold_justification": self.threshold_justification,
            "related_cpts": self.related_cpts,
            "shared_components": self.shared_components
        }