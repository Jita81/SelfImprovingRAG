from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from ...domain.entities.achievement import Achievement
from ...domain.entities.user_achievement import UserAchievement

@dataclass
class BaseResponse:
    """Base response class with success/error handling"""
    success: bool
    error_message: Optional[str] = None
    
    @classmethod
    def success_response(cls, **kwargs):
        """Create a successful response"""
        return cls(success=True, **kwargs)
    
    @classmethod
    def error_response(cls, message: str, **kwargs):
        """Create an error response"""
        return cls(success=False, error_message=message, **kwargs)

@dataclass
class CheckAchievementUnlockResponse(BaseResponse):
    """Response for achievement unlock check"""
    unlocked_achievements: List[Achievement] = None
    total_xp_awarded: int = 0
    progress_updates: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.unlocked_achievements is None:
            self.unlocked_achievements = []
        if self.progress_updates is None:
            self.progress_updates = []

@dataclass
class GetUserAchievementsResponse(BaseResponse):
    """Response for getting user achievements"""
    unlocked_achievements: List[Achievement] = None
    locked_achievements: List[Achievement] = None
    unlocked_count: int = 0
    total_achievements: int = 0
    completion_percentage: float = 0.0
    total_xp_from_achievements: int = 0
    rare_achievements_count: int = 0
    recent_achievements: List[UserAchievement] = None
    achievement_progress: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.unlocked_achievements is None:
            self.unlocked_achievements = []
        if self.locked_achievements is None:
            self.locked_achievements = []
        if self.recent_achievements is None:
            self.recent_achievements = []
        if self.achievement_progress is None:
            self.achievement_progress = []

@dataclass
class GetAchievementProgressResponse(BaseResponse):
    """Response for getting achievement progress"""
    achievement_progress: List[Dict[str, Any]] = None
    overall_completion_percentage: float = 0.0
    achievements_near_completion: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.achievement_progress is None:
            self.achievement_progress = []
        if self.achievements_near_completion is None:
            self.achievements_near_completion = []

@dataclass
class AwardAchievementResponse(BaseResponse):
    """Response for awarding an achievement"""
    achievement: Optional[Achievement] = None
    user_achievement: Optional[UserAchievement] = None
    xp_awarded: int = 0

@dataclass
class AchievementStatsResponse(BaseResponse):
    """Response for achievement statistics"""
    total_achievements: int = 0
    unlocked_achievements: int = 0
    completion_percentage: float = 0.0
    total_xp_earned: int = 0
    rare_achievements_unlocked: int = 0
    categories_completed: List[str] = None
    longest_unlock_streak: int = 0
    most_recent_achievement: Optional[UserAchievement] = None
    
    def __post_init__(self):
        if self.categories_completed is None:
            self.categories_completed = []