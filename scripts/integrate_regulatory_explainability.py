#!/usr/bin/env python3
"""
Script to integrate regulatory explainability into all Bayesian models.

This script automatically adds the necessary imports, initialization, and methods
to integrate regulatory explainability across all risk typology models.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple

# Model configurations for regulatory explainability
MODEL_CONFIGS = {
    'insider_dealing': {
        'primary_framework': 'MAR_ARTICLE_8',
        'evidence_types': ['TRADING_PATTERN', 'TIMING_ANOMALY', 'COMMUNICATION'],
        'key_indicators': [
            'Information asymmetry exploitation',
            'Temporal correlation with price-sensitive events',
            'Cross-account coordination patterns'
        ]
    },
    'market_cornering': {
        'primary_framework': 'MAR_ARTICLE_12',
        'evidence_types': ['TRADING_PATTERN', 'CROSS_ACCOUNT_CORRELATION'],
        'key_indicators': [
            'Market concentration activities',
            'Price manipulation through volume',
            'Coordinated position building'
        ]
    },
    'circular_trading': {
        'primary_framework': 'MAR_ARTICLE_12',
        'evidence_types': ['TRADING_PATTERN', 'CROSS_ACCOUNT_CORRELATION'],
        'key_indicators': [
            'Circular transaction patterns',
            'Artificial volume creation',
            'Cross-account coordination'
        ]
    },
    'cross_desk_collusion': {
        'primary_framework': 'MAR_ARTICLE_8',
        'evidence_types': ['COMMUNICATION', 'CROSS_ACCOUNT_CORRELATION', 'TIMING_ANOMALY'],
        'key_indicators': [
            'Inter-desk communication patterns',
            'Coordinated trading strategies',
            'Information sharing evidence'
        ]
    },
    'commodity_manipulation': {
        'primary_framework': 'MAR_ARTICLE_12',
        'evidence_types': ['TRADING_PATTERN', 'TIMING_ANOMALY'],
        'key_indicators': [
            'Physical commodity influence',
            'Derivative market manipulation',
            'Storage and delivery manipulation'
        ]
    },
    'economic_withholding': {
        'primary_framework': 'STOR_REQUIREMENTS',
        'evidence_types': ['TRADING_PATTERN', 'TIMING_ANOMALY'],
        'key_indicators': [
            'Capacity withholding patterns',
            'Economic withholding strategies',
            'Market power abuse'
        ]
    }
}

def get_model_files() -> List[Tuple[str, Path]]:
    """Get all Bayesian model files that need integration."""
    models_dir = Path('src/models/bayesian')
    model_files = []
    
    for model_name in MODEL_CONFIGS.keys():
        model_file = models_dir / model_name / 'model.py'
        if model_file.exists():
            model_files.append((model_name, model_file))
    
    return model_files

def add_imports(file_content: str) -> str:
    """Add regulatory explainability imports to the file."""
    import_pattern = r'(from \.\.shared\.fallback_logic import FallbackLogic\n)'
    
    regulatory_imports = '''
# Add regulatory explainability import
from ....core.regulatory_explainability import (
    RegulatoryExplainabilityEngine,
    EvidenceItem,
    EvidenceType,
    RegulatoryFramework
)
'''
    
    if 'from ....core.regulatory_explainability import' in file_content:
        return file_content  # Already has imports
    
    # Add datetime import if not present
    if 'from datetime import datetime' not in file_content:
        datetime_import = 'from datetime import datetime\n'
        type_import_pattern = r'(from typing import [^\n]+\n)'
        file_content = re.sub(type_import_pattern, r'\1' + datetime_import, file_content)
    
    return re.sub(import_pattern, r'\1' + regulatory_imports, file_content)

def add_initialization(file_content: str, model_name: str) -> str:
    """Add regulatory explainability engine initialization."""
    init_pattern = r'(self\.esi_calculator = EvidenceSufficiencyIndex\(\)\n)'
    
    initialization = f'''
        # Initialize regulatory explainability engine
        self.explainability_engine = RegulatoryExplainabilityEngine(config or {{}})
'''
    
    if 'self.explainability_engine' in file_content:
        return file_content  # Already initialized
    
    return re.sub(init_pattern, r'\1' + initialization, file_content)

def generate_explainability_methods(model_name: str) -> str:
    """Generate regulatory explainability methods for a specific model."""
    config = MODEL_CONFIGS[model_name]
    primary_framework = config['primary_framework']
    evidence_types = config['evidence_types']
    key_indicators = config['key_indicators']
    
    # Convert model_name to class-appropriate format
    class_name = ''.join(word.capitalize() for word in model_name.split('_'))
    
    method_template = f'''
    def generate_regulatory_explanation(
        self, 
        evidence: Dict[str, Any], 
        inference_result: Dict[str, float],
        account_id: str,
        timestamp: str
    ) -> List[EvidenceItem]:
        """
        Generate regulatory explainability evidence for {model_name.replace('_', ' ')} detection.
        
        Args:
            evidence: Input evidence dictionary
            inference_result: Model inference results
            account_id: Account identifier
            timestamp: Evidence timestamp
            
        Returns:
            List of evidence items for regulatory explanation
        """
        evidence_items = []
        
        # Generate evidence items based on model-specific patterns
        for evidence_key, evidence_value in evidence.items():
            if isinstance(evidence_value, (int, float)) and evidence_value > 0.1:
                # Determine evidence type based on key
                evidence_type = EvidenceType.TRADING_PATTERN
                if 'communication' in evidence_key.lower():
                    evidence_type = EvidenceType.COMMUNICATION
                elif 'timing' in evidence_key.lower() or 'temporal' in evidence_key.lower():
                    evidence_type = EvidenceType.TIMING_ANOMALY
                elif 'cross' in evidence_key.lower() or 'correlation' in evidence_key.lower():
                    evidence_type = EvidenceType.CROSS_ACCOUNT_CORRELATION
                
                evidence_items.append(EvidenceItem(
                    evidence_type=evidence_type,
                    account_id=account_id,
                    timestamp=datetime.fromisoformat(timestamp),
                    description=f"{model_name.replace('_', ' ').title()} indicator: {{evidence_key}} = {{evidence_value:.2f}}",
                    strength=min(float(evidence_value), 1.0),
                    reliability=0.85,
                    regulatory_relevance={{
                        RegulatoryFramework.{primary_framework}: 0.9,
                        RegulatoryFramework.STOR_REQUIREMENTS: 0.8
                    }},
                    raw_data={{
                        'model_type': '{model_name}',
                        'evidence_node': evidence_key,
                        'score': evidence_value,
                        'inference_result': inference_result
                    }}
                ))
        
        return evidence_items
    
    def get_regulatory_framework_mapping(self) -> Dict[RegulatoryFramework, Dict[str, Any]]:
        """
        Get regulatory framework mapping for {model_name.replace('_', ' ')} detection.
        
        Returns:
            Dictionary mapping regulatory frameworks to their requirements
        """
        return {{
            RegulatoryFramework.{primary_framework}: {{
                "description": "{model_name.replace('_', ' ').title()} detection and analysis",
                "key_indicators": {key_indicators},
                "evidence_threshold": 0.7,
                "reporting_requirements": "Detailed pattern analysis required"
            }},
            RegulatoryFramework.STOR_REQUIREMENTS: {{
                "description": "Suspicious transaction reporting for {model_name.replace('_', ' ')} behavior",
                "key_indicators": {key_indicators[:2]},
                "evidence_threshold": 0.6,
                "reporting_requirements": "Transaction-level details required"
            }}
        }}
'''
    
    return method_template

def add_explainability_methods(file_content: str, model_name: str) -> str:
    """Add regulatory explainability methods to the model file."""
    # Check if methods already exist
    if 'generate_regulatory_explanation' in file_content:
        return file_content
    
    # Find the end of the class (before the last closing brace or at end of file)
    methods = generate_explainability_methods(model_name)
    
    # Add methods before the end of the file
    if file_content.endswith('\n'):
        return file_content + methods + '\n'
    else:
        return file_content + '\n' + methods + '\n'

def integrate_model(model_name: str, model_file: Path) -> bool:
    """Integrate regulatory explainability into a single model."""
    try:
        print(f"Integrating regulatory explainability into {model_name}...")
        
        # Read the current file
        with open(model_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Apply transformations
        content = add_imports(content)
        content = add_initialization(content, model_name)
        content = add_explainability_methods(content, model_name)
        
        # Write back the modified content
        with open(model_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Successfully integrated {model_name}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to integrate {model_name}: {e}")
        return False

def main():
    """Main integration function."""
    print("🚀 Starting regulatory explainability integration...")
    
    model_files = get_model_files()
    if not model_files:
        print("❌ No model files found to integrate")
        return
    
    success_count = 0
    total_count = len(model_files)
    
    for model_name, model_file in model_files:
        if integrate_model(model_name, model_file):
            success_count += 1
    
    print(f"\n📊 Integration Summary:")
    print(f"✅ Successfully integrated: {success_count}/{total_count} models")
    print(f"❌ Failed integrations: {total_count - success_count}/{total_count} models")
    
    if success_count == total_count:
        print("\n🎉 All models successfully integrated with regulatory explainability!")
    else:
        print(f"\n⚠️  {total_count - success_count} models require manual review")

if __name__ == "__main__":
    main()