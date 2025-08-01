"""
Comprehensive Tests for CPT Library System

This module tests all components of the centralized CPT Library including:
- Regulatory references and enforcement cases
- Typed CPT definitions with metadata
- Version management and change tracking  
- Typology templates and cross-typology sharing
- Library management and persistence
"""

import pytest
import tempfile
import json
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.models.bayesian.shared.cpt_library import (
    CPTLibrary, TypedCPT, CPTMetadata, CPTType, CPTStatus,
    RegulatoryReference, EnforcementCase, RegulatoryFramework, EnforcementLevel,
    CPTVersionManager, TypologyTemplateManager
)


class TestRegulatoryReference:
    """Test regulatory reference system."""
    
    def test_enforcement_case_creation(self):
        """Test enforcement case creation and validation."""
        case = EnforcementCase(
            case_id="TEST_001",
            case_name="Test Enforcement Case",
            regulatory_authority="Test Authority",
            framework=RegulatoryFramework.MAR_ARTICLE_8,
            enforcement_level=EnforcementLevel.FINE,
            violation_type="Insider Dealing",
            case_summary="Test case summary",
            enforcement_date=datetime(2023, 6, 15),
            penalty_amount=1000000.0,
            relevant_nodes=["MaterialInfo", "Timing"],
            probability_justification="Test justification",
            case_reference="TEST/2023/001"
        )
        
        assert case.case_id == "TEST_001"
        assert case.framework == RegulatoryFramework.MAR_ARTICLE_8
        assert case.enforcement_level == EnforcementLevel.FINE
        assert case.penalty_amount == 1000000.0
        assert "MaterialInfo" in case.relevant_nodes
    
    def test_regulatory_reference_creation(self):
        """Test regulatory reference creation."""
        ref = RegulatoryReference(
            reference_id="REG_TEST_001",
            framework=RegulatoryFramework.MAR_ARTICLE_8,
            article_section="Article 8(1)",
            requirement_text="Test requirement",
            interpretation_guidance="Test guidance",
            compliance_threshold=0.7,
            applicable_typologies=["insider_dealing"],
            probability_rationale="Test rationale"
        )
        
        assert ref.reference_id == "REG_TEST_001"
        assert ref.framework == RegulatoryFramework.MAR_ARTICLE_8
        assert ref.compliance_threshold == 0.7
        assert "insider_dealing" in ref.applicable_typologies
    
    def test_enforcement_case_addition(self):
        """Test adding enforcement cases to references."""
        ref = RegulatoryReference(
            reference_id="REG_TEST_002",
            framework=RegulatoryFramework.MAR_ARTICLE_12,
            article_section="Article 12(1)",
            requirement_text="Test requirement",
            interpretation_guidance="Test guidance",
            applicable_typologies=["spoofing"]
        )
        
        case = EnforcementCase(
            case_id="ENF_TEST_001",
            case_name="Test Case",
            regulatory_authority="Test Authority",
            framework=RegulatoryFramework.MAR_ARTICLE_12,
            enforcement_level=EnforcementLevel.WARNING,
            violation_type="Spoofing",
            case_summary="Test summary",
            enforcement_date=datetime.now()
        )
        
        initial_update_time = ref.last_updated
        ref.add_enforcement_case(case)
        
        assert len(ref.enforcement_cases) == 1
        assert ref.enforcement_cases[0].case_id == "ENF_TEST_001"
        assert ref.last_updated > initial_update_time


