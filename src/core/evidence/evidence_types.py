"""
Evidence Types and Cross-Reference Management for Regulatory Explainability

This module provides proper enum implementations and optimized cross-reference
handling for evidence chains in the regulatory explainability system.
"""

from enum import Enum, auto
from typing import Dict, List, Any, Set, Optional
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)

class EvidenceType(Enum):
    """Proper enum for evidence types"""
    TRADING_PATTERN = "trading_pattern"
    TIMING_ANOMALY = "timing_anomaly"
    COMMUNICATION = "communication"
    CROSS_ACCOUNT_CORRELATION = "cross_account_correlation"
    VOLUME_ANOMALY = "volume_anomaly"
    PRICE_MANIPULATION = "price_manipulation"
    ORDER_PATTERN = "order_pattern"
    MARKET_IMPACT = "market_impact"

class RegulatoryFramework(Enum):
    """Proper enum for regulatory frameworks"""
    MAR_ARTICLE_8 = "mar_article_8"
    MAR_ARTICLE_12 = "mar_article_12"
    STOR_REQUIREMENTS = "stor_requirements"
    MIFID_II_ARTICLE_17 = "mifid_ii_article_17"
    ESMA_GUIDELINES = "esma_guidelines"
    FCA_MAR_GUIDANCE = "fca_mar_guidance"

class EvidenceSeverity(Enum):
    """Evidence severity levels"""
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
    CRITICAL = auto()

class CrossReferenceType(Enum):
    """Types of cross-references between evidence items"""
    TEMPORAL_SEQUENCE = "temporal_sequence"
    CAUSAL_RELATIONSHIP = "causal_relationship"
    CORROBORATING_EVIDENCE = "corroborating_evidence"
    PATTERN_CONTINUATION = "pattern_continuation"
    ACCOUNT_CORRELATION = "account_correlation"

@dataclass
class CrossReference:
    """Optimized cross-reference implementation using indices"""
    target_index: int
    reference_type: CrossReferenceType
    strength: float = 1.0
    description: Optional[str] = None
    
    def __post_init__(self):
        """Validate cross-reference data"""
        if not 0 <= self.strength <= 1.0:
            raise ValueError("Cross-reference strength must be between 0 and 1")
        if self.target_index < 0:
            raise ValueError("Target index must be non-negative")

@dataclass
class EvidenceItem:
    """Optimized evidence item with proper cross-reference handling"""
    sequence_id: int
    evidence_type: EvidenceType
    timestamp: str
    account_id: str
    strength: float
    reliability: float
    description: str
    regulatory_frameworks: List[RegulatoryFramework]
    raw_data: Dict[str, Any]
    cross_references: List[CrossReference] = field(default_factory=list)
    severity: EvidenceSeverity = EvidenceSeverity.MEDIUM
    
    def __post_init__(self):
        """Validate evidence item data"""
        if not 0 <= self.strength <= 1.0:
            raise ValueError("Evidence strength must be between 0 and 1")
        if not 0 <= self.reliability <= 1.0:
            raise ValueError("Evidence reliability must be between 0 and 1")
        if self.sequence_id < 1:
            raise ValueError("Sequence ID must be positive")
    
    def add_cross_reference(
        self, 
        target_index: int, 
        reference_type: CrossReferenceType,
        strength: float = 1.0,
        description: Optional[str] = None
    ) -> None:
        """Add a cross-reference to another evidence item"""
        cross_ref = CrossReference(
            target_index=target_index,
            reference_type=reference_type,
            strength=strength,
            description=description
        )
        self.cross_references.append(cross_ref)
    
    def get_cross_reference_indices(self) -> List[int]:
        """Get list of cross-referenced evidence indices (O(1) lookup)"""
        return [ref.target_index for ref in self.cross_references]
    
    def get_strong_cross_references(self, threshold: float = 0.7) -> List[CrossReference]:
        """Get cross-references above strength threshold"""
        return [ref for ref in self.cross_references if ref.strength >= threshold]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "sequence_id": self.sequence_id,
            "evidence_type": self.evidence_type.value,
            "timestamp": self.timestamp,
            "account_id": self.account_id,
            "strength": self.strength,
            "reliability": self.reliability,
            "description": self.description,
            "regulatory_frameworks": [fw.value for fw in self.regulatory_frameworks],
            "raw_data": self.raw_data,
            "cross_references": [
                {
                    "target_index": ref.target_index,
                    "reference_type": ref.reference_type.value,
                    "strength": ref.strength,
                    "description": ref.description
                }
                for ref in self.cross_references
            ],
            "severity": self.severity.name
        }

