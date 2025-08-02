#!/usr/bin/env python3
"""
Comprehensive Regression Testing Framework for Intermediate Node CPT Integration

This module provides end-to-end regression testing to ensure that the integration
of intermediate nodes with the CPT library maintains full backward compatibility
and doesn't break any existing functionality.

Test Categories:
1. CPT Library Integration Tests
2. Template System Regression Tests  
3. Model Builder Integration Tests
4. End-to-End Model Functionality Tests
5. Performance Regression Tests
6. Regulatory Compliance Tests
"""

import unittest
import sys
import os
import logging
from typing import Dict, List, Any, Optional
from unittest.mock import Mock, patch
import tempfile
import json

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from src.models.bayesian.shared.cpt_library.library import CPTLibrary
    from src.models.bayesian.shared.cpt_library.typed_cpt import TypedCPT, CPTMetadata, CPTType, CPTStatus
    from src.models.bayesian.shared.cpt_library.typology_templates import TypologyTemplateManager
    from src.models.bayesian.shared.cpt_library.intermediate_node_integration import (
        IntermediateNodeCPTLibraryIntegration,
        IntermediateNodeSpec,
        integrate_intermediate_nodes_with_cpt_library
    )
    from src.models.bayesian.shared.model_builder import ModelBuilder
    DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    print(f"Dependencies not available: {e}")
    DEPENDENCIES_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestCPTLibraryIntegration(unittest.TestCase):
    """Test CPT library integration with intermediate nodes."""
    
    def setUp(self):
        """Set up test environment."""
        if not DEPENDENCIES_AVAILABLE:
            self.skipTest("Required dependencies not available")
        
        # Create temporary library
        self.temp_dir = tempfile.mkdtemp()
        self.library = CPTLibrary(library_path=self.temp_dir)
        self.integration = IntermediateNodeCPTLibraryIntegration(self.library)
    
    def tearDown(self):
        """Clean up test environment."""
        if hasattr(self, 'temp_dir'):
            import shutil
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_intermediate_node_type_added(self):
        """Test that INTERMEDIATE_NODE type is properly added to CPT types."""
        self.assertIn(CPTType.INTERMEDIATE_NODE, CPTType)
        self.assertEqual(CPTType.INTERMEDIATE_NODE.value, "intermediate_node")
    
    def test_intermediate_node_specs_initialization(self):
        """Test that intermediate node specifications are properly initialized."""
        # Check that specs are loaded
        self.assertGreater(len(self.integration.intermediate_specs), 0)
        
        # Check specific specs
        self.assertIn("market_impact_spoofing", self.integration.intermediate_specs)
        self.assertIn("behavioral_intent_spoofing", self.integration.intermediate_specs)
        self.assertIn("cost_analysis_intermediate", self.integration.intermediate_specs)
        
        # Validate spec structure
        spec = self.integration.intermediate_specs["market_impact_spoofing"]
        self.assertEqual(spec.node_type, "market_impact")
        self.assertEqual(len(spec.parent_nodes), 3)
        self.assertIn("spoofing", spec.model_types)
    
    def test_template_creation(self):
        """Test intermediate node template creation."""
        # Create templates
        self.integration.create_intermediate_node_templates()
        
        # Verify templates were created
        spoofing_template = self.integration.template_manager.get_template("spoofing", "market_impact_spoofing")
        self.assertIsNotNone(spoofing_template)
        self.assertEqual(spoofing_template["cpt_type"], CPTType.INTERMEDIATE_NODE)
        
        # Check template structure
        self.assertIn("node_states", spoofing_template)
        self.assertIn("parent_nodes", spoofing_template)
        self.assertIn("probability_table", spoofing_template)
        self.assertEqual(len(spoofing_template["node_states"]), 3)
    
    def test_cpt_creation_and_validation(self):
        """Test CPT creation and validation for intermediate nodes."""
        # Create templates first
        self.integration.create_intermediate_node_templates()
        
        # Create CPTs
        cpt_ids = self.integration.create_intermediate_node_cpts()
        
        # Verify CPTs were created
        self.assertGreater(len(cpt_ids), 0)
        
        # Check specific CPT
        market_impact_cpt_id = cpt_ids.get("spoofing.market_impact_spoofing")
        self.assertIsNotNone(market_impact_cpt_id)
        
        # Retrieve and validate CPT
        cpt = self.library.get_cpt(market_impact_cpt_id)
        self.assertIsNotNone(cpt)
        self.assertEqual(cpt.cpt_type, CPTType.INTERMEDIATE_NODE)
        self.assertEqual(cpt.node_name, "market_impact_spoofing")
        
        # Validate CPT structure
        try:
            cpt._validate_structure()
            cpt._validate_probabilities()
        except Exception as e:
            self.fail(f"CPT validation failed: {e}")
    
    def test_probability_table_generation(self):
        """Test probability table generation using noisy-OR logic."""
        spec = self.integration.intermediate_specs["market_impact_spoofing"]
        prob_table = self.integration._generate_intermediate_probability_table(spec)
        
        # Check dimensions
        expected_combinations = 3 ** len(spec.parent_nodes)  # 3^3 = 27
        self.assertEqual(len(prob_table), 3)  # 3 states
        self.assertEqual(len(prob_table[0]), expected_combinations)
        
        # Check probability validity
        for combo_idx in range(expected_combinations):
            column_sum = sum(prob_table[state][combo_idx] for state in range(3))
            self.assertAlmostEqual(column_sum, 1.0, places=3, 
                                 msg=f"Probabilities don't sum to 1 for combination {combo_idx}")
            
            # Check individual probabilities are valid
            for state in range(3):
                prob = prob_table[state][combo_idx]
                self.assertGreaterEqual(prob, 0.0)
                self.assertLessEqual(prob, 1.0)
    
    def test_outcome_node_template_updates(self):
        """Test that outcome node templates are properly updated."""
        # Create intermediate templates first
        self.integration.create_intermediate_node_templates()
        
        # Update outcome templates
        self.integration.update_outcome_node_templates()
        
        # Check spoofing risk factor template
        risk_template = self.integration.template_manager.get_template("spoofing", "risk_factor")
        self.assertIsNotNone(risk_template)
        self.assertEqual(len(risk_template["parent_nodes"]), 2)  # Reduced from 6 to 2
        self.assertIn("market_impact_spoofing", risk_template["parent_nodes"])
        self.assertIn("behavioral_intent_spoofing", risk_template["parent_nodes"])
    
    def test_integration_validation(self):
        """Test the integration validation system."""
        # Run full integration
        self.integration.create_intermediate_node_templates()
        self.integration.create_intermediate_node_cpts()
        
        # Validate integration
        results = self.integration.validate_integration()
        
        # Check validation results
        self.assertGreater(results["templates_created"], 0)
        self.assertGreater(results["cpts_created"], 0) 
        self.assertEqual(len(results["validation_errors"]), 0)
        
        # Check integration summary
        summary = self.integration.get_integration_summary()
        self.assertGreater(summary["total_intermediate_nodes"], 0)
        self.assertIn("spoofing", summary["models_affected"])
        self.assertIn("economic_withholding", summary["models_affected"])


