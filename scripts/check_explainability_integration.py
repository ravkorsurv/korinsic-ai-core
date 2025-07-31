#!/usr/bin/env python3
"""
File-based validation script for regulatory explainability integration.

This script checks that regulatory explainability integration code is present
in all Bayesian models by examining the source files directly.
"""

import os
from pathlib import Path
from typing import List, Dict, Tuple

def check_file_for_integration(file_path: Path) -> Dict[str, bool]:
    """Check a single model file for regulatory explainability integration."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        checks = {
            'has_import': 'from ....core.regulatory_explainability import' in content,
            'has_datetime_import': 'from datetime import datetime' in content,
            'has_engine_init': 'self.explainability_engine = RegulatoryExplainabilityEngine' in content,
            'has_explanation_method': 'def generate_regulatory_explanation(' in content,
            'has_framework_mapping': 'def get_regulatory_framework_mapping(' in content,
            'has_evidence_item': 'EvidenceItem(' in content,
            'has_regulatory_framework': 'RegulatoryFramework.' in content
        }
        
        return checks
        
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return {key: False for key in ['has_import', 'has_datetime_import', 'has_engine_init', 
                                     'has_explanation_method', 'has_framework_mapping', 
                                     'has_evidence_item', 'has_regulatory_framework']}

def get_model_files() -> List[Tuple[str, Path]]:
    """Get all Bayesian model files."""
    models_dir = Path('src/models/bayesian')
    model_files = []
    
    model_names = [
        'spoofing',
        'insider_dealing', 
        'market_cornering',
        'circular_trading',
        'cross_desk_collusion',
        'commodity_manipulation',
        'economic_withholding',
        'wash_trade_detection'
    ]
    
    for model_name in model_names:
        model_file = models_dir / model_name / 'model.py'
        if model_file.exists():
            model_files.append((model_name, model_file))
        else:
            print(f"⚠️  Model file not found: {model_file}")
    
    return model_files

def check_configuration_files() -> Dict[str, bool]:
    """Check configuration files for regulatory explainability settings."""
    config_checks = {}
    
    # Check base configuration
    base_config = Path('config/base.json')
    if base_config.exists():
        with open(base_config, 'r') as f:
            content = f.read()
        config_checks['base_config_enabled'] = '"regulatory_explainability": true' in content
    else:
        config_checks['base_config_enabled'] = False
    
    # Check Bayesian models configuration
    bayesian_config = Path('config/models/bayesian_models.json')
    if bayesian_config.exists():
        with open(bayesian_config, 'r') as f:
            content = f.read()
        config_checks['bayesian_config_enabled'] = '"regulatory_explainability"' in content
    else:
        config_checks['bayesian_config_enabled'] = False
    
    return config_checks

def main():
    """Main validation function."""
    print("🔍 Checking regulatory explainability integration...\n")
    
    # Get model files
    model_files = get_model_files()
    if not model_files:
        print("❌ No model files found")
        return False
    
    print(f"Found {len(model_files)} model files to check\n")
    
    # Check each model
    all_passed = True
    detailed_results = {}
    
    for model_name, model_file in model_files:
        print(f"Checking {model_name}...")
        checks = check_file_for_integration(model_file)
        detailed_results[model_name] = checks
        
        # Calculate pass rate
        passed_checks = sum(checks.values())
        total_checks = len(checks)
        pass_rate = passed_checks / total_checks
        
        if pass_rate >= 0.8:  # At least 80% of checks must pass
            print(f"  ✅ Integration complete ({passed_checks}/{total_checks} checks passed)")
        elif pass_rate >= 0.5:
            print(f"  ⚠️  Partial integration ({passed_checks}/{total_checks} checks passed)")
            all_passed = False
        else:
            print(f"  ❌ Missing integration ({passed_checks}/{total_checks} checks passed)")
            all_passed = False
        
        # Show specific failures
        for check_name, passed in checks.items():
            if not passed:
                print(f"     - Missing: {check_name}")
        
        print()
    
    # Check configurations
    print("Checking configuration files...")
    config_checks = check_configuration_files()
    
    for config_name, enabled in config_checks.items():
        if enabled:
            print(f"  ✅ {config_name}")
        else:
            print(f"  ❌ {config_name}")
            all_passed = False
    
    print()
    
    # Summary
    fully_integrated = sum(1 for checks in detailed_results.values() 
                          if sum(checks.values()) >= len(checks) * 0.8)
    partially_integrated = sum(1 for checks in detailed_results.values() 
                              if 0.5 <= sum(checks.values()) / len(checks) < 0.8)
    not_integrated = len(detailed_results) - fully_integrated - partially_integrated
    
    print("📊 Integration Summary:")
    print(f"✅ Fully integrated: {fully_integrated}/{len(model_files)} models")
    print(f"⚠️  Partially integrated: {partially_integrated}/{len(model_files)} models")
    print(f"❌ Not integrated: {not_integrated}/{len(model_files)} models")
    
    # Configuration summary
    config_enabled = sum(config_checks.values())
    print(f"⚙️  Configuration files: {config_enabled}/{len(config_checks)} enabled")
    
    if all_passed and fully_integrated == len(model_files):
        print("\n🎉 All models successfully integrated with regulatory explainability!")
        return True
    else:
        print(f"\n⚠️  Integration incomplete - see details above")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)