class EvidenceChainBuilder:
    """Optimized evidence chain builder with proper cross-reference management"""
    
    def __init__(self):
        self.evidence_items: List[EvidenceItem] = []
        self.index_map: Dict[int, int] = {}  # sequence_id -> list_index mapping
        
    def add_evidence_item(self, evidence_item: EvidenceItem) -> int:
        """
        Add evidence item to chain and return its list index.
        
        Args:
            evidence_item: Evidence item to add
            
        Returns:
            List index of the added item
        """
        list_index = len(self.evidence_items)
        self.evidence_items.append(evidence_item)
        self.index_map[evidence_item.sequence_id] = list_index
        
        logger.debug(f"Added evidence item {evidence_item.sequence_id} at index {list_index}")
        return list_index
    
    def add_cross_reference(
        self,
        source_sequence_id: int,
        target_sequence_id: int,
        reference_type: CrossReferenceType,
        strength: float = 1.0,
        description: Optional[str] = None
    ) -> bool:
        """
        Add cross-reference between evidence items using sequence IDs.
        
        Args:
            source_sequence_id: Source evidence sequence ID
            target_sequence_id: Target evidence sequence ID
            reference_type: Type of cross-reference
            strength: Reference strength (0-1)
            description: Optional description
            
        Returns:
            True if reference was added successfully
        """
        try:
            source_index = self.index_map.get(source_sequence_id)
            target_index = self.index_map.get(target_sequence_id)
            
            if source_index is None or target_index is None:
                logger.warning(f"Cannot add cross-reference: source {source_sequence_id} or target {target_sequence_id} not found")
                return False
            
            # Add cross-reference using list indices (O(1) lookup)
            self.evidence_items[source_index].add_cross_reference(
                target_index=target_index,
                reference_type=reference_type,
                strength=strength,
                description=description
            )
            
            logger.debug(f"Added cross-reference from {source_sequence_id} to {target_sequence_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding cross-reference: {e}")
            return False
    
    def get_evidence_by_sequence_id(self, sequence_id: int) -> Optional[EvidenceItem]:
        """Get evidence item by sequence ID (O(1) lookup)"""
        index = self.index_map.get(sequence_id)
        if index is not None:
            return self.evidence_items[index]
        return None
    
    def get_evidence_by_index(self, index: int) -> Optional[EvidenceItem]:
        """Get evidence item by list index"""
        if 0 <= index < len(self.evidence_items):
            return self.evidence_items[index]
        return None
    
    def get_cross_referenced_evidence(self, sequence_id: int) -> List[EvidenceItem]:
        """Get all evidence items cross-referenced by the given item"""
        evidence_item = self.get_evidence_by_sequence_id(sequence_id)
        if not evidence_item:
            return []
        
        referenced_items = []
        for ref in evidence_item.cross_references:
            referenced_item = self.get_evidence_by_index(ref.target_index)
            if referenced_item:
                referenced_items.append(referenced_item)
        
        return referenced_items
    
    def build_cross_reference_graph(self) -> Dict[int, Set[int]]:
        """Build cross-reference graph for analysis (O(n) complexity)"""
        graph = {}
        
        for item in self.evidence_items:
            source_id = item.sequence_id
            target_indices = item.get_cross_reference_indices()
            
            # Convert indices back to sequence IDs for graph representation
            target_ids = set()
            for idx in target_indices:
                if 0 <= idx < len(self.evidence_items):
                    target_ids.add(self.evidence_items[idx].sequence_id)
            
            graph[source_id] = target_ids
        
        return graph
    
    def validate_cross_references(self) -> List[str]:
        """Validate all cross-references in the chain"""
        validation_errors = []
        
        for item in self.evidence_items:
            for ref in item.cross_references:
                # Check if target index is valid
                if ref.target_index >= len(self.evidence_items):
                    validation_errors.append(
                        f"Evidence {item.sequence_id} references invalid index {ref.target_index}"
                    )
                
                # Check for self-references
                source_index = self.index_map.get(item.sequence_id)
                if source_index == ref.target_index:
                    validation_errors.append(
                        f"Evidence {item.sequence_id} contains self-reference"
                    )
        
        return validation_errors
    
    def get_evidence_chain(self) -> List[EvidenceItem]:
        """Get the complete evidence chain"""
        return self.evidence_items.copy()
    
    def get_chain_statistics(self) -> Dict[str, Any]:
        """Get statistics about the evidence chain"""
        if not self.evidence_items:
            return {"total_items": 0}
        
        total_cross_refs = sum(len(item.cross_references) for item in self.evidence_items)
        evidence_types = [item.evidence_type for item in self.evidence_items]
        type_counts = {et.value: evidence_types.count(et) for et in EvidenceType}
        
        strengths = [item.strength for item in self.evidence_items]
        reliabilities = [item.reliability for item in self.evidence_items]
        
        return {
            "total_items": len(self.evidence_items),
            "total_cross_references": total_cross_refs,
            "average_cross_references_per_item": total_cross_refs / len(self.evidence_items),
            "evidence_type_distribution": type_counts,
            "average_strength": sum(strengths) / len(strengths),
            "average_reliability": sum(reliabilities) / len(reliabilities),
            "min_strength": min(strengths),
            "max_strength": max(strengths),
            "validation_errors": len(self.validate_cross_references())
        }

