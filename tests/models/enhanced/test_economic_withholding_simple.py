#!/usr/bin/env python3
"""
Simple Enhanced Economic Withholding Model Validation

Validates the enhanced 4-parent CPT structure configuration for economic withholding.
Tests the basic structure and explaining away patterns in the model configuration.
"""

import json
import sys

def test_economic_withholding_configuration():
    """Test that the enhanced economic withholding model is properly configured"""
    print("Testing enhanced economic withholding model configuration...")
    
    try:
        # Load the model configuration
        with open('config/bayesian_model_config.json', 'r') as f:
            config = json.load(f)
        
        print("✅ Configuration file loaded successfully")
        
        # Check that economic_withholding model exists
        if "economic_withholding" not in config["models"]:
            print("❌ economic_withholding model not found in configuration")
            return False
        
        withholding_config = config["models"]["economic_withholding"]
        print("✅ economic_withholding model found")
        
        # Check required sections
        required_sections = ["nodes", "edges", "cpds"]
        for section in required_sections:
            if section not in withholding_config:
                print(f"❌ Missing required section: {section}")
                return False
        print("✅ All required sections present")
        
        # Check node structure
        nodes = {node["name"]: node for node in withholding_config["nodes"]}
        
        # Check evidence nodes (4 parents)
        evidence_nodes = ["CapacityAnalysis", "CostStructure", "MarketConditions", "StrategicBehavior"]
        for node_name in evidence_nodes:
            if node_name not in nodes:
                print(f"❌ Missing evidence node: {node_name}")
                return False
        print("✅ All 4 evidence nodes present")
        
        # Check intermediate nodes
        intermediate_nodes = ["EconomicRationality", "BehavioralIntent"]
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
        edges = withholding_config["edges"]
        edge_dict = {}
        for parent, child in edges:
            if child not in edge_dict:
                edge_dict[child] = []
            edge_dict[child].append(parent)
        
        # Validate explaining away structure
        # EconomicRationality should have 2 parents
        if len(edge_dict.get("EconomicRationality", [])) != 2:
            print(f"❌ EconomicRationality should have 2 parents, found {len(edge_dict.get('EconomicRationality', []))}")
            return False
        
        # BehavioralIntent should have 2 parents
        if len(edge_dict.get("BehavioralIntent", [])) != 2:
            print(f"❌ BehavioralIntent should have 2 parents, found {len(edge_dict.get('BehavioralIntent', []))}")
            return False
        
        # Risk should have 2 parents (intermediate nodes)
        if len(edge_dict.get("Risk", [])) != 2:
            print(f"❌ Risk should have 2 parents, found {len(edge_dict.get('Risk', []))}")
            return False
        
        print("✅ Edge structure supports explaining away")
        
        # Verify specific parent-child relationships
        economic_parents = edge_dict.get("EconomicRationality", [])
        if "CapacityAnalysis" not in economic_parents or "CostStructure" not in economic_parents:
            print("❌ EconomicRationality should have CapacityAnalysis and CostStructure as parents")
            return False
        
        behavioral_parents = edge_dict.get("BehavioralIntent", [])
        if "MarketConditions" not in behavioral_parents or "StrategicBehavior" not in behavioral_parents:
            print("❌ BehavioralIntent should have MarketConditions and StrategicBehavior as parents")
            return False
        
        risk_parents = edge_dict.get("Risk", [])
        if "EconomicRationality" not in risk_parents or "BehavioralIntent" not in risk_parents:
            print("❌ Risk should have EconomicRationality and BehavioralIntent as parents")
            return False
        
        print("✅ Parent-child relationships correctly configured")
        
        # Check CPD completeness
        cpd_variables = {cpd["variable"] for cpd in withholding_config["cpds"]}
        node_names = {node["name"] for node in withholding_config["nodes"]}
        
        if cpd_variables != node_names:
            print("❌ CPD variables don't match node names")
            print(f"   Nodes: {node_names}")
            print(f"   CPDs: {cpd_variables}")
            return False
        
        print("✅ All nodes have corresponding CPDs")
        
        # Check probability distributions
        for cpd in withholding_config["cpds"]:
            values = cpd["values"]
            for col_idx in range(len(values[0])):
                column_sum = sum(values[row][col_idx] for row in range(len(values)))
                if abs(column_sum - 1.0) > 0.001:
                    print(f"❌ CPD for {cpd['variable']} column {col_idx} doesn't sum to 1 (sum={column_sum})")
                    return False
        
        print("✅ All probability distributions sum to 1")
        
        # Test explaining away pattern in Risk CPT
        risk_cpd = next(cpd for cpd in withholding_config["cpds"] if cpd["variable"] == "Risk")
        risk_values = risk_cpd["values"]
        
        # Check that we have the right structure (3 states x 9 combinations)
        if len(risk_values) != 3 or len(risk_values[0]) != 9:
            print(f"❌ Risk CPT should be 3x9, found {len(risk_values)}x{len(risk_values[0])}")
            return False
        
        # Test explaining away: both parents high should give higher risk than individual parents
        high_risk_both_high = risk_values[2][8]  # Both parents in highest state
        high_risk_economic_only = risk_values[2][6]  # EconomicRationality high, BehavioralIntent low
        high_risk_behavioral_only = risk_values[2][2]  # BehavioralIntent high, EconomicRationality low
        
        if high_risk_both_high <= high_risk_economic_only or high_risk_both_high <= high_risk_behavioral_only:
            print("❌ Explaining away pattern not properly implemented in Risk CPT")
            print(f"   Both high: {high_risk_both_high}")
            print(f"   Economic only: {high_risk_economic_only}")
            print(f"   Behavioral only: {high_risk_behavioral_only}")
            return False
        
        print("✅ Explaining away pattern correctly implemented")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        return False