class TestTypedCPT:
    """Test typed CPT definitions."""
    
    def test_cpt_metadata_creation(self):
        """Test CPT metadata creation and validation."""
        metadata = CPTMetadata(
            cpt_id="CPT_TEST_001",
            version="1.0.0",
            status=CPTStatus.DRAFT,
            regulatory_references=["REG_TEST_001"],
            compliance_frameworks=["MAR Article 8"],
            created_by="test_user"
        )
        
        assert metadata.cpt_id == "CPT_TEST_001"
        assert metadata.version == "1.0.0"
        assert metadata.status == CPTStatus.DRAFT
        assert "REG_TEST_001" in metadata.regulatory_references
        assert metadata.usage_count == 0
    
    def test_cpt_creation_and_validation(self):
        """Test typed CPT creation and validation."""
        metadata = CPTMetadata(
            cpt_id="CPT_TEST_002",
            version="1.0.0",
            status=CPTStatus.DRAFT
        )
        
        cpt = TypedCPT(
            metadata=metadata,
            cpt_type=CPTType.EVIDENCE_NODE,
            node_name="TestNode",
            node_states=["Low", "Medium", "High"],
            node_description="Test node description",
            fallback_prior=[0.6, 0.3, 0.1],
            probability_rationale="Test rationale"
        )
        
        assert cpt.node_name == "TestNode"
        assert len(cpt.node_states) == 3
        assert cpt.cpt_type == CPTType.EVIDENCE_NODE
        assert len(cpt.fallback_prior) == 3
        assert sum(cpt.fallback_prior) == pytest.approx(1.0)
    
    def test_cpt_probability_calculation(self):
        """Test CPT probability calculations."""
        metadata = CPTMetadata(
            cpt_id="CPT_TEST_003",
            version="1.0.0",
            status=CPTStatus.APPROVED
        )
        
        cpt = TypedCPT(
            metadata=metadata,
            cpt_type=CPTType.EVIDENCE_NODE,
            node_name="TestNode",
            node_states=["Low", "High"],
            node_description="Test node",
            fallback_prior=[0.8, 0.2]
        )
        
        # Test fallback prior
        prob_low = cpt.get_probability("Low")
        prob_high = cpt.get_probability("High")
        
        assert prob_low == 0.8
        assert prob_high == 0.2
        
        # Test invalid state
        with pytest.raises(ValueError):
            cpt.get_probability("Invalid")
    
    def test_cpt_with_parents(self):
        """Test CPT with parent nodes."""
        metadata = CPTMetadata(
            cpt_id="CPT_TEST_004",
            version="1.0.0",
            status=CPTStatus.VALIDATED
        )
        
        cpt = TypedCPT(
            metadata=metadata,
            cpt_type=CPTType.EVIDENCE_NODE,
            node_name="ChildNode",
            node_states=["False", "True"],
            node_description="Child node with parents",
            parent_nodes=["Parent1"],
            parent_states={"Parent1": ["Low", "High"]},
            probability_table=[
                [0.9, 0.3],  # P(ChildNode=False | Parent1=Low/High)
                [0.1, 0.7]   # P(ChildNode=True | Parent1=Low/High)
            ]
        )
        
        # Test conditional probabilities
        prob_false_given_low = cpt.get_probability("False", {"Parent1": "Low"})
        prob_true_given_high = cpt.get_probability("True", {"Parent1": "High"})
        
        assert prob_false_given_low == 0.9
        assert prob_true_given_high == 0.7
    
    def test_cpt_validation_and_approval(self):
        """Test CPT validation and approval workflow."""
        metadata = CPTMetadata(
            cpt_id="CPT_TEST_005",
            version="1.0.0",
            status=CPTStatus.DRAFT
        )
        
        # Test validation
        metadata.validate("test_validator", "Validation passed")
        assert metadata.status == CPTStatus.VALIDATED
        assert metadata.validated_by == "test_validator"
        assert metadata.validation_notes == "Validation passed"
        
        # Test approval
        metadata.approve("test_approver")
        assert metadata.status == CPTStatus.APPROVED
        assert metadata.updated_by == "test_approver"
    
    def test_cpt_cloning(self):
        """Test CPT cloning for versioning."""
        metadata = CPTMetadata(
            cpt_id="CPT_TEST_006",
            version="1.0.0",
            status=CPTStatus.APPROVED
        )
        
        original_cpt = TypedCPT(
            metadata=metadata,
            cpt_type=CPTType.EVIDENCE_NODE,
            node_name="OriginalNode",
            node_states=["Low", "High"],
            node_description="Original node",
            fallback_prior=[0.7, 0.3]
        )
        
        # Clone to new version
        cloned_cpt = original_cpt.clone("2.0.0", "test_user")
        
        assert cloned_cpt.metadata.version == "2.0.0"
        assert cloned_cpt.metadata.status == CPTStatus.DRAFT
        assert cloned_cpt.metadata.created_by == "test_user"
        assert cloned_cpt.node_name == "OriginalNode"
        assert cloned_cpt.node_states == ["Low", "High"]
        assert cloned_cpt.metadata.cpt_id != original_cpt.metadata.cpt_id


