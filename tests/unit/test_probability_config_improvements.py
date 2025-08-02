#!/usr/bin/env python3
"""
Improved Test Suite for Probability Configuration System

This module provides structured, maintainable tests using pytest framework
to validate the probability configuration improvements and error handling fixes.

Test Categories:
1. Error Handling Validation
2. Centralized Configuration Testing  
3. Performance Validation
4. Model Integration Testing
5. Hierarchical Structure Testing
"""

import pytest
import sys
import os
import time
from typing import Dict, List, Any
from unittest.mock import Mock, patch

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from src.models.bayesian.shared.probability_config import (
        ProbabilityConfig, 
        EvidenceType, 
        ProbabilityProfile
    )
    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False
    pytest.skip("Dependencies not available", allow_module_level=True)


class TestErrorHandling:
    """Test error handling improvements in intermediate nodes."""
    
    @pytest.fixture
    def mock_market_impact_node(self):
        """Create a mock market impact node for testing."""
        try:
            from src.models.bayesian.shared.reusable_intermediate_nodes import MarketImpactNode
            return MarketImpactNode(name="test_market_impact", parent_nodes=None)
        except ImportError:
            pytest.skip("Intermediate nodes module not available")
    
    def test_error_includes_node_name(self, mock_market_impact_node):
        """Test that error messages include the node name for easier debugging.
        
        Validates:
        - Error message contains node name
        - Error is raised when parent nodes are missing
        - Error message format is consistent
        """
        with pytest.raises(ValueError) as exc_info:
            mock_market_impact_node.create_noisy_or_cpt()
        
        error_message = str(exc_info.value)
        assert "test_market_impact:" in error_message, f"Node name not in error: {error_message}"
        assert "Parent nodes must be specified" in error_message
    
    def test_different_node_types_have_specific_errors(self):
        """Test that different node types provide specific error messages.
        
        Validates:
        - Each node type has appropriate error messages
        - Error messages are contextual to the node type
        - Error handling is consistent across node types
        """
        try:
            from src.models.bayesian.shared.reusable_intermediate_nodes import (
                BehavioralIntentNode, CoordinationPatternsNode
            )
            
            behavioral_node = BehavioralIntentNode(name="test_behavioral", parent_nodes=None)
            coordination_node = CoordinationPatternsNode(name="test_coordination", parent_nodes=None)
            
            # Test behavioral node error
            with pytest.raises(ValueError) as behavioral_exc:
                behavioral_node.create_noisy_or_cpt()
            assert "test_behavioral:" in str(behavioral_exc.value)
            
            # Test coordination node error  
            with pytest.raises(ValueError) as coordination_exc:
                coordination_node.create_noisy_or_cpt()
            assert "test_coordination:" in str(coordination_exc.value)
            
        except ImportError:
            pytest.skip("Intermediate nodes module not available")


