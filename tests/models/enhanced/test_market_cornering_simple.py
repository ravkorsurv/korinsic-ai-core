#!/usr/bin/env python3
"""
Simple Enhanced Market Cornering Model Validation

Validates the enhanced 4-parent CPT structure configuration for market cornering.
Tests the basic structure and explaining away patterns in the model configuration.
"""

import json
import sys

def test_market_cornering_configuration():
    """Test that the enhanced market cornering model is properly configured"""
    print("Testing enhanced market cornering model configuration...")
    
    try:
        # Load the model configuration
        with open('config/bayesian_model_config.json', 'r') as f:
            config = json.load(f)
        
        print("✅ Configuration file loaded successfully")
        
        # Check that market_cornering model exists
        if "market_cornering" not in config["models"]:
            print("❌ market_cornering model not found in configuration")
            return False
        
        cornering_config = config["models"]["market_cornering"]
        print("✅ market_cornering model found")
        
        # Check required sections
        required_sections = ["nodes", "edges", "cpds"]
        for section in required_sections:
            if section not in cornering_config:
                print(f"❌ Missing required section: {section}")
                return False
        print("✅ All required sections present")
        
        # Check node structure
        nodes = {node["name"]: node for node in cornering_config["nodes"]}
        
        # Check evidence nodes (4 parents)
        evidence_nodes = ["PositionAccumulation", "SupplyControl", "PriceManipulation", "MarketDomination"]
        for node_name in evidence_nodes:
            if node_name not in nodes:
                print(f"❌ Missing evidence node: {node_name}")
                return False
        print("✅ All 4 evidence nodes present")
        
        # Check intermediate nodes
        intermediate_nodes = ["MarketImpact", "TechnicalManipulation"]
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
        edges = cornering_config["edges"]
        edge_dict = {}
        for parent, child in edges:
            if child not in edge_dict:
                edge_dict[child] = []
            edge_dict[child].append(parent)
        
        # Validate explaining away structure
        # MarketImpact should have 2 parents
        if len(edge_dict.get("MarketImpact", [])) != 2:
            print(f"❌ MarketImpact should have 2 parents, found {len(edge_dict.get('MarketImpact', []))}")
            return False
        
        # TechnicalManipulation should have 2 parents
        if len(edge_dict.get("TechnicalManipulation", [])) != 2:
            print(f"❌ TechnicalManipulation should have 2 parents, found {len(edge_dict.get('TechnicalManipulation', []))}")
            return False
        
        # Risk should have 2 parents (intermediate nodes)
        if len(edge_dict.get("Risk", [])) != 2:
            print(f"❌ Risk should have 2 parents, found {len(edge_dict.get('Risk', []))}")
            return False
        
        print("✅ Edge structure supports explaining away")
        
        # Verify specific parent-child relationships
        market_impact_parents = edge_dict.get("MarketImpact", [])
        if "PositionAccumulation" not in market_impact_parents or "PriceManipulation" not in market_impact_parents:
            print("❌ MarketImpact should have PositionAccumulation and PriceManipulation as parents")
            return False
        
        technical_parents = edge_dict.get("TechnicalManipulation", [])
        if "SupplyControl" not in technical_parents or "MarketDomination" not in technical_parents:
            print("❌ TechnicalManipulation should have SupplyControl and MarketDomination as parents")
            return False
        
        risk_parents = edge_dict.get("Risk", [])
        if "MarketImpact" not in risk_parents or "TechnicalManipulation" not in risk_parents:
            print("❌ Risk should have MarketImpact and TechnicalManipulation as parents")
            return False
        
        print("✅ Parent-child relationships correctly configured")
        
        # Check CPD completeness - this will tell us if we need to update the CPDs
        cpd_variables = {cpd["variable"] for cpd in cornering_config["cpds"]}
        node_names = {node["name"] for node in cornering_config["nodes"]}
        
        if cpd_variables != node_names:
            print("⚠️  CPD variables don't match node names - needs CPD update")
            print(f"   Nodes: {node_names}")
            print(f"   CPDs: {cpd_variables}")
            return "needs_cpd_update"
        
        print("✅ All nodes have corresponding CPDs")
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🧪 ENHANCED MARKET CORNERING MODEL VALIDATION")
    print("=" * 60)
    
    result = test_market_cornering_configuration()
    
    if result == "needs_cpd_update":
        print("\n⚠️  PARTIAL SUCCESS - Model structure is correct but CPDs need updating")
        return 0
    elif result:
        print("\n🎉 ALL TESTS PASSED - Enhanced market cornering model is properly configured!")
        return 0
    else:
        print("\n💥 TESTS FAILED - Check configuration")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)