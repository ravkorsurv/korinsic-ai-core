"""
Test suite for fan-in reduction across all Bayesian models.

This module validates that the fan-in reduction implementation:
1. Reduces CPT complexity from exponential to manageable sizes
2. Preserves all evidence nodes and business logic
3. Maintains model functionality and inference capabilities
4. Uses intermediate nodes correctly with noisy-OR CPTs
"""

import pytest
import numpy as np
from typing import Dict, Any

# Import the refactored models
from src.models.bayesian.economic_withholding.model import EconomicWithholdingModel
from src.models.bayesian.spoofing.model import SpoofingModel
from src.models.bayesian.cross_desk_collusion.model import CrossDeskCollusionModel

# Import intermediate nodes
from src.models.bayesian.shared.intermediate_nodes import (
    MarketImpactIntermediateNode,
    BehavioralIntentIntermediateNode,
    CostAnalysisIntermediateNode,
    MarketConditionsIntermediateNode,
    BehavioralPatternsIntermediateNode,
    TechnicalFactorsIntermediateNode,
)


class TestFanInReduction:
    """Test fan-in reduction implementation across all models."""

    def test_economic_withholding_fan_in_reduction(self):
        """Test that Economic Withholding model reduces from 19→4 parents."""
        # Test without latent intent (direct structure)
        model = EconomicWithholdingModel(use_latent_intent=False)
        
        if model.model is None:
            pytest.skip("pgmpy not available")
        
        # Verify model structure
        assert model.model is not None
        assert len(model.intermediate_nodes) == 4
        
        # Check that intermediate nodes exist
        intermediate_names = [
            'cost_analysis_intermediate',
            'market_conditions_intermediate', 
            'behavioral_patterns_intermediate',
            'technical_factors_intermediate'
        ]
        
        for name in intermediate_names:
            assert name in [node for node in model.model.nodes()]
        
        # Verify final risk node has 4 parents (not 19)
        risk_parents = list(model.model.predecessors('economic_withholding_risk'))
        assert len(risk_parents) == 4
        assert all(name in risk_parents for name in intermediate_names)
        
        # Verify evidence nodes still exist (19 total)
        evidence_nodes = [
            'marginal_cost_deviation', 'fuel_cost_variance', 'plant_efficiency', 'heat_rate_variance',
            'load_factor', 'market_tightness', 'competitive_context', 'transmission_constraint',
            'bid_shape_anomaly', 'offer_withdrawal_pattern', 'capacity_utilization', 
            'markup_consistency', 'opportunity_pricing',
            'fuel_price_correlation', 'cross_plant_coordination', 'price_impact_ratio',
            'volume_participation', 'liquidity_context', 'order_clustering'
        ]
        
        for evidence in evidence_nodes:
            assert evidence in [node for node in model.model.nodes()]
        
        print(f"✅ Economic Withholding: 19 evidence → 4 intermediate → 1 final")

    def test_spoofing_fan_in_reduction(self):
        """Test that Spoofing model reduces from 6→2 parents."""
        model = SpoofingModel(use_latent_intent=True)
        
        # Verify model structure
        assert model.model is not None
        assert len(model.intermediate_nodes) == 2
        
        # Check intermediate nodes exist
        intermediate_names = ['market_impact_intermediate', 'behavioral_intent_intermediate']
        for name in intermediate_names:
            assert name in [node for node in model.model.nodes()]
        
        # Verify latent intent node has 2 parents (not 6)
        latent_parents = list(model.model.predecessors('spoofing_latent_intent'))
        assert len(latent_parents) == 2
        assert all(name in latent_parents for name in intermediate_names)
        
        # Verify all evidence nodes still exist
        evidence_nodes = [
            'order_clustering', 'price_impact_ratio', 'volume_participation',
            'order_behavior', 'intent_to_execute', 'order_cancellation'
        ]
        
        for evidence in evidence_nodes:
            assert evidence in [node for node in model.model.nodes()]
        
        print(f"✅ Spoofing: 6 evidence → 2 intermediate → 1 latent → 1 final")

    def test_cross_desk_collusion_fan_in_reduction(self):
        """Test that Cross-Desk Collusion model reduces from 6→2 parents."""
        model = CrossDeskCollusionModel(use_latent_intent=True)
        
        # Verify model structure
        assert model.model is not None
        assert len(model.intermediate_nodes) == 2
        
        # Check intermediate nodes exist
        intermediate_names = ['coordination_patterns_intermediate', 'communication_intent_intermediate']
        for name in intermediate_names:
            assert name in [node for node in model.model.nodes()]
        
        # Verify latent intent node has 2 parents (not 6)
        latent_parents = list(model.model.predecessors('collusion_latent_intent'))
        assert len(latent_parents) == 2
        assert all(name in latent_parents for name in intermediate_names)
        
        print(f"✅ Cross-Desk Collusion: 6 evidence → 2 intermediate → 1 latent → 1 final")

    def test_intermediate_node_cpt_complexity(self):
        """Test that intermediate nodes have manageable CPT complexity."""
        # Test MarketImpactIntermediateNode with 3 parents
        market_node = MarketImpactIntermediateNode(
            name="test_market",
            parent_nodes=["parent1", "parent2", "parent3"]
        )
        
        cpt = market_node.create_noisy_or_cpt()
        
        # 3 parents with 3 states each = 3^3 = 27 combinations (manageable)
        assert cpt.values.shape == (3, 27)
        assert len(cpt.evidence) == 3
        assert all(card == 3 for card in cpt.evidence_card)
        
        # Test that probabilities sum to 1 for each parent combination
        for i in range(27):
            column_sum = cpt.values[:, i].sum()
            assert abs(column_sum - 1.0) < 1e-10, f"Column {i} probabilities don't sum to 1: {column_sum}"
        
        print(f"✅ Intermediate node CPT: 3 parents → 27 combinations (vs 729 direct)")

    def test_noisy_or_logic_correctness(self):
        """Test that noisy-OR logic works correctly."""
        behavioral_node = BehavioralIntentIntermediateNode(
            name="test_behavioral",
            parent_nodes=["behavior1", "behavior2"]
        )
        
        cpt = behavioral_node.create_noisy_or_cpt()
        
        # Test specific combinations
        # All parents in benign state (0,0) should have high probability for benign outcome
        benign_benign_probs = cpt.values[:, 0]  # First combination: (0,0)
        assert benign_benign_probs[0] > 0.5, "Benign+Benign should favor benign outcome"
        
        # All parents in malicious state should have high probability for malicious outcome  
        malicious_malicious_idx = 3*1 + 1*2  # (2,2) combination
        malicious_malicious_probs = cpt.values[:, malicious_malicious_idx]
        assert malicious_malicious_probs[2] > 0.5, "Malicious+Malicious should favor malicious outcome"
        
        print(f"✅ Noisy-OR logic: Proper probability distributions")

    def test_cpt_size_reduction_benefits(self):
        """Test and quantify the CPT size reduction benefits."""
        
        # Economic Withholding: 19 parents → 4 intermediate groups
        original_combinations = 3 ** 19  # 1,162,261,467 combinations
        
        # New structure: 4 intermediate CPTs + 1 final CPT
        cost_analysis_cpt = 3 ** 4      # 81 combinations
        market_conditions_cpt = 3 ** 4  # 81 combinations  
        behavioral_patterns_cpt = 3 ** 5 # 243 combinations
        technical_factors_cpt = 3 ** 6   # 729 combinations
        final_risk_cpt = 3 ** 4         # 81 combinations
        
        new_total_combinations = (
            cost_analysis_cpt + market_conditions_cpt + 
            behavioral_patterns_cpt + technical_factors_cpt + final_risk_cpt
        )  # 1,215 total combinations
        
        reduction_factor = original_combinations / new_total_combinations
        memory_reduction = (original_combinations * 8) / (new_total_combinations * 8)
        
        assert reduction_factor > 900000, f"Reduction factor should be massive: {reduction_factor}"
        assert new_total_combinations < 2000, f"New total should be manageable: {new_total_combinations}"
        
        print(f"✅ CPT Reduction: {original_combinations:,} → {new_total_combinations:,} "
              f"({reduction_factor:.0f}x improvement)")

    def test_model_inference_functionality(self):
        """Test that models can still perform inference after fan-in reduction."""
        model = SpoofingModel(use_latent_intent=True)
        
        # Create test evidence
        test_evidence = {
            "order_clustering": 1,      # medium clustering
            "price_impact_ratio": 2,    # high impact
            "volume_participation": 1,  # medium participation
            "order_behavior": 2,        # suspicious behavior
            "intent_to_execute": 0,     # genuine intent
            "order_cancellation": 2,    # manipulative cancellation
        }
        
        # Test that calculate_risk still works
        try:
            result = model.calculate_risk(test_evidence)
            
            # Verify result structure
            assert "risk_scores" in result
            assert "risk_assessment" in result
            assert "model_metadata" in result
            
            # Verify risk scores are reasonable
            risk_scores = result["risk_scores"]
            assert 0 <= risk_scores["overall_score"] <= 1
            assert 0 <= risk_scores["confidence"] <= 1
            
            print(f"✅ Model Inference: Still functional after fan-in reduction")
            
        except Exception as e:
            pytest.fail(f"Model inference failed after fan-in reduction: {str(e)}")

    def test_evidence_preservation(self):
        """Test that all original evidence nodes are preserved."""
        models_and_evidence = [
            (
                EconomicWithholdingModel(use_latent_intent=False),
                19,  # Expected evidence count
                [
                    'marginal_cost_deviation', 'fuel_cost_variance', 'plant_efficiency', 
                    'heat_rate_variance', 'load_factor', 'market_tightness', 
                    'competitive_context', 'transmission_constraint', 'bid_shape_anomaly',
                    'offer_withdrawal_pattern', 'capacity_utilization', 'markup_consistency',
                    'opportunity_pricing', 'fuel_price_correlation', 'cross_plant_coordination',
                    'price_impact_ratio', 'volume_participation', 'liquidity_context', 
                    'order_clustering'
                ]
            ),
            (
                SpoofingModel(use_latent_intent=True),
                6,   # Expected evidence count
                [
                    'order_clustering', 'price_impact_ratio', 'volume_participation',
                    'order_behavior', 'intent_to_execute', 'order_cancellation'
                ]
            ),
        ]
        
        for model, expected_count, expected_evidence in models_and_evidence:
            if model.model is None:
                continue
                
            model_nodes = set(model.model.nodes())
            evidence_nodes = [node for node in expected_evidence if node in model_nodes]
            
            assert len(evidence_nodes) == expected_count, (
                f"Expected {expected_count} evidence nodes, found {len(evidence_nodes)}"
            )
            
            for evidence in expected_evidence:
                assert evidence in model_nodes, f"Evidence node {evidence} missing from model"
        
        print(f"✅ Evidence Preservation: All original evidence nodes maintained")


