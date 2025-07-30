from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional
import uuid

from ..value_objects.user_profile import UserProfile
from ..value_objects.gamification_stats import GamificationStats

@dataclass
class User:
    """
    User entity representing a platform user with profile and gamification data.
    This is the main aggregate root for user-related operations.
    """
    id: str
    profile: UserProfile
    gamification: GamificationStats
    created_at: Optional[datetime] = None
    last_active: Optional[datetime] = None
    
    def __post_init__(self):
        """Initialize timestamps if not provided"""
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)
        
        if self.last_active is None:
            self.last_active = datetime.now(timezone.utc)
    
    @classmethod
    def create_new_user(cls, profile: UserProfile) -> 'User':
        """
        Factory method to create a new user with initial gamification stats.
        This ensures proper initialization of all required fields.
        """
        initial_gamification = GamificationStats(
            level=1,
            experience_points=0,
            total_optimizations=0,
            successful_optimizations=0,
            win_streak=0
        )
        
        return cls(
            id=str(uuid.uuid4()),
            profile=profile,
            gamification=initial_gamification
        )
    
    def gain_experience(self, points: int, reason: str) -> dict:
        """
        Award experience points to the user and handle level ups.
        
        Args:
            points: Experience points to award
            reason: Reason for awarding XP (for logging/tracking)
        
        Returns:
            Dictionary with level up information
        """
        self.last_active = datetime.now(timezone.utc)
        return self.gamification.gain_experience(points)
    
    def track_optimization_result(self, success: bool) -> dict:
        """
        Track the result of an optimization attempt.
        
        Args:
            success: Whether the optimization was successful
        
        Returns:
            Dictionary with updated stats
        """
        self.last_active = datetime.now(timezone.utc)
        return self.gamification.track_optimization(success)
    
    def update_last_active(self) -> None:
        """Update the last active timestamp"""
        self.last_active = datetime.now(timezone.utc)
    
    @property
    def is_active_user(self) -> bool:
        """Check if user has been active recently (within 7 days)"""
        if not self.last_active:
            return False
        
        days_since_active = (datetime.now(timezone.utc) - self.last_active).days
        return days_since_active <= 7
    
    @property
    def experience_level_info(self) -> dict:
        """Get comprehensive level and experience information"""
        return {
            "level": self.gamification.level,
            "experience_points": self.gamification.experience_points,
            "current_level_xp": self.gamification.current_level_xp,
            "next_level_xp": self.gamification.next_level_xp,
            "xp_until_next": self.gamification.xp_until_next_level,
            "level_title": self.gamification.current_level_title,
            "success_rate": self.gamification.success_rate
        }
    
    def can_access_feature(self, feature_name: str) -> bool:
        """
        Check if user's level grants access to a specific feature.
        This implements the benefit system from the level configuration.
        """
        level_system = self.gamification._get_level_system()
        
        # Find current level benefits
        for level_info in level_system["levels"]:
            if level_info["level"] == self.gamification.level:
                benefits = level_info.get("benefits", [])
                
                # Check if feature is in benefits or if user has "All features"
                return (feature_name in benefits or 
                       "All features" in benefits or
                       any("All" in benefit for benefit in benefits))
        
        return False
    
    def __str__(self) -> str:
        """String representation of user"""
        return f"User({self.profile.name}, Level {self.gamification.level}, {self.gamification.experience_points} XP)"