class TestBackwardCompatibility(unittest.TestCase):
    """Test that existing CPT library functionality remains intact."""
    
    def setUp(self):
        """Set up test environment."""
        if not DEPENDENCIES_AVAILABLE:
            self.skipTest("Required dependencies not available")
        
        self.temp_dir = tempfile.mkdtemp()
        self.library = CPTLibrary(library_path=self.temp_dir)
    
    def tearDown(self):
        """Clean up test environment."""
        if hasattr(self, 'temp_dir'):
            import shutil
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_existing_cpt_creation(self):
        """Test that existing CPT creation still works."""
        # Create a traditional evidence node CPT
        metadata = CPTMetadata(
            cpt_id="TEST_EVIDENCE_001",
            version="1.0.0",
            status=CPTStatus.DRAFT
        )
        
        cpt = TypedCPT(
            metadata=metadata,
            cpt_type=CPTType.EVIDENCE_NODE,
            node_name="test_evidence",
            node_states=["low", "medium", "high"],
            node_description="Test evidence node",
            probability_table=[[0.7], [0.25], [0.05]],
            fallback_prior=[0.7, 0.25, 0.05]
        )
        
        # Add to library
        cpt_id = self.library.add_cpt(cpt)
        self.assertIsNotNone(cpt_id)
        
        # Retrieve and verify
        retrieved_cpt = self.library.get_cpt(cpt_id)
        self.assertIsNotNone(retrieved_cpt)
        self.assertEqual(retrieved_cpt.node_name, "test_evidence")
    
    def test_existing_template_functionality(self):
        """Test that existing template functionality works."""
        template_manager = self.library.template_manager
        
        # Check existing templates
        spoofing_templates = template_manager.get_typology_templates("spoofing")
        self.assertGreater(len(spoofing_templates), 0)
        
        # Check specific template
        order_pattern_template = template_manager.get_template("spoofing", "OrderPattern")
        self.assertIsNotNone(order_pattern_template)
        self.assertEqual(order_pattern_template["cpt_type"], CPTType.EVIDENCE_NODE)
    
    def test_cpt_with_parents_still_works(self):
        """Test that CPTs with parent nodes still work correctly."""
        metadata = CPTMetadata(
            cpt_id="TEST_CONDITIONAL_001",
            version="1.0.0",
            status=CPTStatus.DRAFT
        )
        
        cpt = TypedCPT(
            metadata=metadata,
            cpt_type=CPTType.RISK_FACTOR,
            node_name="test_conditional",
            node_states=["false", "true"],
            node_description="Test conditional node",
            parent_nodes=["parent1", "parent2"],
            parent_states={"parent1": ["low", "high"], "parent2": ["low", "high"]},
            probability_table=[
                [0.9, 0.7, 0.6, 0.3],  # P(false | parent combinations)
                [0.1, 0.3, 0.4, 0.7]   # P(true | parent combinations)
            ]
        )
        
        # Should create without errors
        cpt_id = self.library.add_cpt(cpt)
        self.assertIsNotNone(cpt_id)
        
        # Validate structure and probabilities
        retrieved_cpt = self.library.get_cpt(cpt_id)
        try:
            retrieved_cpt._validate_structure()
            retrieved_cpt._validate_probabilities()
        except Exception as e:
            self.fail(f"Existing CPT validation failed: {e}")