def test_explaining_away_patterns():
    """Test specific explaining away patterns for economic withholding"""
    print("\nTesting economic withholding explaining away patterns...")
    
    try:
        # Load the model configuration
        with open('config/bayesian_model_config.json', 'r') as f:
            config = json.load(f)
        
        withholding_config = config["models"]["economic_withholding"]
        
        # Test EconomicRationality explaining away
        economic_cpd = next(cpd for cpd in withholding_config["cpds"] if cpd["variable"] == "EconomicRationality")
        economic_values = economic_cpd["values"]
        
        # When both CapacityAnalysis and CostStructure are suspicious, economic rationality should be questionable
        # This explains away individual capacity or cost indicators
        irrational_both_high = economic_values[2][8]  # Both parents high (economically irrational)
        irrational_capacity_only = economic_values[2][6]  # CapacityAnalysis high only
        irrational_cost_only = economic_values[2][2]  # CostStructure high only
        
        if irrational_both_high <= irrational_capacity_only or irrational_both_high <= irrational_cost_only:
            print("❌ EconomicRationality explaining away not properly implemented")
            print(f"   Both high: {irrational_both_high}")
            print(f"   Capacity only: {irrational_capacity_only}")
            print(f"   Cost only: {irrational_cost_only}")
            return False
        
        print("✅ EconomicRationality explaining away correctly implemented")
        
        # Test BehavioralIntent explaining away
        behavioral_cpd = next(cpd for cpd in withholding_config["cpds"] if cpd["variable"] == "BehavioralIntent")
        behavioral_values = behavioral_cpd["values"]
        
        # When both MarketConditions and StrategicBehavior are suspicious, intent should be manipulative
        manipulative_both_high = behavioral_values[2][8]  # Both parents high
        manipulative_market_only = behavioral_values[2][6]  # MarketConditions high only
        manipulative_strategic_only = behavioral_values[2][2]  # StrategicBehavior high only
        
        if manipulative_both_high <= manipulative_market_only or manipulative_both_high <= manipulative_strategic_only:
            print("❌ BehavioralIntent explaining away not properly implemented")
            print(f"   Both high: {manipulative_both_high}")
            print(f"   Market only: {manipulative_market_only}")
            print(f"   Strategic only: {manipulative_strategic_only}")
            return False
        
        print("✅ BehavioralIntent explaining away correctly implemented")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing explaining away patterns: {str(e)}")
        return False

def test_withholding_specific_patterns():
    """Test withholding-specific explaining away patterns"""
    print("\nTesting withholding-specific explaining away patterns...")
    
    try:
        # Load the model configuration
        with open('config/bayesian_model_config.json', 'r') as f:
            config = json.load(f)
        
        withholding_config = config["models"]["economic_withholding"]
        
        # Test that capacity analysis has higher suspicious prior (easier to detect than communications)
        capacity_cpd = next(cpd for cpd in withholding_config["cpds"] if cpd["variable"] == "CapacityAnalysis")
        capacity_values = capacity_cpd["values"]
        
        # Capacity patterns should have higher prior for suspicious behavior (0.1 for highly suspicious)
        highly_suspicious_prior = capacity_values[2][0]
        if highly_suspicious_prior < 0.08:
            print(f"❌ CapacityAnalysis highly suspicious prior too low: {highly_suspicious_prior}")
            return False
        
        print("✅ Capacity analysis has appropriately higher suspicious priors")
        
        # Test economic justification explaining away behavioral patterns
        risk_cpd = next(cpd for cpd in withholding_config["cpds"] if cpd["variable"] == "Risk")
        risk_values = risk_cpd["values"]
        
        # When economically justified (low EconomicRationality) but high behavioral intent, risk should be lower
        # This tests that economic justification explains away suspicious behavior
        risk_justified_suspicious = risk_values[2][2]  # EconomicRationality low, BehavioralIntent high
        risk_unjustified_suspicious = risk_values[2][8]  # Both high
        
        if risk_justified_suspicious >= risk_unjustified_suspicious:
            print("❌ Economic justification not properly explaining away behavioral patterns")
            print(f"   Justified + suspicious behavior: {risk_justified_suspicious}")
            print(f"   Unjustified + suspicious behavior: {risk_unjustified_suspicious}")
            return False
        
        print("✅ Economic justification correctly explains away behavioral patterns")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing withholding patterns: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🧪 ENHANCED ECONOMIC WITHHOLDING MODEL VALIDATION")
    print("=" * 65)
    
    tests = [
        ("Model Configuration", test_economic_withholding_configuration),
        ("Explaining Away Patterns", test_explaining_away_patterns),
        ("Withholding-Specific Patterns", test_withholding_specific_patterns)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 45)
        
        if test_func():
            print(f"✅ {test_name} PASSED")
            passed += 1
        else:
            print(f"❌ {test_name} FAILED")
    
    print("\n" + "=" * 65)
    print(f"SUMMARY: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - Enhanced economic withholding model is properly configured!")
        return 0
    else:
        print("💥 SOME TESTS FAILED - Check configuration")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)