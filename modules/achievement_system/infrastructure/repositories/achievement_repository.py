from abc import ABC, abstractmethod
from typing import Optional, List, Dict
import json
from pathlib import Path

from ...domain.entities.achievement import Achievement
from ...domain.value_objects.achievement_rarity import AchievementRarity
from ...domain.value_objects.achievement_trigger import AchievementTrigger

class AchievementRepository(ABC):
    """Abstract repository interface for achievement persistence"""
    
    @abstractmethod
    def get_all(self) -> List[Achievement]:
        """Get all achievements"""
        pass
    
    @abstractmethod
    def get_by_id(self, achievement_id: str) -> Optional[Achievement]:
        """Get an achievement by ID"""
        pass
    
    @abstractmethod
    def get_by_category(self, category: str) -> List[Achievement]:
        """Get achievements by category"""
        pass
    
    @abstractmethod
    def save(self, achievement: Achievement) -> Achievement:
        """Save an achievement"""
        pass
    
    @abstractmethod
    def delete(self, achievement_id: str) -> bool:
        """Delete an achievement by ID"""
        pass

class InMemoryAchievementRepository(AchievementRepository):
    """
    In-memory implementation of AchievementRepository for testing and development.
    """
    
    def __init__(self):
        self._achievements: Dict[str, Achievement] = {}
        self._load_test_data()
    
    def get_all(self) -> List[Achievement]:
        """Get all achievements"""
        return list(self._achievements.values())
    
    def get_by_id(self, achievement_id: str) -> Optional[Achievement]:
        """Get an achievement by ID"""
        return self._achievements.get(achievement_id)
    
    def get_by_category(self, category: str) -> List[Achievement]:
        """Get achievements by category"""
        return [ach for ach in self._achievements.values() if ach.category == category]
    
    def save(self, achievement: Achievement) -> Achievement:
        """Save an achievement"""
        self._achievements[achievement.id] = achievement
        return achievement
    
    def delete(self, achievement_id: str) -> bool:
        """Delete an achievement by ID"""
        if achievement_id in self._achievements:
            del self._achievements[achievement_id]
            return True
        return False
    
    def _load_test_data(self):
        """Load test achievements from test data file"""
        try:
            test_data_path = Path(__file__).parent.parent.parent.parent.parent / "tests" / "test_data" / "achievement_test_data.json"
            with open(test_data_path, 'r') as f:
                data = json.load(f)
            
            for achievement_data in data.get("achievements", []):
                # Create achievement trigger
                trigger_data = achievement_data["trigger"]
                trigger = AchievementTrigger(
                    trigger_type=trigger_data["type"],
                    threshold=trigger_data["threshold"],
                    minimum_attempts=trigger_data.get("minimum_attempts"),
                    count=trigger_data.get("count"),
                    quality_threshold=trigger_data.get("quality_threshold")
                )
                
                # Create achievement
                achievement = Achievement(
                    id=achievement_data["id"],
                    name=achievement_data["name"],
                    description=achievement_data["description"],
                    rarity=AchievementRarity.from_string(achievement_data["rarity"]),
                    icon=achievement_data["icon"],
                    xp_reward=achievement_data["xp_reward"],
                    trigger=trigger,
                    category=achievement_data["category"]
                )
                
                self._achievements[achievement.id] = achievement
                
        except Exception as e:
            # If test data loading fails, continue with empty repository
            print(f"Warning: Could not load achievement test data: {e}")
            pass

class FileAchievementRepository(AchievementRepository):
    """
    File-based implementation of AchievementRepository for persistence.
    """
    
    def __init__(self, file_path: str = "data/achievements.json"):
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self._achievements: Dict[str, Achievement] = {}
        self._load_from_file()
    
    def get_all(self) -> List[Achievement]:
        """Get all achievements"""
        return list(self._achievements.values())
    
    def get_by_id(self, achievement_id: str) -> Optional[Achievement]:
        """Get an achievement by ID"""
        return self._achievements.get(achievement_id)
    
    def get_by_category(self, category: str) -> List[Achievement]:
        """Get achievements by category"""
        return [ach for ach in self._achievements.values() if ach.category == category]
    
    def save(self, achievement: Achievement) -> Achievement:
        """Save an achievement"""
        self._achievements[achievement.id] = achievement
        self._save_to_file()
        return achievement
    
    def delete(self, achievement_id: str) -> bool:
        """Delete an achievement by ID"""
        if achievement_id in self._achievements:
            del self._achievements[achievement_id]
            self._save_to_file()
            return True
        return False
    
    def _save_to_file(self):
        """Save achievements to JSON file"""
        try:
            achievements_data = []
            for achievement in self._achievements.values():
                achievement_dict = achievement.to_dict()
                achievements_data.append(achievement_dict)
            
            with open(self.file_path, 'w') as f:
                json.dump({"achievements": achievements_data}, f, indent=2)
                
        except Exception as e:
            print(f"Error saving achievements to file: {e}")
    
    def _load_from_file(self):
        """Load achievements from JSON file"""
        try:
            if self.file_path.exists():
                with open(self.file_path, 'r') as f:
                    data = json.load(f)
                
                for achievement_data in data.get("achievements", []):
                    achievement = Achievement.from_dict(achievement_data)
                    self._achievements[achievement.id] = achievement
                    
        except Exception as e:
            print(f"Error loading achievements from file: {e}")
            # Continue with empty repository