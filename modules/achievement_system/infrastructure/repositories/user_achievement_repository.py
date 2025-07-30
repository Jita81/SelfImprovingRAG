from abc import ABC, abstractmethod
from typing import Optional, List, Dict
from datetime import datetime
import json
from pathlib import Path

from ...domain.entities.user_achievement import UserAchievement

class UserAchievementRepository(ABC):
    """Abstract repository interface for user achievement persistence"""
    
    @abstractmethod
    def save_user_achievement(self, user_achievement: UserAchievement) -> UserAchievement:
        """Save a user achievement"""
        pass
    
    @abstractmethod
    def get_user_achievements(self, user_id: str) -> List[UserAchievement]:
        """Get all achievements for a specific user"""
        pass
    
    @abstractmethod
    def get_user_achievement(self, user_id: str, achievement_id: str) -> Optional[UserAchievement]:
        """Get a specific user achievement"""
        pass
    
    @abstractmethod
    def delete_user_achievement(self, user_id: str, achievement_id: str) -> bool:
        """Delete a user achievement"""
        pass
    
    @abstractmethod
    def get_achievement_holders(self, achievement_id: str) -> List[UserAchievement]:
        """Get all users who have unlocked a specific achievement"""
        pass

class InMemoryUserAchievementRepository(UserAchievementRepository):
    """
    In-memory implementation of UserAchievementRepository for testing and development.
    """
    
    def __init__(self):
        self._user_achievements: Dict[str, List[UserAchievement]] = {}
        self._load_test_data()
    
    def save_user_achievement(self, user_achievement: UserAchievement) -> UserAchievement:
        """Save a user achievement"""
        user_id = user_achievement.user_id
        
        if user_id not in self._user_achievements:
            self._user_achievements[user_id] = []
        
        # Remove existing achievement if it exists (shouldn't happen in normal flow)
        self._user_achievements[user_id] = [
            ua for ua in self._user_achievements[user_id] 
            if ua.achievement_id != user_achievement.achievement_id
        ]
        
        # Add the new achievement
        self._user_achievements[user_id].append(user_achievement)
        
        return user_achievement
    
    def get_user_achievements(self, user_id: str) -> List[UserAchievement]:
        """Get all achievements for a specific user"""
        return self._user_achievements.get(user_id, [])
    
    def get_user_achievement(self, user_id: str, achievement_id: str) -> Optional[UserAchievement]:
        """Get a specific user achievement"""
        user_achievements = self._user_achievements.get(user_id, [])
        for ua in user_achievements:
            if ua.achievement_id == achievement_id:
                return ua
        return None
    
    def delete_user_achievement(self, user_id: str, achievement_id: str) -> bool:
        """Delete a user achievement"""
        if user_id not in self._user_achievements:
            return False
        
        original_count = len(self._user_achievements[user_id])
        self._user_achievements[user_id] = [
            ua for ua in self._user_achievements[user_id] 
            if ua.achievement_id != achievement_id
        ]
        
        return len(self._user_achievements[user_id]) < original_count
    
    def get_achievement_holders(self, achievement_id: str) -> List[UserAchievement]:
        """Get all users who have unlocked a specific achievement"""
        holders = []
        for user_achievements in self._user_achievements.values():
            for ua in user_achievements:
                if ua.achievement_id == achievement_id:
                    holders.append(ua)
        return holders
    
    def _load_test_data(self):
        """Load test user achievements from test data file"""
        try:
            test_data_path = Path(__file__).parent.parent.parent.parent.parent / "tests" / "test_data" / "achievement_test_data.json"
            with open(test_data_path, 'r') as f:
                data = json.load(f)
            
            for user_achievement_data in data.get("user_achievements", []):
                user_id = user_achievement_data["user_id"]
                
                for unlocked_achievement in user_achievement_data.get("unlocked_achievements", []):
                    user_achievement = UserAchievement(
                        user_id=user_id,
                        achievement_id=unlocked_achievement["achievement_id"],
                        unlocked_at=datetime.fromisoformat(unlocked_achievement["unlocked_at"].replace('Z', '+00:00')),
                        xp_awarded=unlocked_achievement["xp_awarded"]
                    )
                    
                    if user_id not in self._user_achievements:
                        self._user_achievements[user_id] = []
                    
                    self._user_achievements[user_id].append(user_achievement)
                
        except Exception as e:
            # If test data loading fails, continue with empty repository
            print(f"Warning: Could not load user achievement test data: {e}")
            pass

class FileUserAchievementRepository(UserAchievementRepository):
    """
    File-based implementation of UserAchievementRepository for persistence.
    """
    
    def __init__(self, file_path: str = "data/user_achievements.json"):
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self._user_achievements: Dict[str, List[UserAchievement]] = {}
        self._load_from_file()
    
    def save_user_achievement(self, user_achievement: UserAchievement) -> UserAchievement:
        """Save a user achievement"""
        user_id = user_achievement.user_id
        
        if user_id not in self._user_achievements:
            self._user_achievements[user_id] = []
        
        # Remove existing achievement if it exists
        self._user_achievements[user_id] = [
            ua for ua in self._user_achievements[user_id] 
            if ua.achievement_id != user_achievement.achievement_id
        ]
        
        # Add the new achievement
        self._user_achievements[user_id].append(user_achievement)
        
        self._save_to_file()
        return user_achievement
    
    def get_user_achievements(self, user_id: str) -> List[UserAchievement]:
        """Get all achievements for a specific user"""
        return self._user_achievements.get(user_id, [])
    
    def get_user_achievement(self, user_id: str, achievement_id: str) -> Optional[UserAchievement]:
        """Get a specific user achievement"""
        user_achievements = self._user_achievements.get(user_id, [])
        for ua in user_achievements:
            if ua.achievement_id == achievement_id:
                return ua
        return None
    
    def delete_user_achievement(self, user_id: str, achievement_id: str) -> bool:
        """Delete a user achievement"""
        if user_id not in self._user_achievements:
            return False
        
        original_count = len(self._user_achievements[user_id])
        self._user_achievements[user_id] = [
            ua for ua in self._user_achievements[user_id] 
            if ua.achievement_id != achievement_id
        ]
        
        changed = len(self._user_achievements[user_id]) < original_count
        if changed:
            self._save_to_file()
        
        return changed
    
    def get_achievement_holders(self, achievement_id: str) -> List[UserAchievement]:
        """Get all users who have unlocked a specific achievement"""
        holders = []
        for user_achievements in self._user_achievements.values():
            for ua in user_achievements:
                if ua.achievement_id == achievement_id:
                    holders.append(ua)
        return holders
    
    def _save_to_file(self):
        """Save user achievements to JSON file"""
        try:
            user_achievements_data = {}
            for user_id, achievements in self._user_achievements.items():
                user_achievements_data[user_id] = [ua.to_dict() for ua in achievements]
            
            with open(self.file_path, 'w') as f:
                json.dump({"user_achievements": user_achievements_data}, f, indent=2)
                
        except Exception as e:
            print(f"Error saving user achievements to file: {e}")
    
    def _load_from_file(self):
        """Load user achievements from JSON file"""
        try:
            if self.file_path.exists():
                with open(self.file_path, 'r') as f:
                    data = json.load(f)
                
                for user_id, achievements_data in data.get("user_achievements", {}).items():
                    self._user_achievements[user_id] = []
                    for achievement_data in achievements_data:
                        user_achievement = UserAchievement.from_dict(achievement_data)
                        self._user_achievements[user_id].append(user_achievement)
                    
        except Exception as e:
            print(f"Error loading user achievements from file: {e}")
            # Continue with empty repository