# Factory function for creating evidence items
def create_evidence_item(
    sequence_id: int,
    evidence_type: EvidenceType,
    timestamp: str,
    account_id: str,
    strength: float,
    reliability: float,
    description: str,
    regulatory_frameworks: List[RegulatoryFramework],
    raw_data: Dict[str, Any],
    severity: EvidenceSeverity = EvidenceSeverity.MEDIUM
) -> EvidenceItem:
    """Factory function to create evidence items with validation"""
    return EvidenceItem(
        sequence_id=sequence_id,
        evidence_type=evidence_type,
        timestamp=timestamp,
        account_id=account_id,
        strength=strength,
        reliability=reliability,
        description=description,
        regulatory_frameworks=regulatory_frameworks,
        raw_data=raw_data,
        severity=severity
    )

# Constants for regulatory compliance
class RegulatoryConstants:
    """Constants for regulatory compliance thresholds"""
    
    # Evidence strength thresholds
    MIN_EVIDENCE_STRENGTH = 0.1
    ANALYST_THRESHOLD = 0.5
    COMPLIANCE_THRESHOLD = 0.7
    REGULATOR_THRESHOLD = 0.8
    
    # Framework-specific thresholds
    FRAMEWORK_THRESHOLDS = {
        RegulatoryFramework.MAR_ARTICLE_8: 0.7,
        RegulatoryFramework.MAR_ARTICLE_12: 0.7,
        RegulatoryFramework.STOR_REQUIREMENTS: 0.6,
        RegulatoryFramework.MIFID_II_ARTICLE_17: 0.7,
        RegulatoryFramework.ESMA_GUIDELINES: 0.6
    }
    
    # Cross-reference strength thresholds
    WEAK_CROSS_REFERENCE = 0.3
    MODERATE_CROSS_REFERENCE = 0.6
    STRONG_CROSS_REFERENCE = 0.8