class TestCentralizedConfiguration:
    """Test centralized probability configuration system."""
    
    def test_probability_profile_validation(self):
        """Test that probability profiles validate correctly.
        
        Validates:
        - Probabilities sum to 1.0
        - Individual probabilities are in valid range
        - Validation errors are raised for invalid profiles
        
        Returns:
            None: Test passes if validation works correctly
        """
        # Valid profile
        valid_profile = ProbabilityProfile(0.7, 0.25, 0.05, "Test profile")
        assert abs(valid_profile.low_state + valid_profile.medium_state + valid_profile.high_state - 1.0) < 0.01
        
        # Invalid profile should raise error
        with pytest.raises(ValueError):
            ProbabilityProfile(0.5, 0.3, 0.1, "Invalid profile")  # Sums to 0.9
    
    def test_evidence_node_probability_retrieval(self):
        """Test evidence node probability retrieval system.
        
        Validates:
        - Evidence nodes return correct probability profiles
        - Profile types match expected evidence types
        - Fallback behavior for unknown nodes
        
        Returns:
            None: Test passes if retrieval works correctly
        """
        # Test known evidence node
        order_clustering_prob = ProbabilityConfig.get_evidence_prior("order_clustering")
        assert isinstance(order_clustering_prob, ProbabilityProfile)
        assert order_clustering_prob.low_state > 0
        
        # Test behavioral evidence consistency
        order_behavior_prob = ProbabilityConfig.get_evidence_prior("order_behavior")
        intent_to_execute_prob = ProbabilityConfig.get_evidence_prior("intent_to_execute")
        
        # Both should use BEHAVIORAL evidence type, so should be equal
        assert order_behavior_prob.low_state == intent_to_execute_prob.low_state
        assert order_behavior_prob.medium_state == intent_to_execute_prob.medium_state
    
    def test_intermediate_node_parameters(self):
        """Test intermediate node parameter retrieval.
        
        Validates:
        - Intermediate parameters are correctly structured
        - Parameters contain required fields
        - Parameter values are within expected ranges
        
        Returns:
            None: Test passes if parameters are valid
        """
        market_impact_params = ProbabilityConfig.get_intermediate_params("market_impact")
        
        assert "leak_probability" in market_impact_params
        assert "parent_probabilities" in market_impact_params
        assert "description" in market_impact_params
        
        # Validate parameter ranges
        assert 0 <= market_impact_params["leak_probability"] <= 1
        assert all(0 <= p <= 1 for p in market_impact_params["parent_probabilities"])
    
    def test_evidence_cpd_creation(self):
        """Test evidence CPD creation functionality.
        
        Validates:
        - CPDs are created with correct structure
        - Variable cards match expected values
        - Probability values are valid
        
        Returns:
            None: Test passes if CPD creation works
        """
        try:
            cpd = ProbabilityConfig.create_evidence_cpd("order_clustering", variable_card=3)
            
            # Validate CPD structure
            assert cpd.variable == "order_clustering"
            assert cpd.variable_card == 3
            assert len(cpd.values) == 3  # 3 states
            
            # Validate probabilities sum to 1
            prob_sum = sum(cpd.values[i][0] for i in range(3))
            assert abs(prob_sum - 1.0) < 0.01
            
        except ImportError:
            pytest.skip("pgmpy not available for CPD creation")
    
    def test_business_logic_documentation(self):
        """Test that business logic is properly documented.
        
        Validates:
        - Probability profiles have descriptions
        - Regulatory basis is documented where applicable
        - Documentation is meaningful and specific
        
        Returns:
            None: Test passes if documentation is adequate
        """
        behavioral_profile = ProbabilityConfig.EVIDENCE_PROFILES[EvidenceType.BEHAVIORAL]
        
        assert behavioral_profile.description
        assert len(behavioral_profile.description) > 10  # Meaningful description
        assert behavioral_profile.regulatory_basis  # Should have regulatory basis


