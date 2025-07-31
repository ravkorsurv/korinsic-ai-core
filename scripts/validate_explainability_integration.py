#!/usr/bin/env python3
"""
Validation script for regulatory explainability integration.

This script validates that regulatory explainability is properly integrated
across all Bayesian models without requiring pytest.
"""

import sys
import traceback
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

def test_model_integration(model_class, model_name):
    """Test regulatory explainability integration for a single model."""
    try:
        print(f"Testing {model_name}...")
        
        # Initialize model
        config = {
            "regulatory_explainability": {
                "enabled": True,
                "frameworks": ["MAR_ARTICLE_8", "MAR_ARTICLE_12", "STOR_REQUIREMENTS"]
            }
        }
        
        model = model_class(config=config)
        
        # Check for explainability engine
        if not hasattr(model, 'explainability_engine'):
            print(f"  ❌ Missing explainability_engine")
            return False
        
        # Check for required methods
        if not hasattr(model, 'generate_regulatory_explanation'):
            print(f"  ❌ Missing generate_regulatory_explanation method")
            return False
            
        if not hasattr(model, 'get_regulatory_framework_mapping'):
            print(f"  ❌ Missing get_regulatory_framework_mapping method")
            return False
        
        # Test evidence generation
        sample_evidence = {
            "order_pattern_anomaly": 0.8,
            "temporal_clustering": 0.7,
            "market_impact": 0.9
        }
        
        sample_inference = {
            "Risk": 0.85,
            "Confidence": 0.78
        }
        
        evidence_items = model.generate_regulatory_explanation(
            evidence=sample_evidence,
            inference_result=sample_inference,
            account_id="TEST_ACC_001",
            timestamp=datetime.now().isoformat()
        )
        
        if not isinstance(evidence_items, list):
            print(f"  ❌ generate_regulatory_explanation should return list")
            return False
            
        if len(evidence_items) == 0:
            print(f"  ⚠️  No evidence items generated (this may be normal)")
        
        # Test framework mapping
        framework_mapping = model.get_regulatory_framework_mapping()
        
        if not isinstance(framework_mapping, dict):
            print(f"  ❌ get_regulatory_framework_mapping should return dict")
            return False
            
        if len(framework_mapping) == 0:
            print(f"  ❌ No regulatory frameworks mapped")
            return False
        
        print(f"  ✅ Integration successful")
        print(f"     - Generated {len(evidence_items)} evidence items")
        print(f"     - Mapped {len(framework_mapping)} regulatory frameworks")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error during testing: {e}")
        print(f"     {traceback.format_exc()}")
        return False

def main():
    """Main validation function."""
    print("🚀 Validating regulatory explainability integration...\n")
    
    # Import models
    try:
        from models.bayesian.spoofing.model import SpoofingModel
        from models.bayesian.insider_dealing.model import InsiderDealingModel
        from models.bayesian.market_cornering.model import MarketCorneringModel
        from models.bayesian.circular_trading.model import CircularTradingModel
        from models.bayesian.cross_desk_collusion.model import CrossDeskCollusionModel
        from models.bayesian.commodity_manipulation.model import CommodityManipulationModel
        from models.bayesian.economic_withholding.model import EconomicWithholdingModel
        from models.bayesian.wash_trade_detection.model import WashTradeDetectionModel
    except ImportError as e:
        print(f"❌ Failed to import models: {e}")
        return False
    
    # Test each model
    models_to_test = [
        (SpoofingModel, "Spoofing Detection"),
        (InsiderDealingModel, "Insider Dealing"),
        (MarketCorneringModel, "Market Cornering"),
        (CircularTradingModel, "Circular Trading"),
        (CrossDeskCollusionModel, "Cross Desk Collusion"),
        (CommodityManipulationModel, "Commodity Manipulation"),
        (EconomicWithholdingModel, "Economic Withholding"),
        (WashTradeDetectionModel, "Wash Trade Detection")
    ]
    
    success_count = 0
    total_count = len(models_to_test)
    
    for model_class, model_name in models_to_test:
        if test_model_integration(model_class, model_name):
            success_count += 1
        print()  # Add spacing
    
    # Summary
    print("📊 Validation Summary:")
    print(f"✅ Successfully integrated: {success_count}/{total_count} models")
    print(f"❌ Failed integrations: {total_count - success_count}/{total_count} models")
    
    if success_count == total_count:
        print("\n🎉 All models successfully integrated with regulatory explainability!")
        return True
    else:
        print(f"\n⚠️  {total_count - success_count} models require attention")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)