class TestCPTVersionManager:
    """Test CPT version management."""
    
    def test_version_tracking(self):
        """Test version change tracking."""
        manager = CPTVersionManager()
        
        # Track initial version
        manager.track_version("CPT_001", "1.0.0", "added", "user1", "Initial version")
        
        # Track update
        manager.track_version("CPT_001", "1.1.0", "updated", "user2", "Bug fixes")
        
        # Check history
        history = manager.get_version_history("CPT_001")
        assert len(history) == 2
        assert history[0].version == "1.0.0"
        assert history[1].version == "1.1.0"
        assert history[1].previous_version == "1.0.0"
        
        # Check current version
        current = manager.get_current_version("CPT_001")
        assert current == "1.1.0"
    
    def test_latest_changes(self):
        """Test getting latest changes across all CPTs."""
        manager = CPTVersionManager()
        
        # Add multiple CPT changes
        manager.track_version("CPT_001", "1.0.0", "added", "user1")
        manager.track_version("CPT_002", "1.0.0", "added", "user2")
        manager.track_version("CPT_001", "1.1.0", "updated", "user1")
        
        # Get latest changes
        latest = manager.get_latest_changes(limit=2)
        assert len(latest) == 2
        assert latest[0].cpt_id == "CPT_001"  # Most recent
        assert latest[0].version == "1.1.0"


class TestTypologyTemplateManager:
    """Test typology template management."""
    
    def test_template_loading(self):
        """Test default template loading."""
        manager = TypologyTemplateManager()
        
        # Check available typologies
        typologies = manager.get_available_typologies()
        assert "insider_dealing" in typologies
        assert "spoofing" in typologies
        assert "wash_trade_detection" in typologies
        assert "cross_typology" in typologies
    
    def test_template_retrieval(self):
        """Test template retrieval."""
        manager = TypologyTemplateManager()
        
        # Get specific template
        template = manager.get_template("insider_dealing", "MaterialInfo")
        assert template is not None
        assert template["cpt_type"] == CPTType.EVIDENCE_NODE
        assert "None" in template["node_states"]
        assert "Limited" in template["node_states"]
        assert "Substantial" in template["node_states"]
        
        # Test non-existent template
        template = manager.get_template("nonexistent", "node")
        assert template is None
    
    def test_cross_typology_templates(self):
        """Test cross-typology template functionality."""
        manager = TypologyTemplateManager()
        
        cross_templates = manager.get_cross_typology_templates()
        assert "RegulatoryRisk" in cross_templates
        assert "MarketImpact" in cross_templates
        
        reg_risk_template = cross_templates["RegulatoryRisk"]
        assert reg_risk_template["cpt_type"] == CPTType.CROSS_TYPOLOGY
        assert len(reg_risk_template["node_states"]) == 4  # Low, Medium, High, Critical
    
    def test_template_addition(self):
        """Test adding custom templates."""
        manager = TypologyTemplateManager()
        
        custom_template = {
            "cpt_type": CPTType.EVIDENCE_NODE,
            "node_states": ["Normal", "Abnormal"],
            "description": "Custom test node",
            "fallback_prior": [0.8, 0.2]
        }
        
        manager.add_template("test_typology", "CustomNode", custom_template)
        
        # Verify addition
        retrieved = manager.get_template("test_typology", "CustomNode")
        assert retrieved is not None
        assert retrieved["description"] == "Custom test node"
        assert "test_typology" in manager.get_available_typologies()


