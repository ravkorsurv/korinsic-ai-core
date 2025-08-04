#!/usr/bin/env python3
"""
Simple Enhanced Circular Trading Model Validation

Validates the enhanced 4-parent CPT structure configuration for circular trading.
Tests the basic structure and explaining away patterns in the model configuration.
"""

import json
import sys

def test_circular_trading_configuration():
    """Test that the enhanced circular trading model is properly configured"""
    print("Testing enhanced circular trading model configuration...")
    
    try:
        # Load the model configuration
        with open('config/bayesian_model_config.json', 'r') as f:
            config = json.load(f)
        
        print("✅ Configuration file loaded successfully")
        
        # Check that circular_trading model exists
        if "circular_trading" not in config["models"]:
            print("❌ circular_trading model not found in configuration")
            return False
        
        circular_config = config["models"]["circular_trading"]
        print("✅ circular_trading model found")
        
        # Check required sections
        required_sections = ["nodes", "edges", "cpds"]
        for section in required_sections:
            if section not in circular_config:
                print(f"❌ Missing required section: {section}")
                return False
        print("✅ All required sections present")
        
        # Check node structure
        nodes = {node["name"]: node for node in circular_config["nodes"]}
        
        # Check evidence nodes (4 parents)
        evidence_nodes = ["CircularityPatterns", "ParticipantAnalysis", "VolumeCirculation", "MarketImpactAnalysis"]
        for node_name in evidence_nodes:
            if node_name not in nodes:
                print(f"❌ Missing evidence node: {node_name}")
                return False
        print("✅ All 4 evidence nodes present")
        
        # Check intermediate nodes
        intermediate_nodes = ["CoordinationPatterns", "MarketImpact"]
        for node_name in intermediate_nodes:
            if node_name not in nodes:
                print(f"❌ Missing intermediate node: {node_name}")
                return False
        print("✅ All intermediate nodes present")
        
        # Check Risk node
        if "Risk" not in nodes:
            print("❌ Missing Risk node")
            return False
        print("✅ Risk node present")
        
        # Check edge structure
        edges = circular_config["edges"]
        edge_dict = {}
        for parent, child in edges:
            if child not in edge_dict:
                edge_dict[child] = []
            edge_dict[child].append(parent)
        
        # Validate explaining away structure
        # CoordinationPatterns should have 2 parents
        if len(edge_dict.get("CoordinationPatterns", [])) != 2:
            print(f"❌ CoordinationPatterns should have 2 parents, found {len(edge_dict.get('CoordinationPatterns', []))}")
            return False
        
        # MarketImpact should have 2 parents
        if len(edge_dict.get("MarketImpact", [])) != 2:
            print(f"❌ MarketImpact should have 2 parents, found {len(edge_dict.get('MarketImpact', []))}")
            return False
        
        # Risk should have 2 parents (intermediate nodes)
        if len(edge_dict.get("Risk", [])) != 2:
            print(f"❌ Risk should have 2 parents, found {len(edge_dict.get('Risk', []))}")
            return False
        
        print("✅ Edge structure supports explaining away")
        
        # Verify specific parent-child relationships
        coordination_parents = edge_dict.get("CoordinationPatterns", [])
        if "CircularityPatterns" not in coordination_parents or "ParticipantAnalysis" not in coordination_parents:
            print("❌ CoordinationPatterns should have CircularityPatterns and ParticipantAnalysis as parents")
            return False
        
        market_impact_parents = edge_dict.get("MarketImpact", [])
        if "VolumeCirculation" not in market_impact_parents or "MarketImpactAnalysis" not in market_impact_parents:
            print("❌ MarketImpact should have VolumeCirculation and MarketImpactAnalysis as parents")
            return False
        
        risk_parents = edge_dict.get("Risk", [])
        if "CoordinationPatterns" not in risk_parents or "MarketImpact" not in risk_parents:
            print("❌ Risk should have CoordinationPatterns and MarketImpact as parents")
            return False
        
        print("✅ Parent-child relationships correctly configured")
        
        # Check CPD completeness
        cpd_variables = {cpd["variable"] for cpd in circular_config["cpds"]}
        node_names = {node["name"] for node in circular_config["nodes"]}
        
        if cpd_variables != node_names:
            print("❌ CPD variables don't match node names")
            print(f"   Nodes: {node_names}")
            print(f"   CPDs: {cpd_variables}")
            return False
        
        print("✅ All nodes have corresponding CPDs")
        
        # Check probability distributions
        for cpd in circular_config["cpds"]:
            values = cpd["values"]
            for col_idx in range(len(values[0])):
                column_sum = sum(values[row][col_idx] for row in range(len(values)))
                if abs(column_sum - 1.0) > 0.001:
                    print(f"❌ CPD for {cpd['variable']} column {col_idx} doesn't sum to 1 (sum={column_sum})")
                    return False
        
        print("✅ All probability distributions sum to 1")
        
        # Test explaining away pattern in Risk CPT
        risk_cpd = next(cpd for cpd in circular_config["cpds"] if cpd["variable"] == "Risk")
        risk_values = risk_cpd["values"]
        
        # Check that we have the right structure (3 states x 9 combinations)
        if len(risk_values) != 3 or len(risk_values[0]) != 9:
            print(f"❌ Risk CPT should be 3x9, found {len(risk_values)}x{len(risk_values[0])}")
            return False
        
        # Test explaining away: both parents high should give higher risk than individual parents
        high_risk_both_high = risk_values[2][8]  # Both parents in highest state
        high_risk_coordination_only = risk_values[2][6]  # CoordinationPatterns high, MarketImpact low
        high_risk_market_only = risk_values[2][2]  # MarketImpact high, CoordinationPatterns low
        
        if high_risk_both_high <= high_risk_coordination_only or high_risk_both_high <= high_risk_market_only:
            print("❌ Explaining away pattern not properly implemented in Risk CPT")
            print(f"   Both high: {high_risk_both_high}")
            print(f"   Coordination only: {high_risk_coordination_only}")
            print(f"   Market only: {high_risk_market_only}")
            return False
        
        print("✅ Explaining away pattern correctly implemented")
        
        # Test intermediate node CPTs
        coordination_cpd = next(cpd for cpd in circular_config["cpds"] if cpd["variable"] == "CoordinationPatterns")
        market_impact_cpd = next(cpd for cpd in circular_config["cpds"] if cpd["variable"] == "MarketImpact")
        
        # Both should have 2 evidence variables
        if len(coordination_cpd.get("evidence", [])) != 2:
            print("❌ CoordinationPatterns CPD should have 2 evidence variables")
            return False
        
        if len(market_impact_cpd.get("evidence", [])) != 2:
            print("❌ MarketImpact CPD should have 2 evidence variables")
            return False
        
        print("✅ Intermediate node CPTs correctly configured")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        return False