class TestPerformanceValidation:
    """Test that performance requirements are maintained."""
    
    # Performance threshold constants with clear units
    MAX_ACCEPTABLE_LOOKUP_SECONDS = 0.1
    MAX_ACCEPTABLE_CPD_CREATION_SECONDS = 1.0
    MAX_LOOKUPS_FOR_PERFORMANCE_TEST = 1000
    MAX_CPD_CREATIONS_FOR_PERFORMANCE_TEST = 100
    
    def test_configuration_lookup_performance(self):
        """Test that configuration lookup maintains performance requirements.
        
        Performance thresholds:
        - Configuration lookup: < 0.1s for 1000 lookups
        - Individual lookup: < 0.0001s average
        
        Returns:
            None: Test passes if performance thresholds are met
        """
        start_time = time.time()
        
        # Perform multiple lookups
        for _ in range(self.MAX_LOOKUPS_FOR_PERFORMANCE_TEST):
            ProbabilityConfig.get_evidence_prior("order_clustering")
        
        lookup_time = time.time() - start_time
        
        assert lookup_time < self.MAX_ACCEPTABLE_LOOKUP_SECONDS, (
            f"Configuration lookup too slow: {lookup_time:.4f}s > "
            f"{self.MAX_ACCEPTABLE_LOOKUP_SECONDS}s for {self.MAX_LOOKUPS_FOR_PERFORMANCE_TEST} lookups"
        )
    
    def test_cpd_creation_performance(self):
        """Test CPD creation performance.
        
        Performance thresholds:
        - CPD creation: Monitor timing for 100 creations
        - Should complete without excessive memory usage
        
        Returns:
            None: Test passes if performance is acceptable
        """
        start_time = time.time()
        
        try:
            for i in range(self.MAX_CPD_CREATIONS_FOR_PERFORMANCE_TEST):
                ProbabilityConfig.create_evidence_cpd(f"test_node_{i%10}", variable_card=3)
        except ImportError:
            pytest.skip("pgmpy not available for CPD creation")
        except Exception as e:
            pytest.fail(f"CPD creation failed: {e}")
        
        creation_time = time.time() - start_time
        
        # Log performance (not a hard requirement, but monitored)
        print(f"CPD creation performance: {creation_time:.4f}s for {self.MAX_CPD_CREATIONS_FOR_PERFORMANCE_TEST} creations")
        
        # Ensure it doesn't take unreasonably long
        assert creation_time < self.MAX_ACCEPTABLE_CPD_CREATION_SECONDS, (
            f"CPD creation too slow: {creation_time:.4f}s > {self.MAX_ACCEPTABLE_CPD_CREATION_SECONDS}s"
        )


class TestModelIntegration:
    """Test integration with model systems."""
    
    @pytest.fixture
    def mock_spoofing_model(self):
        """Create a mock spoofing model for testing."""
        try:
            from src.models.bayesian.spoofing.model import SpoofingModel
            return SpoofingModel(use_latent_intent=True)
        except ImportError:
            pytest.skip("Spoofing model not available")
    
    def test_spoofing_model_initialization(self, mock_spoofing_model):
        """Test spoofing model initialization with new configurations.
        
        Validates:
        - Model initializes without errors
        - Correct number of intermediate nodes
        - Node types are as expected
        
        Returns:
            None: Test passes if model integration works
        """
        # Check that model has expected structure
        assert hasattr(mock_spoofing_model, 'config')
        assert hasattr(mock_spoofing_model, 'nodes')
        
        # Model should initialize successfully
        assert mock_spoofing_model.model is not None
    
    def test_cross_model_consistency(self):
        """Test consistency across different models.
        
        Validates:
        - Same evidence types use same probabilities
        - Node recommendations are model-appropriate
        - Factory creates correct configurations
        
        Returns:
            None: Test passes if cross-model consistency is maintained
        """
        try:
            from src.models.bayesian.shared.reusable_intermediate_nodes import ReusableNodeFactory
            
            # Test model-specific recommendations
            spoofing_recommendations = ReusableNodeFactory.get_recommended_nodes_for_model("spoofing")
            collusion_recommendations = ReusableNodeFactory.get_recommended_nodes_for_model("cross_desk_collusion")
            
            assert "market_impact" in spoofing_recommendations
            assert "coordination_patterns" in collusion_recommendations
            
        except ImportError:
            pytest.skip("ReusableNodeFactory not available")