class TestCPTLibrary:
    """Test main CPT Library functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.library_path = Path(self.temp_dir) / "test_library"
        self.library = CPTLibrary(self.library_path)
    
    def test_library_initialization(self):
        """Test library initialization."""
        assert self.library.library_path == self.library_path
        assert self.library_path.exists()
        assert len(self.library.cpts) == 0  # Empty initially
        assert self.library.regulatory_manager is not None
        assert self.library.version_manager is not None
        assert self.library.template_manager is not None
    
    def test_cpt_addition_and_retrieval(self):
        """Test adding and retrieving CPTs."""
        # Create test CPT
        metadata = CPTMetadata(
            cpt_id="CPT_LIB_001",
            version="1.0.0",
            status=CPTStatus.DRAFT,
            applicable_models=["insider_dealing"]
        )
        
        cpt = TypedCPT(
            metadata=metadata,
            cpt_type=CPTType.EVIDENCE_NODE,
            node_name="TestLibraryNode",
            node_states=["Low", "Medium", "High"],
            node_description="Test library node"
        )
        
        # Add to library
        cpt_id = self.library.add_cpt(cpt)
        assert cpt_id == "CPT_LIB_001"
        
        # Retrieve from library
        retrieved = self.library.get_cpt(cpt_id)
        assert retrieved is not None
        assert retrieved.node_name == "TestLibraryNode"
        assert retrieved.metadata.cpt_id == cpt_id
    
    def test_typology_based_retrieval(self):
        """Test retrieving CPTs by typology."""
        # Add CPT for insider dealing
        metadata1 = CPTMetadata(
            cpt_id="CPT_INSIDER_001",
            version="1.0.0",
            status=CPTStatus.APPROVED,
            applicable_models=["insider_dealing"]
        )
        
        cpt1 = TypedCPT(
            metadata=metadata1,
            cpt_type=CPTType.EVIDENCE_NODE,
            node_name="InsiderNode",
            node_states=["Low", "High"],
            node_description="Insider dealing node"
        )
        
        # Add CPT for spoofing
        metadata2 = CPTMetadata(
            cpt_id="CPT_SPOOF_001",
            version="1.0.0",
            status=CPTStatus.APPROVED,
            applicable_models=["spoofing"]
        )
        
        cpt2 = TypedCPT(
            metadata=metadata2,
            cpt_type=CPTType.EVIDENCE_NODE,
            node_name="SpoofingNode",
            node_states=["Normal", "Suspicious"],
            node_description="Spoofing node"
        )
        
        self.library.add_cpt(cpt1)
        self.library.add_cpt(cpt2)
        
        # Test typology-based retrieval
        insider_cpts = self.library.get_cpts_for_typology("insider_dealing")
        spoofing_cpts = self.library.get_cpts_for_typology("spoofing")
        
        assert len(insider_cpts) == 1
        assert len(spoofing_cpts) == 1
        assert insider_cpts[0].node_name == "InsiderNode"
        assert spoofing_cpts[0].node_name == "SpoofingNode"
    
    def test_cpt_creation_from_template(self):
        """Test creating CPT from template."""
        cpt = self.library.create_cpt_from_template(
            "insider_dealing", 
            "MaterialInfo", 
            "test_user"
        )
        
        assert cpt.node_name == "MaterialInfo"
        assert cpt.cpt_type == CPTType.EVIDENCE_NODE
        assert "None" in cpt.node_states
        assert "Limited" in cpt.node_states
        assert "Substantial" in cpt.node_states
        assert cpt.metadata.created_by == "test_user"
        assert "insider_dealing" in cpt.metadata.applicable_models
    
    def test_cpt_validation_workflow(self):
        """Test CPT validation workflow."""
        # Create and add CPT
        metadata = CPTMetadata(
            cpt_id="CPT_VALIDATE_001",
            version="1.0.0",
            status=CPTStatus.DRAFT
        )
        
        cpt = TypedCPT(
            metadata=metadata,
            cpt_type=CPTType.EVIDENCE_NODE,
            node_name="ValidationNode",
            node_states=["Low", "High"],
            node_description="Node for validation testing"
        )
        
        cpt_id = self.library.add_cpt(cpt)
        
        # Validate CPT
        result = self.library.validate_cpt(cpt_id, "validator_user", "Validation complete")
        assert result is True
        
        validated_cpt = self.library.get_cpt(cpt_id)
        assert validated_cpt.metadata.status == CPTStatus.VALIDATED
        assert validated_cpt.metadata.validated_by == "validator_user"
        
        # Approve CPT
        result = self.library.approve_cpt(cpt_id, "approver_user")
        assert result is True
        
        approved_cpt = self.library.get_cpt(cpt_id)
        assert approved_cpt.metadata.status == CPTStatus.APPROVED
        assert approved_cpt.metadata.updated_by == "approver_user"
    
    def test_shared_cpts(self):
        """Test cross-typology CPT sharing."""
        # Add cross-typology CPT
        metadata = CPTMetadata(
            cpt_id="CPT_CROSS_001",
            version="1.0.0",
            status=CPTStatus.APPROVED,
            applicable_models=["insider_dealing", "spoofing"]
        )
        
        cross_cpt = TypedCPT(
            metadata=metadata,
            cpt_type=CPTType.CROSS_TYPOLOGY,
            node_name="SharedRiskNode",
            node_states=["Low", "Medium", "High"],
            node_description="Shared risk assessment node"
        )
        
        self.library.add_cpt(cross_cpt)
        
        # Test shared CPT retrieval
        shared = self.library.get_shared_cpts("insider_dealing", "spoofing")
        assert len(shared) == 1
        assert shared[0].node_name == "SharedRiskNode"
        assert shared[0].cpt_type == CPTType.CROSS_TYPOLOGY
    
    def test_library_statistics(self):
        """Test library statistics generation."""
        # Add multiple CPTs with different statuses
        for i in range(3):
            metadata = CPTMetadata(
                cpt_id=f"CPT_STATS_{i:03d}",
                version="1.0.0",
                status=CPTStatus.DRAFT if i == 0 else CPTStatus.APPROVED,
                applicable_models=["insider_dealing"]
            )
            
            cpt = TypedCPT(
                metadata=metadata,
                cpt_type=CPTType.EVIDENCE_NODE,
                node_name=f"StatsNode{i}",
                node_states=["Low", "High"],
                node_description=f"Statistics test node {i}"
            )
            
            self.library.add_cpt(cpt)
        
        # Get statistics
        stats = self.library.get_library_stats()
        
        assert stats["total_cpts"] == 3
        assert stats["cpts_by_status"]["draft"] == 1
        assert stats["cpts_by_status"]["approved"] == 2
        assert stats["cpts_by_typology"]["insider_dealing"] == 3
        assert stats["total_regulatory_references"] >= 2  # From default loading
    
    def test_library_export_and_persistence(self):
        """Test library export and save functionality."""
        # Add test CPT
        metadata = CPTMetadata(
            cpt_id="CPT_EXPORT_001",
            version="1.0.0",
            status=CPTStatus.APPROVED
        )
        
        cpt = TypedCPT(
            metadata=metadata,
            cpt_type=CPTType.EVIDENCE_NODE,
            node_name="ExportNode",
            node_states=["Low", "High"],
            node_description="Export test node"
        )
        
        self.library.add_cpt(cpt)
        
        # Export library
        exported = self.library.export_library()
        
        assert "cpts" in exported
        assert "regulatory_references" in exported
        assert "version_history" in exported
        assert "metadata" in exported
        assert exported["metadata"]["total_cpts"] == 1
        
        # Test save functionality
        self.library.save_library()
        
        # Verify file was created
        cpts_file = self.library_path / "cpts.json"
        assert cpts_file.exists()
        
        # Verify content
        with open(cpts_file, 'r') as f:
            saved_data = json.load(f)
            assert "CPT_EXPORT_001" in saved_data["cpts"]


class TestIntegration:
    """Integration tests for complete CPT Library workflow."""
    
    def test_end_to_end_workflow(self):
        """Test complete end-to-end CPT Library workflow."""
        with tempfile.TemporaryDirectory() as temp_dir:
            library_path = Path(temp_dir) / "integration_test"
            library = CPTLibrary(library_path)
            
            # Step 1: Create CPT from template
            cpt = library.create_cpt_from_template(
                "insider_dealing", 
                "MaterialInfo", 
                "integration_user"
            )
            
            # Step 2: Add to library
            cpt_id = library.add_cpt(cpt)
            
            # Step 3: Validate
            validation_result = library.validate_cpt(
                cpt_id, 
                "validator", 
                "Integration test validation"
            )
            assert validation_result is True
            
            # Step 4: Approve
            approval_result = library.approve_cpt(cpt_id, "approver")
            assert approval_result is True
            
            # Step 5: Verify final state
            final_cpt = library.get_cpt(cpt_id)
            assert final_cpt.metadata.status == CPTStatus.APPROVED
            assert final_cpt.metadata.validated_by == "validator"
            assert final_cpt.metadata.updated_by == "approver"
            
            # Step 6: Check version history
            history = library.version_manager.get_version_history(cpt_id)
            assert len(history) >= 1
            
            # Step 7: Verify regulatory references
            assert len(final_cpt.metadata.regulatory_references) > 0
            
            # Step 8: Test cross-typology functionality
            typology_cpts = library.get_cpts_for_typology("insider_dealing")
            assert len(typology_cpts) == 1
            assert typology_cpts[0].metadata.cpt_id == cpt_id
            
            # Step 9: Save and verify persistence
            library.save_library()
            assert (library_path / "cpts.json").exists()
            
            # Step 10: Get final statistics
            stats = library.get_library_stats()
            assert stats["total_cpts"] == 1
            assert stats["cpts_by_status"]["approved"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])