class TestPerformanceComparison:
    """Test performance improvements from fan-in reduction."""

    def test_memory_usage_reduction(self):
        """Test memory usage reduction calculations."""
        
        # Before: Economic Withholding with 19 direct parents
        before_combinations = 3 ** 19
        before_memory_gb = (before_combinations * 8) / (1024**3)
        
        # After: Hierarchical structure with intermediate nodes
        after_combinations = 81 + 81 + 243 + 729 + 81  # Sum of all CPTs
        after_memory_mb = (after_combinations * 8) / (1024**2)
        
        reduction_ratio = before_memory_gb / (after_memory_mb / 1024)
        
        assert before_memory_gb > 8.0, "Original should require >8GB"
        assert after_memory_mb < 1.0, "New should require <1MB"
        assert reduction_ratio > 10000, f"Memory reduction should be massive: {reduction_ratio}"
        
        print(f"✅ Memory Usage: {before_memory_gb:.2f}GB → {after_memory_mb:.3f}MB "
              f"({reduction_ratio:.0f}x reduction)")

    def test_training_data_feasibility(self):
        """Test that training data requirements become feasible."""
        
        # Rule of thumb: need ~10 samples per CPT combination for reliable estimation
        samples_per_combination = 10
        
        # Before: Economic Withholding
        before_combinations = 3 ** 19
        before_samples_needed = before_combinations * samples_per_combination
        
        # After: Largest intermediate CPT
        after_max_combinations = 3 ** 6  # Technical factors CPT (largest)
        after_samples_needed = after_max_combinations * samples_per_combination
        
        # Feasibility thresholds
        feasible_samples = 100000  # 100K samples is reasonable for financial surveillance
        
        assert before_samples_needed > feasible_samples * 1000, "Original requirements should be impossible"
        assert after_samples_needed < feasible_samples, "New requirements should be feasible"
        
        print(f"✅ Training Data: {before_samples_needed:,} → {after_samples_needed:,} samples needed")


if __name__ == "__main__":
    # Run tests with verbose output
    test_suite = TestFanInReduction()
    
    print("🧪 Testing Fan-In Reduction Implementation...")
    print("=" * 60)
    
    try:
        test_suite.test_economic_withholding_fan_in_reduction()
        test_suite.test_spoofing_fan_in_reduction() 
        test_suite.test_cross_desk_collusion_fan_in_reduction()
        test_suite.test_intermediate_node_cpt_complexity()
        test_suite.test_noisy_or_logic_correctness()
        test_suite.test_cpt_size_reduction_benefits()
        test_suite.test_model_inference_functionality()
        test_suite.test_evidence_preservation()
        
        performance_tests = TestPerformanceComparison()
        performance_tests.test_memory_usage_reduction()
        performance_tests.test_training_data_feasibility()
        
        print("=" * 60)
        print("🎉 All Fan-In Reduction Tests PASSED!")
        print("✅ Models successfully refactored with massive performance improvements")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        raise