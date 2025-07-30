"""
LeaderboardEntry entity for representing user positions and statistics in leaderboards

This entity represents a user's entry in a leaderboard with their ranking,
statistics, and metadata for a specific time period or category.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional, List
import uuid


@dataclass
class LeaderboardEntry:
    """
    Entity representing a user's position and statistics in a leaderboard.
    
    This is the core entity for leaderboard functionality, containing
    user performance data and ranking information.
    """
    user_id: str
    rank: int
    user_name: str
    
    # Core performance metrics
    success_rate: float
    total_optimizations: int
    successful_optimizations: int
    current_streak: int
    best_streak: int
    level: int
    total_xp: int
    
    # Time period specific metrics
    period_optimizations: Optional[int] = None
    period_successes: Optional[int] = None
    period_success_rate: Optional[float] = None
    period_xp_gained: Optional[int] = None
    
    # Category specific metrics
    category_score: Optional[float] = None
    category_rank: Optional[int] = None
    
    # Composite scoring
    composite_score: Optional[float] = None
    score_breakdown: Optional[Dict[str, float]] = None
    
    # Social and display data
    achievements: Optional[List[str]] = None
    badges: Optional[List[str]] = None
    team_name: Optional[str] = None
    
    # Privacy and visibility
    is_visible: bool = True
    show_stats: bool = True
    
    # Metadata
    entry_id: str = None
    created_at: datetime = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Initialize entity with generated values if not provided"""
        if self.entry_id is None:
            self.entry_id = str(uuid.uuid4())
        
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        
        # Validate basic constraints
        if self.rank < 1:
            raise ValueError("Rank must be positive")
        
        if not 0 <= self.success_rate <= 100:
            raise ValueError("Success rate must be between 0 and 100")
        
        if self.total_optimizations < 0:
            raise ValueError("Total optimizations cannot be negative")
        
        if self.successful_optimizations > self.total_optimizations:
            raise ValueError("Successful optimizations cannot exceed total optimizations")
    
    def update_rank(self, new_rank: int) -> None:
        """
        Update the user's rank in the leaderboard.
        
        Args:
            new_rank: The new rank position
        """
        if new_rank < 1:
            raise ValueError("Rank must be positive")
        
        self.rank = new_rank
        self.updated_at = datetime.utcnow()
    
    def update_statistics(self, 
                         success_rate: Optional[float] = None,
                         total_optimizations: Optional[int] = None,
                         successful_optimizations: Optional[int] = None,
                         current_streak: Optional[int] = None,
                         level: Optional[int] = None,
                         total_xp: Optional[int] = None) -> None:
        """
        Update user statistics in the leaderboard entry.
        
        Args:
            success_rate: Updated success rate
            total_optimizations: Updated total optimization count
            successful_optimizations: Updated successful optimization count
            current_streak: Updated current streak
            level: Updated user level
            total_xp: Updated total XP
        """
        if success_rate is not None:
            if not 0 <= success_rate <= 100:
                raise ValueError("Success rate must be between 0 and 100")
            self.success_rate = success_rate
        
        if total_optimizations is not None:
            if total_optimizations < 0:
                raise ValueError("Total optimizations cannot be negative")
            self.total_optimizations = total_optimizations
        
        if successful_optimizations is not None:
            if successful_optimizations < 0:
                raise ValueError("Successful optimizations cannot be negative")
            if hasattr(self, 'total_optimizations') and successful_optimizations > self.total_optimizations:
                raise ValueError("Successful optimizations cannot exceed total optimizations")
            self.successful_optimizations = successful_optimizations
        
        if current_streak is not None:
            if current_streak < 0:
                raise ValueError("Current streak cannot be negative")
            self.current_streak = current_streak
            
            # Update best streak if current exceeds it
            if current_streak > self.best_streak:
                self.best_streak = current_streak
        
        if level is not None:
            if level < 1:
                raise ValueError("Level must be positive")
            self.level = level
        
        if total_xp is not None:
            if total_xp < 0:
                raise ValueError("Total XP cannot be negative")
            self.total_xp = total_xp
        
        self.updated_at = datetime.utcnow()
    
    def set_period_statistics(self,
                            period_optimizations: int,
                            period_successes: int,
                            period_xp_gained: int) -> None:
        """
        Set statistics specific to a time period.
        
        Args:
            period_optimizations: Optimizations in this period
            period_successes: Successes in this period
            period_xp_gained: XP gained in this period
        """
        if period_optimizations < 0:
            raise ValueError("Period optimizations cannot be negative")
        
        if period_successes < 0 or period_successes > period_optimizations:
            raise ValueError("Period successes must be between 0 and period optimizations")
        
        if period_xp_gained < 0:
            raise ValueError("Period XP gained cannot be negative")
        
        self.period_optimizations = period_optimizations
        self.period_successes = period_successes
        self.period_xp_gained = period_xp_gained
        
        # Calculate period success rate
        if period_optimizations > 0:
            self.period_success_rate = (period_successes / period_optimizations) * 100
        else:
            self.period_success_rate = 0.0
        
        self.updated_at = datetime.utcnow()
    
    def set_category_statistics(self, category_score: float, category_rank: int) -> None:
        """
        Set statistics specific to a category.
        
        Args:
            category_score: Score in the specific category
            category_rank: Rank in the specific category
        """
        if category_rank < 1:
            raise ValueError("Category rank must be positive")
        
        if not 0 <= category_score <= 100:
            raise ValueError("Category score must be between 0 and 100")
        
        self.category_score = category_score
        self.category_rank = category_rank
        self.updated_at = datetime.utcnow()
    
    def set_composite_score(self, composite_score: float, score_breakdown: Dict[str, float]) -> None:
        """
        Set the composite score and its breakdown.
        
        Args:
            composite_score: Total composite score
            score_breakdown: Breakdown of score components
        """
        if composite_score < 0:
            raise ValueError("Composite score cannot be negative")
        
        self.composite_score = composite_score
        self.score_breakdown = score_breakdown.copy() if score_breakdown else {}
        self.updated_at = datetime.utcnow()
    
    def add_achievement(self, achievement_id: str) -> None:
        """
        Add an achievement to the user's profile.
        
        Args:
            achievement_id: ID of the achievement to add
        """
        if self.achievements is None:
            self.achievements = []
        
        if achievement_id not in self.achievements:
            self.achievements.append(achievement_id)
            self.updated_at = datetime.utcnow()
    
    def add_badge(self, badge_name: str) -> None:
        """
        Add a badge to the user's profile.
        
        Args:
            badge_name: Name of the badge to add
        """
        if self.badges is None:
            self.badges = []
        
        if badge_name not in self.badges:
            self.badges.append(badge_name)
            self.updated_at = datetime.utcnow()
    
    def set_privacy_settings(self, is_visible: bool, show_stats: bool) -> None:
        """
        Update privacy settings for the leaderboard entry.
        
        Args:
            is_visible: Whether the user appears in leaderboards
            show_stats: Whether the user's stats are visible to others
        """
        self.is_visible = is_visible
        self.show_stats = show_stats
        self.updated_at = datetime.utcnow()
    
    def get_display_data(self) -> Dict[str, Any]:
        """
        Get data suitable for displaying in leaderboard UI.
        
        Returns:
            Dictionary with display-friendly data
        """
        data = {
            "rank": self.rank,
            "user_name": self.user_name,
            "level": self.level,
            "success_rate": self.success_rate,
            "current_streak": self.current_streak,
            "total_optimizations": self.total_optimizations
        }
        
        # Add period-specific data if available
        if self.period_success_rate is not None:
            data["period_success_rate"] = self.period_success_rate
        
        if self.period_optimizations is not None:
            data["period_optimizations"] = self.period_optimizations
        
        # Add category data if available
        if self.category_score is not None:
            data["category_score"] = self.category_score
        
        # Add composite score if available
        if self.composite_score is not None:
            data["composite_score"] = self.composite_score
        
        # Add social data if show_stats is True
        if self.show_stats:
            if self.badges:
                data["badges"] = self.badges.copy()
            
            if self.team_name:
                data["team_name"] = self.team_name
        
        return data
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert leaderboard entry to dictionary representation.
        
        Returns:
            Dictionary representation of the entry
        """
        return {
            "entry_id": self.entry_id,
            "user_id": self.user_id,
            "rank": self.rank,
            "user_name": self.user_name,
            "success_rate": self.success_rate,
            "total_optimizations": self.total_optimizations,
            "successful_optimizations": self.successful_optimizations,
            "current_streak": self.current_streak,
            "best_streak": self.best_streak,
            "level": self.level,
            "total_xp": self.total_xp,
            "period_optimizations": self.period_optimizations,
            "period_successes": self.period_successes,
            "period_success_rate": self.period_success_rate,
            "period_xp_gained": self.period_xp_gained,
            "category_score": self.category_score,
            "category_rank": self.category_rank,
            "composite_score": self.composite_score,
            "score_breakdown": self.score_breakdown,
            "achievements": self.achievements,
            "badges": self.badges,
            "team_name": self.team_name,
            "is_visible": self.is_visible,
            "show_stats": self.show_stats,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LeaderboardEntry':
        """
        Create LeaderboardEntry from dictionary data.
        
        Args:
            data: Dictionary containing entry data
            
        Returns:
            LeaderboardEntry instance
        """
        # Parse datetime fields
        created_at = None
        if data.get("created_at"):
            created_at = datetime.fromisoformat(data["created_at"].replace('Z', '+00:00'))
        
        updated_at = None
        if data.get("updated_at"):
            updated_at = datetime.fromisoformat(data["updated_at"].replace('Z', '+00:00'))
        
        return cls(
            entry_id=data.get("entry_id"),
            user_id=data["user_id"],
            rank=data["rank"],
            user_name=data["user_name"],
            success_rate=data["success_rate"],
            total_optimizations=data["total_optimizations"],
            successful_optimizations=data["successful_optimizations"],
            current_streak=data["current_streak"],
            best_streak=data["best_streak"],
            level=data["level"],
            total_xp=data["total_xp"],
            period_optimizations=data.get("period_optimizations"),
            period_successes=data.get("period_successes"),
            period_success_rate=data.get("period_success_rate"),
            period_xp_gained=data.get("period_xp_gained"),
            category_score=data.get("category_score"),
            category_rank=data.get("category_rank"),
            composite_score=data.get("composite_score"),
            score_breakdown=data.get("score_breakdown"),
            achievements=data.get("achievements"),
            badges=data.get("badges"),
            team_name=data.get("team_name"),
            is_visible=data.get("is_visible", True),
            show_stats=data.get("show_stats", True),
            created_at=created_at,
            updated_at=updated_at
        )