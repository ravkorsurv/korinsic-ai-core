#!/usr/bin/env python3
"""
Simple Enhanced Cross Desk Collusion Model Validation

Validates the enhanced 4-parent CPT structure configuration for cross desk collusion.
Tests the basic structure and explaining away patterns in the model configuration.
"""

import json
import sys

def test_cross_desk_collusion_configuration():
    """Test that the enhanced cross desk collusion model is properly configured"""
    print("Testing enhanced cross desk collusion model configuration...")
    
    try:
        # Load the model configuration
        with open('config/bayesian_model_config.json', 'r') as f:
            config = json.load(f)
        
        print("✅ Configuration file loaded successfully")
        
        # Check that cross_desk_collusion model exists
        if "cross_desk_collusion" not in config["models"]:
            print("❌ cross_desk_collusion model not found in configuration")
            return False
        
        collusion_config = config["models"]["cross_desk_collusion"]
        print("✅ cross_desk_collusion model found")
        
        # Check required sections
        required_sections = ["nodes", "edges", "cpds"]
        for section in required_sections:
            if section not in collusion_config:
                print(f"❌ Missing required section: {section}")
                return False
        print("✅ All required sections present")
        
        # Check node structure
        nodes = {node["name"]: node for node in collusion_config["nodes"]}
        
        # Check evidence nodes (4 parents)
        evidence_nodes = ["CommunicationPatterns", "TradingCoordination", "InformationAdvantage", "EconomicBenefit"]
        for node_name in evidence_nodes:
            if node_name not in nodes:
                print(f"❌ Missing evidence node: {node_name}")
                return False
        print("✅ All 4 evidence nodes present")
        
        # Check intermediate nodes
        intermediate_nodes = ["CoordinationPatterns", "InformationAdvantageNode"]
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
        edges = collusion_config["edges"]
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
        
        # InformationAdvantageNode should have 2 parents
        if len(edge_dict.get("InformationAdvantageNode", [])) != 2:
            print(f"❌ InformationAdvantageNode should have 2 parents, found {len(edge_dict.get('InformationAdvantageNode', []))}")
            return False
        
        # Risk should have 2 parents (intermediate nodes)
        if len(edge_dict.get("Risk", [])) != 2:
            print(f"❌ Risk should have 2 parents, found {len(edge_dict.get('Risk', []))}")
            return False
        
        print("✅ Edge structure supports explaining away")
        
        # Verify specific parent-child relationships
        coordination_parents = edge_dict.get("CoordinationPatterns", [])
        if "CommunicationPatterns" not in coordination_parents or "TradingCoordination" not in coordination_parents:
            print("❌ CoordinationPatterns should have CommunicationPatterns and TradingCoordination as parents")
            return False
        
        info_advantage_parents = edge_dict.get("InformationAdvantageNode", [])
        if "InformationAdvantage" not in info_advantage_parents or "EconomicBenefit" not in info_advantage_parents:
            print("❌ InformationAdvantageNode should have InformationAdvantage and EconomicBenefit as parents")
            return False
        
        risk_parents = edge_dict.get("Risk", [])
        if "CoordinationPatterns" not in risk_parents or "InformationAdvantageNode" not in risk_parents:
            print("❌ Risk should have CoordinationPatterns and InformationAdvantageNode as parents")
            return False
        
        print("✅ Parent-child relationships correctly configured")
        
        # Check CPD completeness
        cpd_variables = {cpd["variable"] for cpd in collusion_config["cpds"]}
        node_names = {node["name"] for node in collusion_config["nodes"]}
        
        if cpd_variables != node_names:
            print("❌ CPD variables don't match node names")
            print(f"   Nodes: {node_names}")
            print(f"   CPDs: {cpd_variables}")
            return False
        
        print("✅ All nodes have corresponding CPDs")
        
        # Check probability distributions
        for cpd in collusion_config["cpds"]:
            values = cpd["values"]
            for col_idx in range(len(values[0])):
                column_sum = sum(values[row][col_idx] for row in range(len(values)))
                if abs(column_sum - 1.0) > 0.001:
                    print(f"❌ CPD for {cpd['variable']} column {col_idx} doesn't sum to 1 (sum={column_sum})")
                    return False
        
        print("✅ All probability distributions sum to 1")
        
        # Test explaining away pattern in Risk CPT
        risk_cpd = next(cpd for cpd in collusion_config["cpds"] if cpd["variable"] == "Risk")
        risk_values = risk_cpd["values"]
        
        # Check that we have the right structure (3 states x 9 combinations)
        if len(risk_values) != 3 or len(risk_values[0]) != 9:
            print(f"❌ Risk CPT should be 3x9, found {len(risk_values)}x{len(risk_values[0])}")
            return False
        
        # Test explaining away: both parents high should give higher risk than individual parents
        high_risk_both_high = risk_values[2][8]  # Both parents in highest state
        high_risk_coordination_only = risk_values[2][6]  # CoordinationPatterns high, InformationAdvantageNode low
        high_risk_info_only = risk_values[2][2]  # InformationAdvantageNode high, CoordinationPatterns low
        
        if high_risk_both_high <= high_risk_coordination_only or high_risk_both_high <= high_risk_info_only:
            print("❌ Explaining away pattern not properly implemented in Risk CPT")
            print(f"   Both high: {high_risk_both_high}")
            print(f"   Coordination only: {high_risk_coordination_only}")
            print(f"   Information only: {high_risk_info_only}")
            return False
        
        print("✅ Explaining away pattern correctly implemented")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        return False