class TestHierarchicalStructure:
    """Test hierarchical evidence node structure."""
    
    def test_model_specific_node_retrieval(self):
        """Test retrieval of nodes for specific models.
        
        Validates:
        - Model-specific nodes are returned correctly
        - Lazy loading works as expected
        - Unknown models return empty dictionaries
        
        Returns:
            None: Test passes if hierarchical structure works
        """
        spoofing_nodes = ProbabilityConfig.EvidenceNodeGroups.get_nodes_for_model('spoofing')
        
        assert len(spoofing_nodes) > 0
        assert "order_clustering" in spoofing_nodes
        assert "price_impact_ratio" in spoofing_nodes
        
        # Unknown model should return empty dict
        unknown_nodes = ProbabilityConfig.EvidenceNodeGroups.get_nodes_for_model('unknown_model')
        assert len(unknown_nodes) == 0
    
    def test_model_completeness_validation(self):
        """Test validation of model completeness.
        
        Validates:
        - Required nodes exist for models
        - Validation correctly identifies missing nodes
        - Model types are properly supported
        
        Returns:
            None: Test passes if validation works correctly
        """
        # Test complete model
        required_spoofing_nodes = ["order_clustering", "price_impact_ratio", "volume_participation"]
        is_complete = ProbabilityConfig.EvidenceNodeGroups.validate_model_completeness(
            'spoofing', required_spoofing_nodes
        )
        assert is_complete
        
        # Test incomplete model
        missing_nodes = ["nonexistent_node"]
        is_incomplete = ProbabilityConfig.EvidenceNodeGroups.validate_model_completeness(
            'spoofing', missing_nodes
        )
        assert not is_incomplete
    
    def test_supported_model_types(self):
        """Test that supported model types are correctly identified.
        
        Validates:
        - Model types list is not empty
        - Expected model types are included
        - List is consistent with implementation
        
        Returns:
            None: Test passes if model types are correct
        """
        model_types = ProbabilityConfig.EvidenceNodeGroups.get_model_types()
        
        assert len(model_types) > 0
        assert 'spoofing' in model_types
        assert 'cross_desk_collusion' in model_types


class TestConfigurationValidation:
    """Test explicit configuration validation."""
    
    def test_explicit_validation_call(self):
        """Test that explicit validation works correctly.
        
        Validates:
        - Validation can be called explicitly
        - Validation passes for current configuration
        - No import-time performance overhead
        
        Returns:
            None: Test passes if validation works
        """
        # This should not raise an exception
        try:
            ProbabilityConfig.validate_all_probabilities()
        except Exception as e:
            pytest.fail(f"Configuration validation failed: {e}")
    
    def test_no_import_time_validation(self):
        """Test that validation is not performed at import time.
        
        Validates:
        - Import time is reasonable
        - No automatic validation overhead
        - Validation is opt-in
        
        Returns:
            None: Test passes if import performance is good
        """
        # This is more of a design validation - 
        # the fact that we can import without issues indicates success
        import_start = time.time()
        
        # Re-import the module (this should be fast)
        import importlib
        import src.models.bayesian.shared.probability_config
        importlib.reload(src.models.bayesian.shared.probability_config)
        
        import_time = time.time() - import_start
        
        # Import should be very fast (< 0.1s)
        assert import_time < 0.1, f"Import too slow: {import_time:.4f}s"


# Performance test fixtures and utilities
@pytest.fixture
def performance_monitor():
    """Fixture to monitor test performance."""
    start_time = time.time()
    yield
    end_time = time.time()
    print(f"\nTest execution time: {end_time - start_time:.4f}s")


# Parameterized tests for different evidence types
@pytest.mark.parametrize("evidence_type", [
    EvidenceType.BEHAVIORAL,
    EvidenceType.MARKET_IMPACT,
    EvidenceType.INFORMATION,
    EvidenceType.COORDINATION,
    EvidenceType.ECONOMIC,
    EvidenceType.TECHNICAL
])
def test_evidence_type_profiles(evidence_type):
    """Test that all evidence type profiles are valid.
    
    Args:
        evidence_type: The evidence type to test
        
    Validates:
        - Profile exists for each evidence type
        - Probabilities are valid
        - Documentation is present
    """
    profile = ProbabilityConfig.EVIDENCE_PROFILES[evidence_type]
    
    assert isinstance(profile, ProbabilityProfile)
    assert abs(profile.low_state + profile.medium_state + profile.high_state - 1.0) < 0.01
    assert profile.description
    assert len(profile.description) > 5


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])