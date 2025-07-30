from dataclasses import dataclass
from typing import Dict, Any
from ..value_objects.achievement_rarity import AchievementRarity
from ..value_objects.achievement_trigger import AchievementTrigger

@dataclass
class Achievement:
    """
    Achievement entity representing a specific achievement that can be unlocked.
    This is the aggregate root for achievement-related operations.
    """
    id: str
    name: str
    description: str
    rarity: AchievementRarity
    icon: str
    xp_reward: int
    trigger: AchievementTrigger
    category: str
    
    def __post_init__(self):
        """Validate achievement data"""
        if not self.id:
            raise ValueError("Achievement ID cannot be empty")
        
        if not self.name:
            raise ValueError("Achievement name cannot be empty")
        
        if not self.description:
            raise ValueError("Achievement description cannot be empty")
        
        if self.xp_reward < 0:
            raise ValueError("XP reward cannot be negative")
        
        if not self.category:
            raise ValueError("Achievement category cannot be empty")
    
    def check_unlock_conditions(self, event_data: Dict[str, Any]) -> bool:
        """
        Check if the provided event data satisfies this achievement's unlock conditions.
        
        Args:
            event_data: Dictionary containing event-specific data
            
        Returns:
            True if achievement should be unlocked, False otherwise
        """
        return self.trigger.check_trigger(event_data)
    
    def calculate_progress(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate progress toward unlocking this achievement.
        
        Args:
            event_data: Dictionary containing event-specific data
            
        Returns:
            Dictionary with progress information
        """
        progress = self.trigger.calculate_progress(event_data)
        progress["achievement_id"] = self.id
        return progress
    
    def calculate_final_xp_reward(self) -> int:
        """
        Calculate the final XP reward including rarity multiplier.
        
        Returns:
            Final XP amount after applying rarity multiplier
        """
        return self.rarity.calculate_xp_reward(self.xp_reward)
    
    @property
    def is_rare(self) -> bool:
        """Check if this achievement is considered rare"""
        return self.rarity.is_rare()
    
    @property
    def display_info(self) -> Dict[str, Any]:
        """Get display information for UI"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "rarity": self.rarity.value,
            "rarity_color": self.rarity.color,
            "icon": self.icon,
            "xp_reward": self.xp_reward,
            "final_xp_reward": self.calculate_final_xp_reward(),
            "category": self.category,
            "trigger_description": self.trigger.description,
            "is_rare": self.is_rare
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert achievement to dictionary for serialization"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "rarity": self.rarity.value,
            "icon": self.icon,
            "xp_reward": self.xp_reward,
            "category": self.category,
            "trigger": {
                "trigger_type": self.trigger.trigger_type,
                "threshold": self.trigger.threshold,
                "minimum_attempts": self.trigger.minimum_attempts,
                "count": self.trigger.count,
                "quality_threshold": self.trigger.quality_threshold
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Achievement':
        """Create Achievement from dictionary data"""
        trigger_data = data["trigger"]
        trigger = AchievementTrigger(
            trigger_type=trigger_data["trigger_type"],
            threshold=trigger_data["threshold"],
            minimum_attempts=trigger_data.get("minimum_attempts"),
            count=trigger_data.get("count"),
            quality_threshold=trigger_data.get("quality_threshold")
        )
        
        return cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            rarity=AchievementRarity.from_string(data["rarity"]),
            icon=data["icon"],
            xp_reward=data["xp_reward"],
            trigger=trigger,
            category=data["category"]
        )
    
    def __str__(self) -> str:
        """String representation of achievement"""
        return f"Achievement({self.name}, {self.rarity.value}, {self.xp_reward} XP)"
    
    def __eq__(self, other) -> bool:
        """Check equality based on achievement ID"""
        if not isinstance(other, Achievement):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        """Hash based on achievement ID"""
        return hash(self.id)