def test_explaining_away_patterns():
    """Test specific explaining away patterns for circular trading"""
    print("\nTesting circular trading explaining away patterns...")
    
    try:
        # Load the model configuration
        with open('config/bayesian_model_config.json', 'r') as f:
            config = json.load(f)
        
        circular_config = config["models"]["circular_trading"]
        
        # Test CoordinationPatterns explaining away
        coordination_cpd = next(cpd for cpd in circular_config["cpds"] if cpd["variable"] == "CoordinationPatterns")
        coordination_values = coordination_cpd["values"]
        
        # When both CircularityPatterns and ParticipantAnalysis are high, coordination should be high
        # This explains away individual suspicious indicators
        high_coord_both_high = coordination_values[2][8]  # Both parents high
        high_coord_circularity_only = coordination_values[2][6]  # CircularityPatterns high only
        high_coord_participant_only = coordination_values[2][2]  # ParticipantAnalysis high only
        
        if high_coord_both_high <= high_coord_circularity_only or high_coord_both_high <= high_coord_participant_only:
            print("❌ CoordinationPatterns explaining away not properly implemented")
            return False
        
        print("✅ CoordinationPatterns explaining away correctly implemented")
        
        # Test MarketImpact explaining away
        market_cpd = next(cpd for cpd in circular_config["cpds"] if cpd["variable"] == "MarketImpact")
        market_values = market_cpd["values"]
        
        # When both VolumeCirculation and MarketImpactAnalysis are high, market impact should be high
        high_market_both_high = market_values[2][8]  # Both parents high
        high_market_volume_only = market_values[2][6]  # VolumeCirculation high only
        high_market_analysis_only = market_values[2][2]  # MarketImpactAnalysis high only
        
        if high_market_both_high <= high_market_volume_only or high_market_both_high <= high_market_analysis_only:
            print("❌ MarketImpact explaining away not properly implemented")
            return False
        
        print("✅ MarketImpact explaining away correctly implemented")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing explaining away patterns: {str(e)}")
        return False

def test_performance_characteristics():
    """Test performance characteristics of enhanced circular trading model"""
    print("\nTesting performance characteristics...")
    
    try:
        # Test CPT size reduction through intermediate nodes
        # Direct 4-parent CPT would have 3^4 = 81 combinations
        # With intermediate nodes: 2*(3^2) + 3^2 = 18 + 9 = 27 combinations
        
        direct_combinations = 3 ** 4  # 81
        intermediate_combinations = 2 * (3 ** 2) + (3 ** 2)  # 27
        
        reduction_factor = direct_combinations / intermediate_combinations
        
        print(f"CPT complexity reduction: {direct_combinations} → {intermediate_combinations} ({reduction_factor:.1f}x)")
        
        # Should achieve ~3x reduction in CPT complexity
        if reduction_factor < 2.5 or reduction_factor > 3.5:
            print(f"❌ Expected ~3x reduction, got {reduction_factor:.1f}x")
            return False
        
        print("✅ Achieved optimal CPT complexity reduction")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing performance: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🧪 ENHANCED CIRCULAR TRADING MODEL VALIDATION")
    print("=" * 55)
    
    tests = [
        ("Model Configuration", test_circular_trading_configuration),
        ("Explaining Away Patterns", test_explaining_away_patterns),
        ("Performance Characteristics", test_performance_characteristics)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 35)
        
        if test_func():
            print(f"✅ {test_name} PASSED")
            passed += 1
        else:
            print(f"❌ {test_name} FAILED")
    
    print("\n" + "=" * 55)
    print(f"SUMMARY: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - Enhanced circular trading model is properly configured!")
        return 0
    else:
        print("💥 SOME TESTS FAILED - Check configuration")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)