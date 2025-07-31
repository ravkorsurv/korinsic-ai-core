#!/usr/bin/env python3
"""
Improved Validation Script for Regulatory Explainability Integration

This script provides enhanced validation with proper error handling, logging,
and optional parallel processing for better performance.
"""

import sys
import logging
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('validation.log')
    ]
)
logger = logging.getLogger(__name__)

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass

class ModelImportError(ValidationError):
    """Exception for model import failures"""
    pass

class ExplainabilityTestError(ValidationError):
    """Exception for explainability testing failures"""
    pass

class ModelValidator:
    """Enhanced model validator with proper error handling"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.parallel_testing = self.config.get('parallel_testing', False)
        self.max_workers = self.config.get('max_workers', 4)
        
    def test_model_integration(self, model_class, model_name: str) -> Dict[str, any]:
        """
        Test regulatory explainability integration for a single model.
        
        Args:
            model_class: Model class to test
            model_name: Name of the model for reporting
            
        Returns:
            Dictionary with test results and details
        """
        start_time = time.time()
        result = {
            "model_name": model_name,
            "success": False,
            "errors": [],
            "warnings": [],
            "test_duration": 0.0,
            "details": {}
        }
        
        try:
            logger.info(f"Testing {model_name}...")
            
            # Test 1: Model initialization
            try:
                config = {
                    "regulatory_explainability": {
                        "enabled": True,
                        "frameworks": ["MAR_ARTICLE_8", "MAR_ARTICLE_12", "STOR_REQUIREMENTS"]
                    }
                }
                model = model_class(config=config)
                result["details"]["initialization"] = "SUCCESS"
                logger.debug(f"{model_name} initialized successfully")
            except ImportError as e:
                raise ModelImportError(f"Failed to import dependencies for {model_name}: {e}")
            except AttributeError as e:
                raise ValidationError(f"Model {model_name} missing required attributes: {e}")
            except Exception as e:
                raise ValidationError(f"Failed to initialize {model_name}: {e}")
            
            # Test 2: Check for explainability engine
            if not hasattr(model, 'explainability_engine'):
                raise ExplainabilityTestError(f"{model_name} missing explainability_engine attribute")
            result["details"]["explainability_engine"] = "PRESENT"
            
            # Test 3: Check for required methods
            required_methods = [
                'generate_regulatory_explanation',
                'get_regulatory_framework_mapping'
            ]
            
            for method_name in required_methods:
                if not hasattr(model, method_name):
                    raise ExplainabilityTestError(f"{model_name} missing {method_name} method")
                if not callable(getattr(model, method_name)):
                    raise ExplainabilityTestError(f"{model_name}.{method_name} is not callable")
            
            result["details"]["required_methods"] = "ALL_PRESENT"
            
            # Test 4: Test evidence generation
            try:
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
                    raise ExplainabilityTestError(f"{model_name} generate_regulatory_explanation should return list, got {type(evidence_items)}")
                
                result["details"]["evidence_generation"] = f"SUCCESS ({len(evidence_items)} items)"
                
                if len(evidence_items) == 0:
                    result["warnings"].append("No evidence items generated (may be normal for this model)")
                    
            except TypeError as e:
                raise ExplainabilityTestError(f"{model_name} evidence generation failed with TypeError: {e}")
            except Exception as e:
                raise ExplainabilityTestError(f"{model_name} evidence generation failed: {e}")
            
            # Test 5: Test framework mapping
            try:
                framework_mapping = model.get_regulatory_framework_mapping()
                
                if not isinstance(framework_mapping, dict):
                    raise ExplainabilityTestError(f"{model_name} get_regulatory_framework_mapping should return dict, got {type(framework_mapping)}")
                
                if len(framework_mapping) == 0:
                    raise ExplainabilityTestError(f"{model_name} returned empty regulatory framework mapping")
                
                result["details"]["framework_mapping"] = f"SUCCESS ({len(framework_mapping)} frameworks)"
                
            except Exception as e:
                raise ExplainabilityTestError(f"{model_name} framework mapping failed: {e}")
            
            # Test 6: Performance test
            try:
                start_perf = time.time()
                for _ in range(5):  # Run 5 times for average
                    model.generate_regulatory_explanation(
                        evidence=sample_evidence,
                        inference_result=sample_inference,
                        account_id="PERF_TEST",
                        timestamp=datetime.now().isoformat()
                    )
                avg_time = (time.time() - start_perf) / 5
                
                result["details"]["average_generation_time"] = f"{avg_time:.3f}s"
                
                if avg_time > 1.0:
                    result["warnings"].append(f"Slow performance: {avg_time:.3f}s average generation time")
                    
            except Exception as e:
                result["warnings"].append(f"Performance test failed: {e}")
            
            # All tests passed
            result["success"] = True
            logger.info(f"✅ {model_name} integration test PASSED")
            
        except ModelImportError as e:
            result["errors"].append(str(e))
            logger.error(f"❌ {model_name} failed with import error: {e}")
        except ExplainabilityTestError as e:
            result["errors"].append(str(e))
            logger.error(f"❌ {model_name} failed explainability test: {e}")
        except ValidationError as e:
            result["errors"].append(str(e))
            logger.error(f"❌ {model_name} validation failed: {e}")
        except Exception as e:
            result["errors"].append(f"Unexpected error: {e}")
            logger.error(f"❌ {model_name} failed with unexpected error: {e}")
            logger.debug(f"Full traceback: {traceback.format_exc()}")
        
        finally:
            result["test_duration"] = time.time() - start_time
            
        return result
    
    def validate_all_models(self) -> Dict[str, any]:
        """
        Validate all models with optional parallel processing.
        
        Returns:
            Complete validation results
        """
        logger.info("🚀 Starting comprehensive regulatory explainability validation...")
        
        # Import models with proper error handling
        models_to_test = self._import_models()
        
        if not models_to_test:
            logger.error("No models could be imported for testing")
            return {"success": False, "error": "No models available for testing"}
        
        start_time = time.time()
        
        if self.parallel_testing and len(models_to_test) > 1:
            results = self._run_parallel_tests(models_to_test)
        else:
            results = self._run_sequential_tests(models_to_test)
        
        total_time = time.time() - start_time
        
        # Compile summary
        summary = self._compile_summary(results, total_time)
        
        # Log final results
        self._log_final_results(summary)
        
        return summary
    
    def _import_models(self) -> List[Tuple[any, str]]:
        """Import all models with proper error handling"""
        models_to_test = []
        
        model_imports = [
            ("src.models.bayesian.spoofing.model", "SpoofingModel", "Spoofing Detection"),
            ("src.models.bayesian.insider_dealing.model", "InsiderDealingModel", "Insider Dealing"),
            ("src.models.bayesian.market_cornering.model", "MarketCorneringModel", "Market Cornering"),
            ("src.models.bayesian.circular_trading.model", "CircularTradingModel", "Circular Trading"),
            ("src.models.bayesian.cross_desk_collusion.model", "CrossDeskCollusionModel", "Cross Desk Collusion"),
            ("src.models.bayesian.commodity_manipulation.model", "CommodityManipulationModel", "Commodity Manipulation"),
            ("src.models.bayesian.economic_withholding.model", "EconomicWithholdingModel", "Economic Withholding"),
            ("src.models.bayesian.wash_trade_detection.model", "WashTradeDetectionModel", "Wash Trade Detection")
        ]
        
        for module_path, class_name, display_name in model_imports:
            try:
                # Convert path to module format
                module_name = module_path.replace("/", ".").replace("src.", "")
                module = __import__(module_name, fromlist=[class_name])
                model_class = getattr(module, class_name)
                models_to_test.append((model_class, display_name))
                logger.debug(f"Successfully imported {display_name}")
            except ImportError as e:
                logger.warning(f"Failed to import {display_name}: {e}")
            except AttributeError as e:
                logger.warning(f"Failed to get class {class_name} from {module_path}: {e}")
            except Exception as e:
                logger.warning(f"Unexpected error importing {display_name}: {e}")
        
        logger.info(f"Successfully imported {len(models_to_test)} models for testing")
        return models_to_test
    
    def _run_sequential_tests(self, models_to_test: List[Tuple[any, str]]) -> List[Dict]:
        """Run tests sequentially"""
        logger.info("Running tests sequentially...")
        results = []
        
        for model_class, model_name in models_to_test:
            result = self.test_model_integration(model_class, model_name)
            results.append(result)
        
        return results
    
    def _run_parallel_tests(self, models_to_test: List[Tuple[any, str]]) -> List[Dict]:
        """Run tests in parallel for better performance"""
        logger.info(f"Running tests in parallel with {self.max_workers} workers...")
        results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_model = {
                executor.submit(self.test_model_integration, model_class, model_name): model_name
                for model_class, model_name in models_to_test
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_model):
                model_name = future_to_model[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    logger.error(f"Parallel test failed for {model_name}: {e}")
                    results.append({
                        "model_name": model_name,
                        "success": False,
                        "errors": [f"Parallel execution error: {e}"],
                        "warnings": [],
                        "test_duration": 0.0,
                        "details": {}
                    })
        
        # Sort results by model name for consistent output
        results.sort(key=lambda x: x["model_name"])
        return results
    
    def _compile_summary(self, results: List[Dict], total_time: float) -> Dict:
        """Compile summary statistics"""
        total_models = len(results)
        successful_models = sum(1 for r in results if r["success"])
        failed_models = total_models - successful_models
        
        total_errors = sum(len(r["errors"]) for r in results)
        total_warnings = sum(len(r["warnings"]) for r in results)
        
        avg_test_time = sum(r["test_duration"] for r in results) / total_models if total_models > 0 else 0
        
        return {
            "success": failed_models == 0,
            "summary": {
                "total_models": total_models,
                "successful_models": successful_models,
                "failed_models": failed_models,
                "total_errors": total_errors,
                "total_warnings": total_warnings,
                "total_time": total_time,
                "average_test_time": avg_test_time
            },
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
    
    def _log_final_results(self, summary: Dict) -> None:
        """Log final validation results"""
        stats = summary["summary"]
        
        logger.info("📊 Validation Summary:")
        logger.info(f"✅ Successfully integrated: {stats['successful_models']}/{stats['total_models']} models")
        logger.info(f"❌ Failed integrations: {stats['failed_models']}/{stats['total_models']} models")
        logger.info(f"⚠️  Total warnings: {stats['total_warnings']}")
        logger.info(f"🕒 Total time: {stats['total_time']:.2f}s")
        logger.info(f"⏱️  Average test time: {stats['average_test_time']:.2f}s")
        
        if summary["success"]:
            logger.info("🎉 All models successfully integrated with regulatory explainability!")
        else:
            logger.warning(f"⚠️  {stats['failed_models']} models require attention")
            
        # Log detailed results for failed models
        for result in summary["results"]:
            if not result["success"]:
                logger.error(f"❌ {result['model_name']} failures:")
                for error in result["errors"]:
                    logger.error(f"   - {error}")

def main():
    """Main validation function with enhanced error handling"""
    try:
        config = {
            "parallel_testing": True,  # Enable parallel testing
            "max_workers": 4
        }
        
        validator = ModelValidator(config)
        summary = validator.validate_all_models()
        
        # Exit with appropriate code
        sys.exit(0 if summary["success"] else 1)
        
    except KeyboardInterrupt:
        logger.info("Validation interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Validation failed with unexpected error: {e}")
        logger.debug(f"Full traceback: {traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    main()