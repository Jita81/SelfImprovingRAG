from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass
class CheckAchievementUnlockRequest:
    """Request DTO for checking if achievements should be unlocked"""
    user_id: str
    event_type: str
    event_data: Dict[str, Any]
    
    def validate(self) -> bool:
        """Validate the request data"""
        return (
            self.user_id and
            self.event_type and
            isinstance(self.event_data, dict)
        )

@dataclass
class GetUserAchievementsRequest:
    """Request DTO for getting user's achievements"""
    user_id: str
    include_locked: bool = True
    category_filter: Optional[str] = None
    
    def validate(self) -> bool:
        """Validate the request data"""
        return bool(self.user_id)

@dataclass
class GetAchievementProgressRequest:
    """Request DTO for getting achievement progress"""
    user_id: str
    achievement_id: Optional[str] = None  # If None, get progress for all achievements
    
    def validate(self) -> bool:
        """Validate the request data"""
        return bool(self.user_id)

@dataclass
class AwardAchievementRequest:
    """Request DTO for manually awarding an achievement (admin use)"""
    user_id: str
    achievement_id: str
    reason: str
    override_unlock_check: bool = False
    
    def validate(self) -> bool:
        """Validate the request data"""
        return (
            self.user_id and
            self.achievement_id and
            self.reason
        )