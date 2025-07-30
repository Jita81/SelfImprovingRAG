"""
Request DTOs for Leaderboard Service

Data transfer objects for handling leaderboard service requests
with validation and type safety.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime


@dataclass
class GetLeaderboardRequest:
    """Request for retrieving leaderboard data with filtering options"""
    
    period: str  # "daily", "weekly", "monthly", "all_time"
    limit: int = 10
    offset: int = 0
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    category: Optional[str] = None
    team_name: Optional[str] = None
    ranking_criteria: str = "default"
    respect_privacy: bool = True
    
    def validate(self) -> None:
        """Validate the request parameters"""
        valid_periods = ["daily", "weekly", "monthly", "all_time"]
        if self.period not in valid_periods:
            raise ValueError(f"Period must be one of: {valid_periods}")
        
        if self.limit <= 0 or self.limit > 100:
            raise ValueError("Limit must be between 1 and 100")
        
        if self.offset < 0:
            raise ValueError("Offset cannot be negative")
        
        valid_criteria = ["default", "streak_focused", "volume_focused"]
        if self.ranking_criteria not in valid_criteria:
            raise ValueError(f"Ranking criteria must be one of: {valid_criteria}")


@dataclass
class UpdateUserStatsRequest:
    """Request for updating user statistics in leaderboard"""
    
    user_id: str
    success_rate: Optional[float] = None
    total_optimizations: Optional[int] = None
    successful_optimizations: Optional[int] = None
    current_streak: Optional[int] = None
    level: Optional[int] = None
    total_xp: Optional[int] = None
    optimization_result: Optional[bool] = None  # For streak tracking
    
    def validate(self) -> None:
        """Validate the request parameters"""
        if not self.user_id:
            raise ValueError("User ID is required")
        
        if self.success_rate is not None and not (0 <= self.success_rate <= 100):
            raise ValueError("Success rate must be between 0 and 100")
        
        if self.total_optimizations is not None and self.total_optimizations < 0:
            raise ValueError("Total optimizations cannot be negative")
        
        if self.successful_optimizations is not None and self.successful_optimizations < 0:
            raise ValueError("Successful optimizations cannot be negative")
        
        if self.current_streak is not None and self.current_streak < 0:
            raise ValueError("Current streak cannot be negative")
        
        if self.level is not None and self.level < 1:
            raise ValueError("Level must be positive")
        
        if self.total_xp is not None and self.total_xp < 0:
            raise ValueError("Total XP cannot be negative")


@dataclass
class GetUserRankingRequest:
    """Request for getting a specific user's ranking and statistics"""
    
    user_id: str
    period: str = "all_time"
    category: Optional[str] = None
    ranking_criteria: str = "default"
    
    def validate(self) -> None:
        """Validate the request parameters"""
        if not self.user_id:
            raise ValueError("User ID is required")
        
        valid_periods = ["daily", "weekly", "monthly", "all_time"]
        if self.period not in valid_periods:
            raise ValueError(f"Period must be one of: {valid_periods}")


@dataclass
class GetSocialComparisonRequest:
    """Request for social comparison data"""
    
    user_id: str
    comparison_type: str  # "friends", "team", "following"
    metric: str  # "success_rate", "total_optimizations", "level", etc.
    period: str = "all_time"
    
    def validate(self) -> None:
        """Validate the request parameters"""
        if not self.user_id:
            raise ValueError("User ID is required")
        
        valid_types = ["friends", "team", "following", "global"]
        if self.comparison_type not in valid_types:
            raise ValueError(f"Comparison type must be one of: {valid_types}")
        
        valid_metrics = ["success_rate", "total_optimizations", "level", "current_streak"]
        if self.metric not in valid_metrics:
            raise ValueError(f"Metric must be one of: {valid_metrics}")


@dataclass
class CreateHistoricalSnapshotRequest:
    """Request for creating a historical leaderboard snapshot"""
    
    period: str
    snapshot_date: str
    category: Optional[str] = None
    
    def validate(self) -> None:
        """Validate the request parameters"""
        valid_periods = ["daily", "weekly", "monthly", "all_time"]
        if self.period not in valid_periods:
            raise ValueError(f"Period must be one of: {valid_periods}")
        
        if not self.snapshot_date:
            raise ValueError("Snapshot date is required")
        
        # Validate date format
        try:
            datetime.fromisoformat(self.snapshot_date.replace('Z', '+00:00'))
        except ValueError:
            raise ValueError("Snapshot date must be in ISO format")


@dataclass
class GetTeamLeaderboardRequest:
    """Request for team-specific leaderboard data"""
    
    team_name: str
    period: str = "all_time"
    limit: int = 10
    ranking_criteria: str = "default"
    
    def validate(self) -> None:
        """Validate the request parameters"""
        if not self.team_name:
            raise ValueError("Team name is required")
        
        valid_periods = ["daily", "weekly", "monthly", "all_time"]
        if self.period not in valid_periods:
            raise ValueError(f"Period must be one of: {valid_periods}")
        
        if self.limit <= 0 or self.limit > 100:
            raise ValueError("Limit must be between 1 and 100")