def test_explaining_away_patterns():
    """Test specific explaining away patterns for cross desk collusion"""
    print("\nTesting cross desk collusion explaining away patterns...")
    
    try:
        # Load the model configuration
        with open('config/bayesian_model_config.json', 'r') as f:
            config = json.load(f)
        
        collusion_config = config["models"]["cross_desk_collusion"]
        
        # Test CoordinationPatterns explaining away
        coordination_cpd = next(cpd for cpd in collusion_config["cpds"] if cpd["variable"] == "CoordinationPatterns")
        coordination_values = coordination_cpd["values"]
        
        # When both CommunicationPatterns and TradingCoordination are high, coordination should be high
        # This explains away individual suspicious indicators
        high_coord_both_high = coordination_values[2][8]  # Both parents high
        high_coord_comm_only = coordination_values[2][6]  # CommunicationPatterns high only
        high_coord_trading_only = coordination_values[2][2]  # TradingCoordination high only
        
        if high_coord_both_high <= high_coord_comm_only or high_coord_both_high <= high_coord_trading_only:
            print("❌ CoordinationPatterns explaining away not properly implemented")
            print(f"   Both high: {high_coord_both_high}")
            print(f"   Comm only: {high_coord_comm_only}")
            print(f"   Trading only: {high_coord_trading_only}")
            return False
        
        print("✅ CoordinationPatterns explaining away correctly implemented")
        
        # Test InformationAdvantageNode explaining away
        info_cpd = next(cpd for cpd in collusion_config["cpds"] if cpd["variable"] == "InformationAdvantageNode")
        info_values = info_cpd["values"]
        
        # When both InformationAdvantage and EconomicBenefit are high, information advantage should be high
        high_info_both_high = info_values[2][8]  # Both parents high
        high_info_advantage_only = info_values[2][6]  # InformationAdvantage high only
        high_info_benefit_only = info_values[2][2]  # EconomicBenefit high only
        
        if high_info_both_high <= high_info_advantage_only or high_info_both_high <= high_info_benefit_only:
            print("❌ InformationAdvantageNode explaining away not properly implemented")
            print(f"   Both high: {high_info_both_high}")
            print(f"   Advantage only: {high_info_advantage_only}")
            print(f"   Benefit only: {high_info_benefit_only}")
            return False
        
        print("✅ InformationAdvantageNode explaining away correctly implemented")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing explaining away patterns: {str(e)}")
        return False

def test_collusion_specific_patterns():
    """Test collusion-specific explaining away patterns"""
    print("\nTesting collusion-specific explaining away patterns...")
    
    try:
        # Load the model configuration
        with open('config/bayesian_model_config.json', 'r') as f:
            config = json.load(f)
        
        collusion_config = config["models"]["cross_desk_collusion"]
        
        # Test that communication evidence has low prior (hard to detect)
        comm_cpd = next(cpd for cpd in collusion_config["cpds"] if cpd["variable"] == "CommunicationPatterns")
        comm_values = comm_cpd["values"]
        
        # Communication patterns should have very low prior for highly suspicious (0.03)
        highly_suspicious_prior = comm_values[2][0]
        if highly_suspicious_prior > 0.05:
            print(f"❌ CommunicationPatterns highly suspicious prior too high: {highly_suspicious_prior}")
            return False
        
        print("✅ Communication patterns have appropriately low suspicious priors")
        
        # Test that when strong communication evidence exists, it explains away profit patterns
        risk_cpd = next(cpd for cpd in collusion_config["cpds"] if cpd["variable"] == "Risk")
        risk_values = risk_cpd["values"]
        
        # Strong coordination + clear information advantage should give very high risk
        max_risk_prob = risk_values[2][8]  # Both intermediate nodes high
        if max_risk_prob < 0.5:
            print(f"❌ Maximum risk probability too low: {max_risk_prob}")
            return False
        
        print("✅ Strong evidence combination produces high risk assessment")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing collusion patterns: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🧪 ENHANCED CROSS DESK COLLUSION MODEL VALIDATION")
    print("=" * 60)
    
    tests = [
        ("Model Configuration", test_cross_desk_collusion_configuration),
        ("Explaining Away Patterns", test_explaining_away_patterns),
        ("Collusion-Specific Patterns", test_collusion_specific_patterns)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 40)
        
        if test_func():
            print(f"✅ {test_name} PASSED")
            passed += 1
        else:
            print(f"❌ {test_name} FAILED")
    
    print("\n" + "=" * 60)
    print(f"SUMMARY: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - Enhanced cross desk collusion model is properly configured!")
        return 0
    else:
        print("💥 SOME TESTS FAILED - Check configuration")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)