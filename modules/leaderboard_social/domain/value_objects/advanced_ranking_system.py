"""
Advanced Ranking System with ELO-style Scoring and Dynamic Adjustments

This module implements sophisticated ranking algorithms including:
- ELO-style competitive ranking
- Dynamic skill rating adjustments
- Performance trend analysis
- Confidence intervals for ratings
- Multi-dimensional scoring
"""

from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import math
import statistics


class RankingAlgorithm(Enum):
    """Different ranking algorithms available"""
    ELO_BASED = "elo_based"
    PERFORMANCE_WEIGHTED = "performance_weighted"
    TREND_ADJUSTED = "trend_adjusted"
    CONFIDENCE_RATED = "confidence_rated"
    HYBRID_COMPOSITE = "hybrid_composite"


class PerformanceTrend(Enum):
    """Performance trend classifications"""
    RAPIDLY_IMPROVING = "rapidly_improving"
    STEADILY_IMPROVING = "steadily_improving"
    STABLE = "stable"
    DECLINING = "declining"
    VOLATILE = "volatile"


@dataclass
class SkillRating:
    """ELO-style skill rating with confidence metrics"""
    rating: float
    confidence: float  # 0.0 to 1.0
    volatility: float  # Measures rating stability
    last_updated: datetime
    games_played: int
    
    def __post_init__(self):
        """Validate skill rating parameters"""
        self.rating = max(0.0, self.rating)
        self.confidence = max(0.0, min(1.0, self.confidence))
        self.volatility = max(0.0, self.volatility)
    
    @property
    def effective_rating(self) -> float:
        """Rating adjusted by confidence"""
        return self.rating * self.confidence
    
    @property
    def rating_range(self) -> Tuple[float, float]:
        """Confidence interval for rating"""
        margin = self.volatility * (1.0 - self.confidence) * 200
        return (self.rating - margin, self.rating + margin)
    
    @property
    def skill_tier(self) -> str:
        """Determine skill tier based on rating"""
        if self.rating >= 2400:
            return "Master"
        elif self.rating >= 2000:
            return "Expert"
        elif self.rating >= 1600:
            return "Advanced"
        elif self.rating >= 1200:
            return "Intermediate"
        elif self.rating >= 800:
            return "Beginner"
        else:
            return "Novice"