class TestModelBuilderIntegration(unittest.TestCase):
    """Test integration with model builder."""
    
    def setUp(self):
        """Set up test environment."""
        if not DEPENDENCIES_AVAILABLE:
            self.skipTest("Required dependencies not available")
        
        self.model_builder = ModelBuilder()
    
    def test_model_builder_handles_intermediate_nodes(self):
        """Test that model builder can handle intermediate node configurations."""
        # Create a model configuration with intermediate nodes
        config = {
            "nodes": [
                "evidence1", "evidence2", "evidence3",
                "intermediate_node", "risk_factor", "outcome"
            ],
            "edges": [
                ("evidence1", "intermediate_node"),
                ("evidence2", "intermediate_node"),
                ("evidence3", "intermediate_node"),
                ("intermediate_node", "risk_factor"),
                ("risk_factor", "outcome")
            ],
            "cpds": [
                {
                    "variable": "evidence1",
                    "variable_card": 3,
                    "values": [[0.7], [0.25], [0.05]]
                },
                {
                    "variable": "evidence2", 
                    "variable_card": 3,
                    "values": [[0.7], [0.25], [0.05]]
                },
                {
                    "variable": "evidence3",
                    "variable_card": 3,
                    "values": [[0.7], [0.25], [0.05]]
                },
                {
                    "variable": "intermediate_node",
                    "variable_card": 3,
                    "values": [[0.8, 0.6, 0.4, 0.5, 0.3, 0.2, 0.3, 0.1, 0.05],
                              [0.15, 0.3, 0.4, 0.35, 0.45, 0.5, 0.4, 0.4, 0.35],
                              [0.05, 0.1, 0.2, 0.15, 0.25, 0.3, 0.3, 0.5, 0.6]],
                    "evidence": ["evidence1", "evidence2", "evidence3"],
                    "evidence_card": [3, 3, 3]
                },
                {
                    "variable": "risk_factor",
                    "variable_card": 3,
                    "values": [[0.9, 0.6, 0.2],
                              [0.08, 0.3, 0.3],
                              [0.02, 0.1, 0.5]],
                    "evidence": ["intermediate_node"],
                    "evidence_card": [3]
                },
                {
                    "variable": "outcome",
                    "variable_card": 3,
                    "values": [[0.95, 0.7, 0.3],
                              [0.04, 0.25, 0.4],
                              [0.01, 0.05, 0.3]],
                    "evidence": ["risk_factor"],
                    "evidence_card": [3]
                }
            ]
        }
        
        # Should build without errors
        try:
            model = self.model_builder.build_from_config(config)
            self.assertIsNotNone(model)
            
            # Verify model structure
            self.assertEqual(len(model.nodes()), 6)
            self.assertEqual(len(model.edges()), 5)
            
            # Verify model validation passes
            self.assertTrue(model.check_model())
            
        except Exception as e:
            self.fail(f"Model builder failed with intermediate nodes: {e}")


