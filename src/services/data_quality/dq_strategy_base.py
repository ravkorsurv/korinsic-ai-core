"""
Data Quality Scoring Strategy Base Interface

Defines the abstract interface for DQSI scoring strategies.
Supports both fallback (lightweight) and role_aware (full-featured) modes.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class KDEResult:
    """Result for a single KDE (Key Data Element) scoring"""
    kde_name: str
    score: float  # 0.0-1.0 (0.0=failed/missing, 0.6=imputed, 1.0=passed)
    risk_tier: str  # 'high', 'medium', 'low'
    risk_weight: int  # 3, 2, 1
    dimension: str  # Which DQ dimension this KDE belongs to
    tier: str  # 'foundational' or 'enhanced'
    is_synthetic: bool = False  # True for synthetic KDEs (timeliness, coverage)
    imputed: bool = False  # True if value was inferred/imputed
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DQSIOutput:
    """Complete DQSI output for injection into alerts/cases"""
    dqsi_score: float
    dqsi_confidence_index: float
    dqsi_mode: str  # 'fallback' or 'role_aware'
    dqsi_critical_kdes_missing: List[str]
    dqsi_sub_scores: Dict[str, float]  # dimension scores
    dqsi_kde_weights: Dict[str, int]  # KDE risk weights
    dqsi_confidence_note: str
    kde_results: List[KDEResult] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class DQConfig:
    """Configuration for DQSI calculations"""
    # Strategy mode
    dq_strategy: str = 'fallback'  # 'fallback' or 'role_aware'
    
    # 7 DQ Dimensions organized in 2 tiers
    dimensions: Dict[str, List[str]] = field(default_factory=lambda: {
        'foundational': ['completeness', 'conformity', 'timeliness', 'coverage'],
        'enhanced': ['accuracy', 'uniqueness', 'consistency']
    })
    
    # Tier weights
    dimension_tier_weights: Dict[str, float] = field(default_factory=lambda: {
        'foundational': 1.0,
        'enhanced': 0.75
    })
    
    # KDE risk tiers
    kde_risk_tiers: Dict[str, str] = field(default_factory=lambda: {
        'trader_id': 'high',
        'trade_time': 'high', 
        'order_timestamp': 'high',
        'notional': 'medium',
        'quantity': 'medium',
        'price': 'medium',
        'desk_id': 'low',
        'instrument': 'low',
        'client_id': 'low'
    })
    
    # Risk weights
    risk_weights: Dict[str, int] = field(default_factory=lambda: {
        'high': 3,
        'medium': 2, 
        'low': 1
    })
    
    # Critical KDEs and cap
    critical_kdes: List[str] = field(default_factory=lambda: ['trader_id', 'order_timestamp'])
    dqsi_critical_cap: float = 0.75
    
    # Synthetic KDE settings
    synthetic_kdes: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        'timeliness': {
            'weight': 3,
            'dimension': 'timeliness',
            'tier': 'foundational',
            'scoring_bands': {
                '<1h': 1.0,
                '1-6h': 0.9,
                '6-24h': 0.75,
                '1-2d': 0.6,
                '>2d': 0.3,
                'missing': 0.0
            }
        },
        'coverage': {
            'weight': 3,
            'dimension': 'coverage', 
            'tier': 'foundational',
            'scoring_bands': {
                '0-10%': 1.0,
                '10-20%': 0.9,
                '20-40%': 0.75,
                '40-60%': 0.5,
                '>60%': 0.25,
                'no_baseline': 0.0
            }
        }
    })
    
    # Confidence index parameters
    confidence_params: Dict[str, float] = field(default_factory=lambda: {
        'imputation_penalty': 0.1,
        'missing_kde_penalty': 0.05,
        'fallback_mode_modifier': 0.8
    })


class DQScoringStrategy(ABC):
    """Abstract base class for DQSI scoring strategies"""
    
    def __init__(self, config: DQConfig):
        self.config = config
        
    @abstractmethod
    def score_kdes(self, data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> List[KDEResult]:
        """
        Score individual KDEs based on strategy
        
        Args:
            data: Input data containing KDEs
            metadata: Optional metadata (role info, etc.)
            
        Returns:
            List of KDE scoring results
        """
        pass
    
    @abstractmethod
    def get_strategy_name(self) -> str:
        """Return strategy name"""
        pass
    
    def calculate_dqsi_score(self, kde_results: List[KDEResult]) -> float:
        """
        Calculate overall DQSI score from KDE results using weighted average
        
        Args:
            kde_results: List of KDE scoring results
            
        Returns:
            DQSI score (0.0-1.0)
        """
        if not kde_results:
            return 0.0
        
        total_weighted_score = 0.0
        total_weight = 0.0
        
        for kde_result in kde_results:
            # Get tier weight
            tier_weight = self.config.dimension_tier_weights.get(kde_result.tier, 1.0)
            
            # Calculate weighted score
            weight = kde_result.risk_weight * tier_weight
            total_weighted_score += kde_result.score * weight
            total_weight += weight
        
        dqsi_score = total_weighted_score / total_weight if total_weight > 0 else 0.0
        
        # Apply critical KDE cap
        critical_kdes_missing = [
            kde.kde_name for kde in kde_results 
            if kde.kde_name in self.config.critical_kdes and kde.score == 0.0
        ]
        
        if critical_kdes_missing:
            dqsi_score = min(dqsi_score, self.config.dqsi_critical_cap)
        
        return dqsi_score
    
    def calculate_confidence_index(self, kde_results: List[KDEResult], dqsi_score: float) -> Tuple[float, str]:
        """
        Calculate DQSI confidence index
        
        Args:
            kde_results: List of KDE results
            dqsi_score: Calculated DQSI score
            
        Returns:
            Tuple of (confidence_index, confidence_note)
        """
        if not kde_results:
            return 0.0, "No KDEs available for scoring"
        
        # Calculate metrics
        total_kdes = len(kde_results)
        present_kdes = len([kde for kde in kde_results if kde.score > 0.0])
        imputed_kdes = len([kde for kde in kde_results if kde.imputed])
        critical_missing = len([
            kde for kde in kde_results 
            if kde.kde_name in self.config.critical_kdes and kde.score == 0.0
        ])
        
        # Calculate base metrics
        kde_coverage = present_kdes / total_kdes if total_kdes > 0 else 0.0
        sub_dimension_fill = kde_coverage  # Same for KDE-level scoring
        imputation_rate = imputed_kdes / total_kdes if total_kdes > 0 else 0.0
        
        # Base confidence calculation
        base_confidence = (
            (kde_coverage + sub_dimension_fill) / 2
            - self.config.confidence_params['missing_kde_penalty'] * critical_missing
            - self.config.confidence_params['imputation_penalty'] * imputation_rate
        )
        
        # Apply mode modifier
        mode_modifier = (
            self.config.confidence_params['fallback_mode_modifier'] 
            if self.get_strategy_name() == 'fallback' 
            else 1.0
        )
        
        confidence_index = max(0.0, min(1.0, base_confidence * mode_modifier))
        
        # Generate confidence note
        confidence_note = f"{critical_missing} high-risk KDE missing, {imputation_rate:.0%} imputed"
        if self.get_strategy_name() == 'fallback':
            confidence_note += ", fallback weight applied"
        
        return confidence_index, confidence_note
    
    def calculate_dimension_scores(self, kde_results: List[KDEResult]) -> Dict[str, float]:
        """Calculate sub-scores for each dimension"""
        dimension_scores = {}
        
        # Group KDEs by dimension
        dimension_kdes = {}
        for kde in kde_results:
            if kde.dimension not in dimension_kdes:
                dimension_kdes[kde.dimension] = []
            dimension_kdes[kde.dimension].append(kde)
        
        # Calculate score for each dimension
        for dimension, kdes in dimension_kdes.items():
            if kdes:
                total_weighted_score = 0.0
                total_weight = 0.0
                
                for kde in kdes:
                    tier_weight = self.config.dimension_tier_weights.get(kde.tier, 1.0)
                    weight = kde.risk_weight * tier_weight
                    total_weighted_score += kde.score * weight
                    total_weight += weight
                
                dimension_scores[dimension] = (
                    total_weighted_score / total_weight if total_weight > 0 else 0.0
                )
            else:
                dimension_scores[dimension] = 0.0
        
        return dimension_scores
    
    def create_synthetic_kdes(self, data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> List[KDEResult]:
        """Create synthetic KDEs for system-level metrics"""
        synthetic_kdes = []
        
        # Timeliness synthetic KDE
        if 'timeliness' in self.config.synthetic_kdes:
            timeliness_score = self._calculate_timeliness_score(data, metadata)
            synthetic_kdes.append(KDEResult(
                kde_name='synthetic_timeliness',
                score=timeliness_score,
                risk_tier='high',
                risk_weight=self.config.synthetic_kdes['timeliness']['weight'],
                dimension='timeliness',
                tier='foundational',
                is_synthetic=True,
                details={'type': 'feed_delay_monitoring'}
            ))
        
        # Coverage synthetic KDE  
        if 'coverage' in self.config.synthetic_kdes:
            coverage_score = self._calculate_coverage_score(data, metadata)
            synthetic_kdes.append(KDEResult(
                kde_name='synthetic_coverage',
                score=coverage_score,
                risk_tier='high', 
                risk_weight=self.config.synthetic_kdes['coverage']['weight'],
                dimension='coverage',
                tier='foundational',
                is_synthetic=True,
                details={'type': 'volume_drop_monitoring'}
            ))
        
        return synthetic_kdes
    
    def _calculate_timeliness_score(self, data: Dict[str, Any], metadata: Optional[Dict[str, Any]]) -> float:
        """Calculate timeliness synthetic KDE score based on feed delay"""
        # Extract timestamp if available
        timestamp_fields = ['timestamp', 'trade_time', 'order_timestamp', 'created_at']
        
        for field in timestamp_fields:
            if field in data:
                try:
                    data_time = datetime.fromisoformat(str(data[field]).replace('Z', '+00:00'))
                    current_time = datetime.now(data_time.tzinfo)
                    delay_hours = (current_time - data_time).total_seconds() / 3600
                    
                    # Score based on delay bands
                    if delay_hours < 1:
                        return 1.0
                    elif delay_hours < 6:
                        return 0.9
                    elif delay_hours < 24:
                        return 0.75
                    elif delay_hours < 48:
                        return 0.6
                    else:
                        return 0.3
                        
                except (ValueError, TypeError):
                    continue
        
        # No valid timestamp found
        return 0.0
    
    def _calculate_coverage_score(self, data: Dict[str, Any], metadata: Optional[Dict[str, Any]]) -> float:
        """Calculate coverage synthetic KDE score based on volume/value drop"""
        # This would typically compare against historical baselines
        # For now, return a default score indicating need for baseline data
        
        if metadata and 'baseline_volume' in metadata:
            current_volume = metadata.get('current_volume', 0)
            baseline_volume = metadata['baseline_volume']
            
            if baseline_volume > 0:
                drop_percentage = max(0, (baseline_volume - current_volume) / baseline_volume)
                
                if drop_percentage <= 0.1:
                    return 1.0
                elif drop_percentage <= 0.2:
                    return 0.9
                elif drop_percentage <= 0.4:
                    return 0.75
                elif drop_percentage <= 0.6:
                    return 0.5
                else:
                    return 0.25
        
        # No baseline available
        return 0.0