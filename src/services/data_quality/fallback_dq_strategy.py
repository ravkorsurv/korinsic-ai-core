"""
Fallback Data Quality Scoring Strategy

Lightweight DQSI strategy for startups and light clients.
Provides basic profiling only without role-based logic, reconciliation, or accuracy checks.
"""

from typing import Dict, List, Any, Optional
import logging
from .dq_strategy_base import DQScoringStrategy, KDEResult, DQConfig

logger = logging.getLogger(__name__)


class FallbackDQScoringStrategy(DQScoringStrategy):
    """
    Fallback strategy for lightweight DQSI scoring
    
    Features:
    - Basic profiling only
    - No role-based logic
    - No reconciliation
    - No accuracy validation
    - Minimal resource usage
    """
    
    def __init__(self, config: DQConfig):
        super().__init__(config)
        logger.info("Initialized Fallback DQ Scoring Strategy")
    
    def get_strategy_name(self) -> str:
        return "fallback"
    
    def score_kdes(self, data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> List[KDEResult]:
        """
        Score KDEs using basic profiling approach
        
        Args:
            data: Input data containing KDEs
            metadata: Optional metadata (ignored in fallback mode)
            
        Returns:
            List of KDE scoring results
        """
        kde_results = []
        
        # Score each KDE present in data
        for kde_name, kde_value in data.items():
            if kde_name in self.config.kde_risk_tiers:
                kde_result = self._score_single_kde(kde_name, kde_value)
                kde_results.append(kde_result)
        
        # Add synthetic KDEs
        synthetic_kdes = self.create_synthetic_kdes(data, metadata)
        kde_results.extend(synthetic_kdes)
        
        logger.debug(f"Scored {len(kde_results)} KDEs using fallback strategy")
        return kde_results
    
    def _score_single_kde(self, kde_name: str, kde_value: Any) -> KDEResult:
        """
        Score a single KDE using basic profiling
        
        Args:
            kde_name: Name of the KDE
            kde_value: Value of the KDE
            
        Returns:
            KDEResult for this KDE
        """
        # Get KDE metadata
        risk_tier = self.config.kde_risk_tiers.get(kde_name, 'low')
        risk_weight = self.config.risk_weights.get(risk_tier, 1)
        dimension = self._get_kde_dimension(kde_name)
        tier = self._get_dimension_tier(dimension)
        
        # Basic scoring logic
        score = self._calculate_basic_score(kde_name, kde_value)
        imputed = False
        
        # Check if value appears to be imputed/inferred
        if isinstance(kde_value, str) and kde_value.lower() in ['unknown', 'n/a', 'null', 'missing']:
            score = 0.6  # Imputed value
            imputed = True
        elif kde_value is None or kde_value == '':
            score = 0.0  # Missing value
        
        return KDEResult(
            kde_name=kde_name,
            score=score,
            risk_tier=risk_tier,
            risk_weight=risk_weight,
            dimension=dimension,
            tier=tier,
            is_synthetic=False,
            imputed=imputed,
            details={
                'strategy': 'fallback',
                'profiling_only': True
            }
        )
    
    def _calculate_basic_score(self, kde_name: str, kde_value: Any) -> float:
        """
        Calculate basic score for a KDE value
        
        Args:
            kde_name: Name of the KDE
            kde_value: Value to score
            
        Returns:
            Score between 0.0 and 1.0
        """
        # Check for missing/null values
        if kde_value is None or kde_value == '':
            return 0.0
        
        # Basic type and format checks
        if kde_name in ['trader_id', 'client_id', 'desk_id']:
            # ID fields - check if they look valid
            return self._score_id_field(kde_value)
        elif kde_name in ['trade_time', 'order_timestamp', 'timestamp']:
            # Timestamp fields - check if parseable
            return self._score_timestamp_field(kde_value)
        elif kde_name in ['notional', 'quantity', 'price']:
            # Numeric fields - check if valid numbers
            return self._score_numeric_field(kde_value)
        elif kde_name in ['instrument']:
            # String fields - basic validation
            return self._score_string_field(kde_value)
        else:
            # Default scoring for unknown fields
            return 1.0 if kde_value is not None else 0.0
    
    def _score_id_field(self, value: Any) -> float:
        """Score ID fields (trader_id, client_id, etc.)"""
        if not value:
            return 0.0
        
        str_value = str(value).strip()
        
        # Check basic format requirements
        if len(str_value) < 2:
            return 0.3  # Too short for valid ID
        elif len(str_value) > 50:
            return 0.7  # Suspiciously long but might be valid
        elif str_value.isalnum() or '_' in str_value or '-' in str_value:
            return 1.0  # Valid format
        else:
            return 0.5  # Questionable format
    
    def _score_timestamp_field(self, value: Any) -> float:
        """Score timestamp fields"""
        if not value:
            return 0.0
        
        try:
            from datetime import datetime
            
            str_value = str(value)
            
            # Try common timestamp formats
            formats = [
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%dT%H:%M:%S',
                '%Y-%m-%d %H:%M:%S.%f',
                '%Y-%m-%dT%H:%M:%S.%f',
                '%Y-%m-%dT%H:%M:%SZ',
                '%Y-%m-%dT%H:%M:%S.%fZ'
            ]
            
            for fmt in formats:
                try:
                    datetime.strptime(str_value[:19], fmt[:19])
                    return 1.0  # Valid timestamp
                except ValueError:
                    continue
            
            # Try ISO format parsing
            try:
                datetime.fromisoformat(str_value.replace('Z', '+00:00'))
                return 1.0
            except ValueError:
                pass
            
            return 0.3  # Invalid timestamp format
            
        except Exception:
            return 0.0
    
    def _score_numeric_field(self, value: Any) -> float:
        """Score numeric fields (notional, quantity, price)"""
        if value is None:
            return 0.0
        
        try:
            float_value = float(value)
            
            # Check for reasonable values
            if float_value < 0:
                return 0.2  # Negative values are suspicious for most financial fields
            elif float_value == 0:
                return 0.6  # Zero might be valid but worth flagging
            elif float_value > 1e12:  # Very large numbers
                return 0.7  # Might be valid but suspicious
            else:
                return 1.0  # Valid numeric value
                
        except (ValueError, TypeError):
            return 0.1  # Not a valid number
    
    def _score_string_field(self, value: Any) -> float:
        """Score string fields (instrument, etc.)"""
        if not value:
            return 0.0
        
        str_value = str(value).strip()
        
        if len(str_value) == 0:
            return 0.0
        elif len(str_value) < 2:
            return 0.4  # Very short strings are suspicious
        elif len(str_value) > 100:
            return 0.6  # Very long strings might be errors
        else:
            return 1.0  # Reasonable string length
    
    def _get_kde_dimension(self, kde_name: str) -> str:
        """Map KDE to its primary dimension"""
        # Mapping KDEs to dimensions based on their nature
        kde_dimension_map = {
            'trader_id': 'completeness',
            'trade_time': 'timeliness', 
            'order_timestamp': 'timeliness',
            'timestamp': 'timeliness',
            'notional': 'completeness',
            'quantity': 'completeness',
            'price': 'completeness',
            'desk_id': 'completeness',
            'instrument': 'completeness',
            'client_id': 'completeness'
        }
        
        return kde_dimension_map.get(kde_name, 'completeness')
    
    def _get_dimension_tier(self, dimension: str) -> str:
        """Get tier for a dimension"""
        for tier, dimensions in self.config.dimensions.items():
            if dimension in dimensions:
                return tier
        return 'foundational'  # Default to foundational