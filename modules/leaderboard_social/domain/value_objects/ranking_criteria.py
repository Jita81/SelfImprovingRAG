"""
RankingCriteria value object for leaderboard scoring and ranking

This value object defines how users are ranked in leaderboards based on
various metrics and weighting systems.
"""

from dataclasses import dataclass
from typing import Dict, Any, List, Tuple
from enum import Enum


class RankingType(Enum):
    """Enumeration of supported ranking criteria types"""
    DEFAULT = "default"
    STREAK_FOCUSED = "streak_focused" 
    VOLUME_FOCUSED = "volume_focused"
    SUCCESS_FOCUSED = "success_focused"
    LEVEL_FOCUSED = "level_focused"


@dataclass(frozen=True)
class RankingCriteria:
    """
    Value object representing leaderboard ranking criteria.
    
    Defines how users are scored and ranked based on various metrics
    with configurable weights and primary/secondary sorting.
    """
    ranking_type: RankingType
    primary_metric: str
    secondary_metric: str
    tertiary_metric: str
    weights: Dict[str, float]
    
    def __post_init__(self):
        """Validate ranking criteria configuration"""
        if self.ranking_type not in RankingType:
            raise ValueError(f"Invalid ranking type: {self.ranking_type}")
        
        # Validate that all weights are positive and sum to reasonable value
        if not all(weight >= 0 for weight in self.weights.values()):
            raise ValueError("All weights must be non-negative")
        
        # Validate primary metrics exist in weights
        required_metrics = {self.primary_metric, self.secondary_metric, self.tertiary_metric}
        if not required_metrics.issubset(set(self.weights.keys())):
            missing = required_metrics - set(self.weights.keys())
            raise ValueError(f"Missing weights for metrics: {missing}")
    
    def calculate_composite_score(self, user_stats: Dict[str, Any]) -> Tuple[float, Dict[str, float]]:
        """
        Calculate composite score for a user based on their statistics.
        
        Args:
            user_stats: Dictionary containing user performance metrics
            
        Returns:
            Tuple of (total_score, score_breakdown)
        """
        score_breakdown = {}
        total_score = 0.0
        
        # Calculate weighted scores for each metric
        for metric, weight in self.weights.items():
            if metric in user_stats:
                raw_value = float(user_stats[metric])
                
                # Normalize different types of metrics
                normalized_value = self._normalize_metric(metric, raw_value)
                
                # Apply weight to get component score
                component_score = normalized_value * weight
                score_breakdown[f"{metric}_score"] = component_score
                total_score += component_score
        
        return total_score, score_breakdown
    
    def _normalize_metric(self, metric: str, value: float) -> float:
        """
        Normalize different types of metrics to comparable scales.
        
        Args:
            metric: The metric name
            value: The raw metric value
            
        Returns:
            Normalized value (typically 0-100 scale)
        """
        # Success rate is already a percentage (0-100)
        if "success_rate" in metric:
            return value
        
        # Level scaling (assuming max level ~20)
        if "level" in metric:
            return min(value * 5, 100)  # Scale levels to 0-100
        
        # Optimization counts (use logarithmic scaling)
        if "optimization" in metric:
            if value <= 0:
                return 0
            # Scale optimizations: log base for large numbers
            return min(value * 0.3, 100)  # Scale to 0-100 range
        
        # Streak scaling (assuming max reasonable streak ~50)
        if "streak" in metric:
            return min(value * 2, 100)  # Scale streaks to 0-100
        
        # XP scaling (assuming typical XP in thousands)
        if "xp" in metric:
            return min(value / 50, 100)  # Scale XP to 0-100
        
        # Default: assume value is already in good range
        return min(value, 100)
    
    def compare_users(self, user1_stats: Dict[str, Any], user2_stats: Dict[str, Any]) -> int:
        """
        Compare two users based on ranking criteria.
        
        Args:
            user1_stats: Statistics for first user
            user2_stats: Statistics for second user
            
        Returns:
            -1 if user1 ranks higher, 1 if user2 ranks higher, 0 if tied
        """
        # Calculate composite scores
        score1, _ = self.calculate_composite_score(user1_stats)
        score2, _ = self.calculate_composite_score(user2_stats)
        
        # Compare composite scores first
        if abs(score1 - score2) > 0.01:  # Small tolerance for floating point
            return -1 if score1 > score2 else 1
        
        # If composite scores are tied, use hierarchical comparison
        return self._hierarchical_compare(user1_stats, user2_stats)
    
    def _hierarchical_compare(self, user1_stats: Dict[str, Any], user2_stats: Dict[str, Any]) -> int:
        """
        Compare users using hierarchical metric ordering (primary, secondary, tertiary).
        
        Args:
            user1_stats: Statistics for first user
            user2_stats: Statistics for second user
            
        Returns:
            -1 if user1 ranks higher, 1 if user2 ranks higher, 0 if tied
        """
        metrics = [self.primary_metric, self.secondary_metric, self.tertiary_metric]
        
        for metric in metrics:
            if metric in user1_stats and metric in user2_stats:
                val1 = float(user1_stats[metric])
                val2 = float(user2_stats[metric])
                
                if abs(val1 - val2) > 0.01:  # Small tolerance
                    return -1 if val1 > val2 else 1
        
        # All metrics are tied
        return 0
    
    def get_ranking_description(self) -> str:
        """
        Get human-readable description of ranking criteria.
        
        Returns:
            String description of how ranking works
        """
        descriptions = {
            RankingType.DEFAULT: f"Balanced ranking: {self.primary_metric} ({self.weights.get(self.primary_metric, 0):.0%}), "
                                 f"{self.secondary_metric} ({self.weights.get(self.secondary_metric, 0):.0%}), "
                                 f"{self.tertiary_metric} ({self.weights.get(self.tertiary_metric, 0):.0%})",
            RankingType.STREAK_FOCUSED: f"Streak-focused ranking prioritizing {self.primary_metric}",
            RankingType.VOLUME_FOCUSED: f"Volume-focused ranking prioritizing {self.primary_metric}",
            RankingType.SUCCESS_FOCUSED: f"Success-focused ranking prioritizing {self.primary_metric}",
            RankingType.LEVEL_FOCUSED: f"Level-focused ranking prioritizing {self.primary_metric}"
        }
        return descriptions.get(self.ranking_type, f"Custom ranking based on {self.primary_metric}")
    
    @classmethod
    def create_default(cls) -> 'RankingCriteria':
        """Create default balanced ranking criteria"""
        return cls(
            ranking_type=RankingType.DEFAULT,
            primary_metric="success_rate",
            secondary_metric="total_optimizations",
            tertiary_metric="current_streak",
            weights={
                "success_rate": 0.4,
                "total_optimizations": 0.3,
                "current_streak": 0.2,
                "level": 0.1
            }
        )
    
    @classmethod
    def create_streak_focused(cls) -> 'RankingCriteria':
        """Create streak-focused ranking criteria"""
        return cls(
            ranking_type=RankingType.STREAK_FOCUSED,
            primary_metric="current_streak",
            secondary_metric="success_rate",
            tertiary_metric="total_optimizations",
            weights={
                "current_streak": 0.5,
                "success_rate": 0.3,
                "total_optimizations": 0.2
            }
        )
    
    @classmethod
    def create_volume_focused(cls) -> 'RankingCriteria':
        """Create volume-focused ranking criteria"""
        return cls(
            ranking_type=RankingType.VOLUME_FOCUSED,
            primary_metric="total_optimizations",
            secondary_metric="success_rate", 
            tertiary_metric="current_streak",
            weights={
                "total_optimizations": 0.5,
                "success_rate": 0.4,
                "current_streak": 0.1
            }
        )
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RankingCriteria':
        """Create ranking criteria from dictionary data"""
        return cls(
            ranking_type=RankingType(data["ranking_type"]) if isinstance(data["ranking_type"], str) else data["ranking_type"],
            primary_metric=data["primary"],
            secondary_metric=data["secondary"],
            tertiary_metric=data["tertiary"],
            weights=data["weights"]
        )