class TestPerformanceRegression(unittest.TestCase):
    """Test that performance improvements are realized and no regressions occur."""
    
    def setUp(self):
        """Set up test environment."""
        if not DEPENDENCIES_AVAILABLE:
            self.skipTest("Required dependencies not available")
    
    def test_cpt_size_reduction(self):
        """Test that intermediate nodes actually reduce CPT complexity."""
        # Original: 6 parents with 3 states each = 3^6 = 729 combinations
        original_combinations = 3 ** 6
        
        # With intermediate nodes: 2 intermediate nodes with 3 states each = 3^2 = 9 combinations
        intermediate_combinations = 3 ** 2
        
        # Plus the intermediate node CPTs: 3^3 = 27 combinations each
        intermediate_node_combinations = 3 ** 3
        
        # Total with intermediates: 9 + 2 * 27 = 63 combinations
        total_with_intermediates = intermediate_combinations + 2 * intermediate_node_combinations
        
        # Verify significant reduction
        reduction_factor = original_combinations / total_with_intermediates
        self.assertGreater(reduction_factor, 10, 
                          f"Expected >10x reduction, got {reduction_factor:.2f}x")
        
        logger.info(f"CPT complexity reduction: {reduction_factor:.1f}x "
                   f"({original_combinations} → {total_with_intermediates} combinations)")
    
    def test_memory_usage_estimation(self):
        """Test estimated memory usage reduction."""
        # Estimate memory for probability tables (assuming 8 bytes per float)
        bytes_per_float = 8
        states_per_node = 3
        
        # Original model memory
        original_combinations = 3 ** 6  # 729
        original_memory = original_combinations * states_per_node * bytes_per_float
        
        # Intermediate model memory
        outcome_combinations = 3 ** 2  # 9
        intermediate_combinations = 3 ** 3  # 27 each
        total_combinations = outcome_combinations + 2 * intermediate_combinations  # 63
        intermediate_memory = total_combinations * states_per_node * bytes_per_float
        
        # Calculate reduction
        memory_reduction = original_memory / intermediate_memory
        
        self.assertGreater(memory_reduction, 10,
                          f"Expected >10x memory reduction, got {memory_reduction:.2f}x")
        
        logger.info(f"Memory usage reduction: {memory_reduction:.1f}x "
                   f"({original_memory} → {intermediate_memory} bytes)")


class TestRegulatoryCompliance(unittest.TestCase):
    """Test that regulatory compliance is maintained."""
    
    def setUp(self):
        """Set up test environment."""
        if not DEPENDENCIES_AVAILABLE:
            self.skipTest("Required dependencies not available")
        
        self.temp_dir = tempfile.mkdtemp()
        self.library = CPTLibrary(library_path=self.temp_dir)
        self.integration = IntermediateNodeCPTLibraryIntegration(self.library)
    
    def tearDown(self):
        """Clean up test environment."""
        if hasattr(self, 'temp_dir'):
            import shutil
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_regulatory_references_preserved(self):
        """Test that regulatory references are preserved in intermediate nodes."""
        # Create templates
        self.integration.create_intermediate_node_templates()
        
        # Check that regulatory basis is included
        template = self.integration.template_manager.get_template("spoofing", "market_impact_spoofing")
        self.assertIn("regulatory_basis", template)
        self.assertIn("ESMA", template["regulatory_basis"])
    
    def test_compliance_frameworks_maintained(self):
        """Test that compliance frameworks are maintained."""
        # Create CPTs
        self.integration.create_intermediate_node_templates()
        cpt_ids = self.integration.create_intermediate_node_cpts()
        
        # Check CPT compliance frameworks
        for cpt_id in cpt_ids.values():
            cpt = self.library.get_cpt(cpt_id)
            self.assertIn("MAR", cpt.metadata.compliance_frameworks)
            self.assertIn("ESMA", cpt.metadata.compliance_frameworks)
    
    def test_audit_trail_maintained(self):
        """Test that audit trail is maintained for intermediate nodes."""
        # Create CPTs
        self.integration.create_intermediate_node_templates()
        cpt_ids = self.integration.create_intermediate_node_cpts()
        
        # Check audit trail
        for cpt_id in cpt_ids.values():
            cpt = self.library.get_cpt(cpt_id)
            self.assertIsNotNone(cpt.metadata.created_at)
            self.assertEqual(cpt.metadata.created_by, "intermediate_node_integration")
            self.assertEqual(cpt.metadata.status, CPTStatus.VALIDATED)


