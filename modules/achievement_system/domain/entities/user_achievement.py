from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional, Dict, Any

@dataclass
class UserAchievement:
    """
    UserAchievement entity representing an achievement unlocked by a specific user.
    Links users to their unlocked achievements with timestamps and XP records.
    """
    user_id: str
    achievement_id: str
    unlocked_at: datetime
    xp_awarded: int
    
    def __post_init__(self):
        """Validate user achievement data"""
        if not self.user_id:
            raise ValueError("User ID cannot be empty")
        
        if not self.achievement_id:
            raise ValueError("Achievement ID cannot be empty")
        
        if self.xp_awarded < 0:
            raise ValueError("XP awarded cannot be negative")
        
        if not self.unlocked_at:
            self.unlocked_at = datetime.now(timezone.utc)
    
    @classmethod
    def create_new(cls, user_id: str, achievement_id: str, xp_awarded: int) -> 'UserAchievement':
        """
        Factory method to create a new user achievement with current timestamp.
        
        Args:
            user_id: ID of the user who unlocked the achievement
            achievement_id: ID of the achievement that was unlocked
            xp_awarded: Amount of XP awarded for this achievement
            
        Returns:
            New UserAchievement instance
        """
        return cls(
            user_id=user_id,
            achievement_id=achievement_id,
            unlocked_at=datetime.now(timezone.utc),
            xp_awarded=xp_awarded
        )
    
    @property
    def days_since_unlock(self) -> int:
        """Get number of days since this achievement was unlocked"""
        now = datetime.now(timezone.utc)
        delta = now - self.unlocked_at
        return delta.days
    
    @property
    def is_recent(self) -> bool:
        """Check if this achievement was unlocked recently (within 7 days)"""
        return self.days_since_unlock <= 7
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user achievement to dictionary for serialization"""
        return {
            "user_id": self.user_id,
            "achievement_id": self.achievement_id,
            "unlocked_at": self.unlocked_at.isoformat(),
            "xp_awarded": self.xp_awarded,
            "days_since_unlock": self.days_since_unlock,
            "is_recent": self.is_recent
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserAchievement':
        """Create UserAchievement from dictionary data"""
        unlocked_at = data["unlocked_at"]
        if isinstance(unlocked_at, str):
            unlocked_at = datetime.fromisoformat(unlocked_at.replace('Z', '+00:00'))
        
        return cls(
            user_id=data["user_id"],
            achievement_id=data["achievement_id"],
            unlocked_at=unlocked_at,
            xp_awarded=data["xp_awarded"]
        )
    
    def __str__(self) -> str:
        """String representation of user achievement"""
        return f"UserAchievement({self.user_id}, {self.achievement_id}, {self.xp_awarded} XP)"
    
    def __eq__(self, other) -> bool:
        """Check equality based on user ID and achievement ID"""
        if not isinstance(other, UserAchievement):
            return False
        return (self.user_id == other.user_id and 
                self.achievement_id == other.achievement_id)
    
    def __hash__(self) -> int:
        """Hash based on user ID and achievement ID"""
        return hash((self.user_id, self.achievement_id))