@dataclass
class PerformanceMetrics:
    """Comprehensive performance metrics for ranking"""
    success_rate: float
    optimization_count: int
    average_improvement: float
    consistency_score: float  # Variance in performance
    difficulty_factor: float  # Average difficulty of tasks attempted
    recent_performance: List[float]  # Last N performance scores
    
    def __post_init__(self):
        """Calculate derived metrics"""
        if not self.recent_performance:
            self.recent_performance = []
    
    @property
    def performance_trend(self) -> PerformanceTrend:
        """Analyze performance trend from recent data"""
        if len(self.recent_performance) < 3:
            return PerformanceTrend.STABLE
        
        # Calculate trend using linear regression slope
        n = len(self.recent_performance)
        x_values = list(range(n))
        y_values = self.recent_performance
        
        # Simple linear regression
        x_mean = sum(x_values) / n
        y_mean = sum(y_values) / n
        
        numerator = sum((x_values[i] - x_mean) * (y_values[i] - y_mean) for i in range(n))
        denominator = sum((x_values[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return PerformanceTrend.STABLE
        
        slope = numerator / denominator
        
        # Classify trend based on slope and variance
        variance = statistics.variance(y_values) if n > 1 else 0
        
        if variance > 0.3:  # High variance indicates volatility
            return PerformanceTrend.VOLATILE
        elif slope > 0.05:  # Lowered threshold for detecting improvement
            return PerformanceTrend.RAPIDLY_IMPROVING if slope > 0.15 else PerformanceTrend.STEADILY_IMPROVING
        elif slope < -0.05:  # Lowered threshold for detecting decline
            return PerformanceTrend.DECLINING
        else:
            return PerformanceTrend.STABLE
    
    @property
    def momentum_score(self) -> float:
        """Calculate momentum based on recent trend"""
        if len(self.recent_performance) < 2:
            return 1.0
        
        # Weight recent performances more heavily
        weighted_recent = []
        for i, perf in enumerate(self.recent_performance[-5:]):  # Last 5 performances
            weight = (i + 1) / 5  # More recent = higher weight
            weighted_recent.append(perf * weight)
        
        if not weighted_recent:
            return 1.0
        
        momentum = sum(weighted_recent) / len(weighted_recent)
        return max(0.1, min(2.0, momentum))  # Clamp between 0.1 and 2.0


class AdvancedRankingSystem:
    """
    Advanced ranking system with multiple algorithms and dynamic adjustments.
    
    Supports ELO-style competitive ranking, performance trends, and confidence-based ratings.
    """
    
    def __init__(self, initial_rating: float = 1200.0, k_factor: float = 32.0):
        self.initial_rating = initial_rating
        self.k_factor = k_factor  # ELO K-factor for rating adjustments
        self.min_games_for_confidence = 10
        self.volatility_decay = 0.95  # How quickly volatility decreases
        
        # Rating history for trend analysis
        self.rating_history: Dict[str, List[Tuple[datetime, float]]] = {}
        self.performance_cache: Dict[str, PerformanceMetrics] = {}
    
    def calculate_elo_rating(self, 
                           player_rating: float, 
                           opponent_rating: float, 
                           result: float,
                           k_factor: Optional[float] = None) -> float:
        """
        Calculate new ELO rating after a game.
        
        Args:
            player_rating: Current player rating
            opponent_rating: Opponent's rating
            result: Game result (1.0 = win, 0.5 = draw, 0.0 = loss)
            k_factor: Optional custom K-factor
            
        Returns:
            New rating for the player
        """
        k = k_factor or self.k_factor
        
        # Calculate expected score
        expected_score = 1 / (1 + 10 ** ((opponent_rating - player_rating) / 400))
        
        # Calculate new rating
        new_rating = player_rating + k * (result - expected_score)
        
        return max(0.0, new_rating)  # Ensure rating doesn't go negative
    
    def update_skill_rating(self, 
                          user_id: str, 
                          current_rating: SkillRating,
                          performance_result: float,
                          opponent_rating: Optional[float] = None,
                          difficulty_multiplier: float = 1.0) -> SkillRating:
        """
        Update skill rating based on performance.
        
        Args:
            user_id: User identifier
            current_rating: Current skill rating
            performance_result: Performance score (0.0 to 1.0)
            opponent_rating: Rating of opponent (if competitive)
            difficulty_multiplier: Difficulty adjustment factor
            
        Returns:
            Updated skill rating
        """
        # Determine opponent rating for ELO calculation
        if opponent_rating is None:
            # Use average rating as baseline opponent
            opponent_rating = self.initial_rating
        
        # Convert performance to ELO result (performance_result should be 0.0-1.0)
        elo_result = max(0.0, min(1.0, performance_result))
        
        # Calculate new base rating using ELO
        new_base_rating = self.calculate_elo_rating(
            current_rating.rating,
            opponent_rating,
            elo_result,
            k_factor=self.k_factor * difficulty_multiplier
        )
        
        # Update confidence based on games played
        games_played = current_rating.games_played + 1
        confidence_factor = min(1.0, games_played / self.min_games_for_confidence)
        new_confidence = 0.5 + (0.5 * confidence_factor)
        
        # Update volatility (decreases with more games, increases with unexpected results)
        expected_performance = 1 / (1 + 10 ** ((opponent_rating - current_rating.rating) / 400))
        surprise_factor = abs(performance_result - expected_performance)
        
        new_volatility = (current_rating.volatility * self.volatility_decay) + (surprise_factor * 0.2)
        new_volatility = max(0.05, min(0.5, new_volatility))  # Clamp volatility
        
        # Store rating history
        if user_id not in self.rating_history:
            self.rating_history[user_id] = []
        
        self.rating_history[user_id].append((datetime.utcnow(), new_base_rating))
        
        # Keep only recent history (last 100 entries)
        if len(self.rating_history[user_id]) > 100:
            self.rating_history[user_id] = self.rating_history[user_id][-100:]
        
        return SkillRating(
            rating=new_base_rating,
            confidence=new_confidence,
            volatility=new_volatility,
            last_updated=datetime.utcnow(),
            games_played=games_played
        )
    
    def calculate_performance_weighted_score(self, 
                                           metrics: PerformanceMetrics,
                                           base_rating: float = 1200.0) -> float:
        """
        Calculate score using performance-weighted algorithm.
        
        Args:
            metrics: Performance metrics
            base_rating: Base rating to start from
            
        Returns:
            Performance-weighted score
        """
        # Base score from success rate
        success_score = metrics.success_rate * 100
        
        # Volume bonus (diminishing returns)
        volume_bonus = math.log(max(1, metrics.optimization_count)) * 10
        
        # Improvement factor
        improvement_factor = 1.0 + (metrics.average_improvement * 0.5)
        
        # Consistency bonus
        consistency_bonus = (1.0 - (1.0 / (1.0 + metrics.consistency_score))) * 20
        
        # Difficulty adjustment
        difficulty_adjustment = metrics.difficulty_factor * 1.2
        
        # Momentum from recent performance
        momentum = metrics.momentum_score
        
        # Combine all factors
        weighted_score = (
            (success_score + volume_bonus + consistency_bonus) 
            * improvement_factor 
            * difficulty_adjustment 
            * momentum
        )
        
        return base_rating + weighted_score
    
    def calculate_trend_adjusted_score(self, 
                                     user_id: str, 
                                     base_score: float,
                                     metrics: PerformanceMetrics) -> float:
        """
        Adjust score based on performance trends.
        
        Args:
            user_id: User identifier
            base_score: Base score to adjust
            metrics: Performance metrics
            
        Returns:
            Trend-adjusted score
        """
        trend = metrics.performance_trend
        
        # Trend multipliers
        trend_multipliers = {
            PerformanceTrend.RAPIDLY_IMPROVING: 1.15,
            PerformanceTrend.STEADILY_IMPROVING: 1.08,
            PerformanceTrend.STABLE: 1.0,
            PerformanceTrend.DECLINING: 0.95,
            PerformanceTrend.VOLATILE: 0.98
        }
        
        multiplier = trend_multipliers.get(trend, 1.0)
        
        # Additional adjustment based on rating history
        if user_id in self.rating_history and len(self.rating_history[user_id]) >= 5:
            recent_ratings = [rating for _, rating in self.rating_history[user_id][-5:]]
            rating_trend = (recent_ratings[-1] - recent_ratings[0]) / len(recent_ratings)
            
            # Positive trend gets small bonus, negative trend gets small penalty
            trend_bonus = max(-0.05, min(0.05, rating_trend / 1000))
            multiplier += trend_bonus
        
        return base_score * multiplier
    
    def calculate_confidence_rated_score(self, 
                                       skill_rating: SkillRating,
                                       metrics: PerformanceMetrics) -> float:
        """
        Calculate score with confidence intervals.
        
        Args:
            skill_rating: Current skill rating
            metrics: Performance metrics
            
        Returns:
            Confidence-adjusted score
        """
        # Use effective rating (rating * confidence)
        base_score = skill_rating.effective_rating
        
        # Penalize high volatility
        volatility_penalty = skill_rating.volatility * 50
        
        # Bonus for consistent performance
        consistency_bonus = (1.0 - skill_rating.volatility) * metrics.consistency_score * 25
        
        # Recent performance influence
        momentum_adjustment = (metrics.momentum_score - 1.0) * 100
        
        final_score = base_score - volatility_penalty + consistency_bonus + momentum_adjustment
        
        return max(0.0, final_score)
    
    def calculate_hybrid_composite_score(self, 
                                       user_id: str,
                                       skill_rating: SkillRating,
                                       metrics: PerformanceMetrics) -> Dict[str, Any]:
        """
        Calculate comprehensive score using hybrid approach.
        
        Args:
            user_id: User identifier
            skill_rating: Current skill rating
            metrics: Performance metrics
            
        Returns:
            Dictionary with composite score and breakdown
        """
        # Calculate individual algorithm scores
        elo_score = skill_rating.rating
        performance_score = self.calculate_performance_weighted_score(metrics)
        trend_score = self.calculate_trend_adjusted_score(user_id, elo_score, metrics)
        confidence_score = self.calculate_confidence_rated_score(skill_rating, metrics)
        
        # Weighted combination
        weights = {
            'elo': 0.3,
            'performance': 0.25,
            'trend': 0.25,
            'confidence': 0.2
        }
        
        composite_score = (
            elo_score * weights['elo'] +
            performance_score * weights['performance'] +
            trend_score * weights['trend'] +
            confidence_score * weights['confidence']
        )
        
        return {
            'composite_score': composite_score,
            'breakdown': {
                'elo_score': elo_score,
                'performance_score': performance_score,
                'trend_score': trend_score,
                'confidence_score': confidence_score
            },
            'weights': weights,
            'skill_tier': skill_rating.skill_tier,
            'performance_trend': metrics.performance_trend.value,
            'confidence_level': skill_rating.confidence,
            'rating_range': skill_rating.rating_range
        }
    
    def rank_users(self, 
                   user_data: Dict[str, Tuple[SkillRating, PerformanceMetrics]],
                   algorithm: RankingAlgorithm = RankingAlgorithm.HYBRID_COMPOSITE) -> List[Dict[str, Any]]:
        """
        Rank users using specified algorithm.
        
        Args:
            user_data: Dictionary mapping user_id to (SkillRating, PerformanceMetrics)
            algorithm: Ranking algorithm to use
            
        Returns:
            Sorted list of user rankings
        """
        rankings = []
        
        for user_id, (skill_rating, metrics) in user_data.items():
            if algorithm == RankingAlgorithm.ELO_BASED:
                score = skill_rating.effective_rating
                breakdown = {'elo_rating': skill_rating.rating, 'confidence': skill_rating.confidence}
            
            elif algorithm == RankingAlgorithm.PERFORMANCE_WEIGHTED:
                score = self.calculate_performance_weighted_score(metrics)
                breakdown = {'performance_weighted': score}
            
            elif algorithm == RankingAlgorithm.TREND_ADJUSTED:
                base_score = skill_rating.rating
                score = self.calculate_trend_adjusted_score(user_id, base_score, metrics)
                breakdown = {'trend_adjusted': score, 'base_score': base_score}
            
            elif algorithm == RankingAlgorithm.CONFIDENCE_RATED:
                score = self.calculate_confidence_rated_score(skill_rating, metrics)
                breakdown = {'confidence_rated': score}
            
            else:  # HYBRID_COMPOSITE
                result = self.calculate_hybrid_composite_score(user_id, skill_rating, metrics)
                score = result['composite_score']
                breakdown = result['breakdown']
            
            rankings.append({
                'user_id': user_id,
                'score': score,
                'skill_rating': skill_rating,
                'performance_metrics': metrics,
                'score_breakdown': breakdown,
                'algorithm_used': algorithm.value
            })
        
        # Sort by score (descending)
        rankings.sort(key=lambda x: x['score'], reverse=True)
        
        # Add rank positions
        for i, ranking in enumerate(rankings):
            ranking['rank'] = i + 1
        
        return rankings
    
    def predict_future_rating(self, 
                            user_id: str,
                            current_rating: SkillRating,
                            projected_games: int,
                            expected_performance: float = 0.5) -> Dict[str, Any]:
        """
        Predict future rating based on current trends.
        
        Args:
            user_id: User identifier
            current_rating: Current skill rating
            projected_games: Number of future games to simulate
            expected_performance: Expected average performance (0.0 to 1.0)
            
        Returns:
            Prediction data including confidence intervals
        """
        if user_id not in self.rating_history or len(self.rating_history[user_id]) < 3:
            return {
                'predicted_rating': current_rating.rating,
                'confidence_low': current_rating.rating - 100,
                'confidence_high': current_rating.rating + 100,
                'prediction_accuracy': 'low'
            }
        
        # Analyze historical trend
        recent_history = self.rating_history[user_id][-10:]
        time_diffs = []
        rating_changes = []
        
        for i in range(1, len(recent_history)):
            time_diff = (recent_history[i][0] - recent_history[i-1][0]).total_seconds()
            rating_change = recent_history[i][1] - recent_history[i-1][1]
            time_diffs.append(time_diff)
            rating_changes.append(rating_change)
        
        # Calculate average change per game
        avg_change = statistics.mean(rating_changes) if rating_changes else 0
        change_variance = statistics.variance(rating_changes) if len(rating_changes) > 1 else 100
        
        # Project future rating
        projected_change = avg_change * projected_games
        
        # Apply performance expectation adjustment
        performance_factor = (expected_performance - 0.5) * 2  # Convert to -1 to 1 scale
        performance_adjustment = performance_factor * 50 * projected_games
        
        predicted_rating = current_rating.rating + projected_change + performance_adjustment
        
        # Calculate confidence intervals
        uncertainty = math.sqrt(change_variance * projected_games)
        confidence_low = predicted_rating - uncertainty
        confidence_high = predicted_rating + uncertainty
        
        # Determine prediction accuracy
        if len(rating_changes) >= 10 and change_variance < 1000:
            accuracy = 'high'
        elif len(rating_changes) >= 5 and change_variance < 2500:
            accuracy = 'medium'
        else:
            accuracy = 'low'
        
        return {
            'predicted_rating': predicted_rating,
            'confidence_low': confidence_low,
            'confidence_high': confidence_high,
            'prediction_accuracy': accuracy,
            'projected_games': projected_games,
            'historical_trend': avg_change,
            'uncertainty': uncertainty
        }