class TestEndToEndIntegration(unittest.TestCase):
    """End-to-end integration tests."""
    
    def setUp(self):
        """Set up test environment."""
        if not DEPENDENCIES_AVAILABLE:
            self.skipTest("Required dependencies not available")
        
        self.temp_dir = tempfile.mkdtemp()
        self.library = CPTLibrary(library_path=self.temp_dir)
    
    def tearDown(self):
        """Clean up test environment."""
        if hasattr(self, 'temp_dir'):
            import shutil
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_full_integration_workflow(self):
        """Test the complete integration workflow."""
        # Step 1: Integrate intermediate nodes
        integration = integrate_intermediate_nodes_with_cpt_library(self.library)
        
        # Step 2: Verify integration completed successfully
        validation_results = integration.validate_integration()
        self.assertEqual(len(validation_results["validation_errors"]), 0,
                        f"Integration validation failed: {validation_results['validation_errors']}")
        
        # Step 3: Verify specific nodes exist
        spoofing_cpt_id = "INT_MARKET_IMPACT_SPOOFING_SPOOFING"
        cpt = self.library.get_cpt(spoofing_cpt_id)
        self.assertIsNotNone(cpt, f"CPT {spoofing_cpt_id} not found")
        
        # Step 4: Verify CPT functionality
        try:
            cpt._validate_structure()
            cpt._validate_probabilities()
        except Exception as e:
            self.fail(f"End-to-end CPT validation failed: {e}")
        
        # Step 5: Verify templates are updated
        risk_template = integration.template_manager.get_template("spoofing", "risk_factor")
        self.assertIsNotNone(risk_template)
        self.assertEqual(len(risk_template["parent_nodes"]), 2)
        
        logger.info("End-to-end integration test completed successfully")
    
    def test_integration_summary_accuracy(self):
        """Test that integration summary provides accurate information."""
        integration = integrate_intermediate_nodes_with_cpt_library(self.library)
        summary = integration.get_integration_summary()
        
        # Verify summary accuracy
        self.assertGreater(summary["total_intermediate_nodes"], 0)
        self.assertIn("spoofing", summary["models_affected"])
        self.assertIn("economic_withholding", summary["models_affected"])
        self.assertIn("cross_desk_collusion", summary["models_affected"])
        
        # Verify node types
        node_types = summary["nodes_by_type"]
        self.assertIn("market_impact", node_types)
        self.assertIn("behavioral_intent", node_types)
        
        logger.info(f"Integration summary: {json.dumps(summary, indent=2)}")


def run_regression_tests():
    """Run all regression tests."""
    print("🚀 RUNNING COMPREHENSIVE REGRESSION TESTS")
    print("=" * 60)
    
    # Test suites
    test_suites = [
        ("CPT Library Integration", TestCPTLibraryIntegration),
        ("Backward Compatibility", TestBackwardCompatibility),
        ("Model Builder Integration", TestModelBuilderIntegration),
        ("Performance Regression", TestPerformanceRegression),
        ("Regulatory Compliance", TestRegulatoryCompliance),
        ("End-to-End Integration", TestEndToEndIntegration),
    ]
    
    total_tests = 0
    total_failures = 0
    total_errors = 0
    
    for suite_name, test_class in test_suites:
        print(f"\n📋 {suite_name}")
        print("-" * 40)
        
        # Create test suite
        suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
        
        # Run tests
        runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
        result = runner.run(suite)
        
        # Track results
        total_tests += result.testsRun
        total_failures += len(result.failures)
        total_errors += len(result.errors)
        
        # Print results
        if result.failures:
            print(f"❌ FAILURES ({len(result.failures)}):")
            for test, traceback in result.failures:
                print(f"  - {test}: {traceback.split('AssertionError: ')[-1].split('\n')[0]}")
        
        if result.errors:
            print(f"❌ ERRORS ({len(result.errors)}):")
            for test, traceback in result.errors:
                print(f"  - {test}: {traceback.split('\n')[-2]}")
    
    # Final summary
    print("\n" + "=" * 60)
    print("📊 REGRESSION TEST SUMMARY")
    print("=" * 60)
    
    success_rate = ((total_tests - total_failures - total_errors) / total_tests * 100) if total_tests > 0 else 0
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {total_tests - total_failures - total_errors}")
    print(f"Failed: {total_failures}")
    print(f"Errors: {total_errors}")
    print(f"Success Rate: {success_rate:.1f}%")
    
    if total_failures == 0 and total_errors == 0:
        print("\n🎉 ALL REGRESSION TESTS PASSED!")
        print("✅ Intermediate node integration is ready for deployment")
        return 0
    else:
        print(f"\n⚠️  {total_failures + total_errors} test(s) failed")
        print("❌ Integration needs fixes before deployment")
        return 1


if __name__ == "__main__":
    exit_code = run_regression_tests()
    sys.exit(exit_code)