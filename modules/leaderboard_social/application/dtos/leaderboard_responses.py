"""
Response DTOs for Leaderboard Service

Data transfer objects for handling leaderboard service responses
with consistent structure and type safety.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime


@dataclass
class BaseResponse:
    """Base response class for all leaderboard operations"""
    success: bool
    error: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class GetLeaderboardResponse(BaseResponse):
    """Response for leaderboard retrieval requests"""
    leaderboard_entries: List[Dict[str, Any]] = field(default_factory=list)
    period: Optional[str] = None
    category: Optional[str] = None
    team_name: Optional[str] = None
    total_participants: int = 0
    ranking_criteria: Optional[str] = None
    team_statistics: Optional[Dict[str, Any]] = None
    
    # For weekly/daily specific properties  
    weekly_success_rate: Optional[float] = None
    optimizations_today: Optional[int] = None
    daily_success_rate: Optional[float] = None


@dataclass
class UpdateUserStatsResponse(BaseResponse):
    """Response for user statistics update requests"""
    user_id: Optional[str] = None
    new_rank: Optional[int] = None
    previous_rank: Optional[int] = None
    new_streak: Optional[int] = None
    rank_change: Optional[int] = None


@dataclass
class GetUserRankingResponse(BaseResponse):
    """Response for user ranking requests"""
    user_id: Optional[str] = None
    rank: Optional[int] = None
    composite_score: Optional[float] = None
    score_breakdown: Optional[Dict[str, float]] = None
    period: Optional[str] = None
    category: Optional[str] = None


@dataclass 
class GetSocialComparisonResponse(BaseResponse):
    """Response for social comparison requests"""
    user_id: Optional[str] = None
    comparison_type: Optional[str] = None
    metric: Optional[str] = None
    comparison_data: Optional[Dict[str, Any]] = None


@dataclass
class CreateHistoricalSnapshotResponse(BaseResponse):
    """Response for historical snapshot creation"""
    snapshot_id: Optional[str] = None
    period: Optional[str] = None
    snapshot_date: Optional[str] = None
    participants_count: Optional[int] = None