"""
Main CPT Library Management System

This module provides the central CPT Library class that manages all
CPT definitions, regulatory references, and version control.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from datetime import datetime

from .typed_cpt import TypedCPT, CPTMetadata, CPTType, CPTStatus
from .regulatory_reference import RegulatoryReferenceManager, RegulatoryFramework
from .version_manager import CPTVersionManager
from .typology_templates import TypologyTemplateManager

logger = logging.getLogger(__name__)


class CPTLibrary:
    """
    Central CPT Library Management System.
    
    Provides centralized management of all CPT definitions with:
    - Regulatory compliance tracking
    - Version control and change management
    - Cross-typology sharing and reuse
    - Audit trails and compliance documentation
    """
    
    def __init__(self, library_path: Optional[Path] = None):
        """
        Initialize the CPT Library.
        
        Args:
            library_path: Path to store CPT library data
        """
        self.library_path = library_path or Path("data/cpt_library")
        self.library_path.mkdir(parents=True, exist_ok=True)
        
        # Core components
        self.cpts: Dict[str, TypedCPT] = {}
        self.regulatory_manager = RegulatoryReferenceManager()
        self.version_manager = CPTVersionManager()
        self.template_manager = TypologyTemplateManager()
        
        # Indexes for fast lookup
        self.cpts_by_typology: Dict[str, Set[str]] = {}
        self.cpts_by_node_name: Dict[str, Set[str]] = {}
        self.cpts_by_framework: Dict[str, Set[str]] = {}
        
        # Load existing data
        self._load_library()
        
        logger.info(f"CPT Library initialized with {len(self.cpts)} CPTs")
    
    def _load_library(self) -> None:
        """Load existing CPT library data."""
        try:
            # Load CPTs
            cpts_file = self.library_path / "cpts.json"
            if cpts_file.exists():
                with open(cpts_file, 'r') as f:
                    cpts_data = json.load(f)
                    self._load_cpts_from_data(cpts_data)
            
            # Load regulatory references
            refs_file = self.library_path / "regulatory_references.json"
            if refs_file.exists():
                with open(refs_file, 'r') as f:
                    refs_data = json.load(f)
                    # TODO: Load regulatory references
            
            self._rebuild_indexes()
            
        except Exception as e:
            logger.error(f"Error loading CPT library: {str(e)}")
    
    def _load_cpts_from_data(self, data: Dict[str, Any]) -> None:
        """Load CPTs from serialized data."""
        for cpt_id, cpt_data in data.get("cpts", {}).items():
            try:
                # Reconstruct metadata
                metadata_data = cpt_data["metadata"]
                metadata = CPTMetadata(
                    cpt_id=metadata_data["cpt_id"],
                    version=metadata_data["version"],
                    status=CPTStatus(metadata_data["status"]),
                    regulatory_references=metadata_data.get("regulatory_references", []),
                    compliance_frameworks=metadata_data.get("compliance_frameworks", []),
                    enforcement_case_ids=metadata_data.get("enforcement_case_ids", []),
                    created_by=metadata_data.get("created_by", "system"),
                    updated_by=metadata_data.get("updated_by", "system"),
                    validation_notes=metadata_data.get("validation_notes", ""),
                    usage_count=metadata_data.get("usage_count", 0),
                    applicable_models=metadata_data.get("applicable_models", [])
                )
                
                # Parse timestamps
                if metadata_data.get("created_at"):
                    metadata.created_at = datetime.fromisoformat(metadata_data["created_at"])
                if metadata_data.get("last_updated"):
                    metadata.last_updated = datetime.fromisoformat(metadata_data["last_updated"])
                if metadata_data.get("validated_at"):
                    metadata.validated_at = datetime.fromisoformat(metadata_data["validated_at"])
                if metadata_data.get("last_used"):
                    metadata.last_used = datetime.fromisoformat(metadata_data["last_used"])
                
                # Reconstruct CPT
                cpt = TypedCPT(
                    metadata=metadata,
                    cpt_type=CPTType(cpt_data["cpt_type"]),
                    node_name=cpt_data["node_name"],
                    node_states=cpt_data["node_states"],
                    node_description=cpt_data["node_description"],
                    parent_nodes=cpt_data.get("parent_nodes", []),
                    parent_states=cpt_data.get("parent_states", {}),
                    probability_table=cpt_data.get("probability_table", []),
                    fallback_prior=cpt_data.get("fallback_prior", []),
                    probability_rationale=cpt_data.get("probability_rationale", ""),
                    threshold_justification=cpt_data.get("threshold_justification", ""),
                    related_cpts=cpt_data.get("related_cpts", []),
                    shared_components=cpt_data.get("shared_components", [])
                )
                
                self.cpts[cpt_id] = cpt
                
            except Exception as e:
                logger.error(f"Error loading CPT {cpt_id}: {str(e)}")
    
    def _rebuild_indexes(self) -> None:
        """Rebuild lookup indexes."""
        self.cpts_by_typology.clear()
        self.cpts_by_node_name.clear()
        self.cpts_by_framework.clear()
        
        for cpt_id, cpt in self.cpts.items():
            # Index by applicable models (typologies)
            for model in cpt.metadata.applicable_models:
                if model not in self.cpts_by_typology:
                    self.cpts_by_typology[model] = set()
                self.cpts_by_typology[model].add(cpt_id)
            
            # Index by node name
            if cpt.node_name not in self.cpts_by_node_name:
                self.cpts_by_node_name[cpt.node_name] = set()
            self.cpts_by_node_name[cpt.node_name].add(cpt_id)
            
            # Index by compliance frameworks
            for framework in cpt.metadata.compliance_frameworks:
                if framework not in self.cpts_by_framework:
                    self.cpts_by_framework[framework] = set()
                self.cpts_by_framework[framework].add(cpt_id)
    
    def add_cpt(self, cpt: TypedCPT) -> str:
        """
        Add a CPT to the library.
        
        Args:
            cpt: The CPT to add
            
        Returns:
            CPT ID
        """
        cpt_id = cpt.metadata.cpt_id
        
        if cpt_id in self.cpts:
            raise ValueError(f"CPT {cpt_id} already exists")
        
        self.cpts[cpt_id] = cpt
        self._update_indexes_for_cpt(cpt_id, cpt)
        
        # Track version
        self.version_manager.track_version(cpt_id, cpt.metadata.version, "added")
        
        logger.info(f"Added CPT {cpt_id} to library")
        return cpt_id
    
    def get_cpt(self, cpt_id: str) -> Optional[TypedCPT]:
        """Get CPT by ID."""
        return self.cpts.get(cpt_id)
    
    def get_cpts_for_typology(self, typology: str) -> List[TypedCPT]:
        """Get all CPTs applicable to a specific typology."""
        cpt_ids = self.cpts_by_typology.get(typology, set())
        return [self.cpts[cpt_id] for cpt_id in cpt_ids if cpt_id in self.cpts]
    
    def get_cpts_by_node_name(self, node_name: str) -> List[TypedCPT]:
        """Get all CPTs for a specific node name."""
        cpt_ids = self.cpts_by_node_name.get(node_name, set())
        return [self.cpts[cpt_id] for cpt_id in cpt_ids if cpt_id in self.cpts]
    
    def get_cpts_by_framework(self, framework: str) -> List[TypedCPT]:
        """Get all CPTs for a regulatory framework."""
        cpt_ids = self.cpts_by_framework.get(framework, set())
        return [self.cpts[cpt_id] for cpt_id in cpt_ids if cpt_id in self.cpts]
    
    def update_cpt(self, cpt_id: str, cpt: TypedCPT) -> None:
        """
        Update an existing CPT.
        
        Args:
            cpt_id: ID of CPT to update
            cpt: Updated CPT
        """
        if cpt_id not in self.cpts:
            raise ValueError(f"CPT {cpt_id} not found")
        
        old_cpt = self.cpts[cpt_id]
        self.cpts[cpt_id] = cpt
        
        # Update indexes
        self._remove_from_indexes(cpt_id, old_cpt)
        self._update_indexes_for_cpt(cpt_id, cpt)
        
        # Track version change
        if old_cpt.metadata.version != cpt.metadata.version:
            self.version_manager.track_version(cpt_id, cpt.metadata.version, "updated")
        
        logger.info(f"Updated CPT {cpt_id}")
    
    def _update_indexes_for_cpt(self, cpt_id: str, cpt: TypedCPT) -> None:
        """Update indexes for a specific CPT."""
        # Index by applicable models
        for model in cpt.metadata.applicable_models:
            if model not in self.cpts_by_typology:
                self.cpts_by_typology[model] = set()
            self.cpts_by_typology[model].add(cpt_id)
        
        # Index by node name
        if cpt.node_name not in self.cpts_by_node_name:
            self.cpts_by_node_name[cpt.node_name] = set()
        self.cpts_by_node_name[cpt.node_name].add(cpt_id)
        
        # Index by frameworks
        for framework in cpt.metadata.compliance_frameworks:
            if framework not in self.cpts_by_framework:
                self.cpts_by_framework[framework] = set()
            self.cpts_by_framework[framework].add(cpt_id)
    
    def _remove_from_indexes(self, cpt_id: str, cpt: TypedCPT) -> None:
        """Remove CPT from indexes."""
        # Remove from typology index
        for model in cpt.metadata.applicable_models:
            if model in self.cpts_by_typology:
                self.cpts_by_typology[model].discard(cpt_id)
        
        # Remove from node name index
        if cpt.node_name in self.cpts_by_node_name:
            self.cpts_by_node_name[cpt.node_name].discard(cpt_id)
        
        # Remove from framework index
        for framework in cpt.metadata.compliance_frameworks:
            if framework in self.cpts_by_framework:
                self.cpts_by_framework[framework].discard(cpt_id)
    
    def create_cpt_from_template(self, typology: str, node_name: str, 
                                created_by: str = "system") -> TypedCPT:
        """
        Create a new CPT from a typology template.
        
        Args:
            typology: Risk typology
            node_name: Node name
            created_by: Creator identifier
            
        Returns:
            New CPT instance
        """
        template = self.template_manager.get_template(typology, node_name)
        if not template:
            raise ValueError(f"No template found for {typology}.{node_name}")
        
        # Create metadata
        metadata = CPTMetadata(
            cpt_id="",  # Will be auto-generated
            version="1.0.0",
            status=CPTStatus.DRAFT,
            created_by=created_by,
            applicable_models=[typology]
        )
        
        # Get regulatory references for typology
        reg_refs = self.regulatory_manager.get_references_for_typology(typology)
        for ref in reg_refs:
            metadata.add_regulatory_reference(ref.reference_id)
            if ref.framework.value not in metadata.compliance_frameworks:
                metadata.compliance_frameworks.append(ref.framework.value)
        
        # Create CPT from template
        cpt = TypedCPT(
            metadata=metadata,
            cpt_type=template["cpt_type"],
            node_name=node_name,
            node_states=template["node_states"],
            node_description=template["description"],
            parent_nodes=template.get("parent_nodes", []),
            parent_states=template.get("parent_states", {}),
            probability_table=template.get("probability_table", []),
            fallback_prior=template.get("fallback_prior", []),
            probability_rationale=template.get("probability_rationale", ""),
            threshold_justification=template.get("threshold_justification", "")
        )
        
        return cpt
    
    def validate_cpt(self, cpt_id: str, validator: str, notes: str = "") -> bool:
        """
        Validate a CPT.
        
        Args:
            cpt_id: CPT to validate
            validator: Validator identifier
            notes: Validation notes
            
        Returns:
            True if validation successful
        """
        cpt = self.get_cpt(cpt_id)
        if not cpt:
            raise ValueError(f"CPT {cpt_id} not found")
        
        try:
            # Validate structure and probabilities
            cpt._validate_structure()
            cpt._validate_probabilities()
            
            # Mark as validated
            cpt.metadata.validate(validator, notes)
            
            logger.info(f"CPT {cpt_id} validated by {validator}")
            return True
            
        except Exception as e:
            logger.error(f"CPT {cpt_id} validation failed: {str(e)}")
            return False
    
    def approve_cpt(self, cpt_id: str, approver: str) -> bool:
        """
        Approve a validated CPT.
        
        Args:
            cpt_id: CPT to approve
            approver: Approver identifier
            
        Returns:
            True if approval successful
        """
        cpt = self.get_cpt(cpt_id)
        if not cpt:
            raise ValueError(f"CPT {cpt_id} not found")
        
        try:
            cpt.metadata.approve(approver)
            logger.info(f"CPT {cpt_id} approved by {approver}")
            return True
            
        except Exception as e:
            logger.error(f"CPT {cpt_id} approval failed: {str(e)}")
            return False
    
    def get_shared_cpts(self, typology1: str, typology2: str) -> List[TypedCPT]:
        """Get CPTs that can be shared between two typologies."""
        cpts1 = set(self.cpts_by_typology.get(typology1, set()))
        cpts2 = set(self.cpts_by_typology.get(typology2, set()))
        
        # Find CPTs that are applicable to both or marked as cross-typology
        shared_ids = cpts1.intersection(cpts2)
        
        # Also include cross-typology CPTs
        for cpt_id, cpt in self.cpts.items():
            if cpt.cpt_type == CPTType.CROSS_TYPOLOGY:
                shared_ids.add(cpt_id)
        
        return [self.cpts[cpt_id] for cpt_id in shared_ids if cpt_id in self.cpts]
    
    def export_library(self) -> Dict[str, Any]:
        """Export entire library for backup/transfer."""
        return {
            "cpts": {
                cpt_id: cpt.to_dict() 
                for cpt_id, cpt in self.cpts.items()
            },
            "regulatory_references": self.regulatory_manager.export_references(),
            "version_history": self.version_manager.export_history(),
            "metadata": {
                "total_cpts": len(self.cpts),
                "export_timestamp": datetime.now().isoformat(),
                "library_version": "1.0.0"
            }
        }
    
    def save_library(self) -> None:
        """Save library to disk."""
        try:
            # Save CPTs
            cpts_file = self.library_path / "cpts.json"
            with open(cpts_file, 'w') as f:
                json.dump(self.export_library(), f, indent=2)
            
            logger.info(f"CPT Library saved to {self.library_path}")
            
        except Exception as e:
            logger.error(f"Error saving CPT library: {str(e)}")
    
    def get_library_stats(self) -> Dict[str, Any]:
        """Get library statistics."""
        stats = {
            "total_cpts": len(self.cpts),
            "cpts_by_status": {},
            "cpts_by_typology": {k: len(v) for k, v in self.cpts_by_typology.items()},
            "cpts_by_framework": {k: len(v) for k, v in self.cpts_by_framework.items()},
            "total_regulatory_references": len(self.regulatory_manager.references),
            "total_enforcement_cases": len(self.regulatory_manager.enforcement_cases)
        }
        
        # Count by status
        for cpt in self.cpts.values():
            status = cpt.metadata.status.value
            stats["cpts_by_status"][status] = stats["cpts_by_status"].get(status, 0) + 1
        
        return stats