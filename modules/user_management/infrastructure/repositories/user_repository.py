from abc import ABC, abstractmethod
from typing import Optional, List, Dict
from datetime import datetime
import json
from pathlib import Path

from ...domain.entities.user import User
from ...domain.value_objects.user_profile import UserProfile
from ...domain.value_objects.gamification_stats import GamificationStats

class UserRepository(ABC):
    """Abstract repository interface for user persistence"""
    
    @abstractmethod
    def save(self, user: User) -> User:
        """Save a user and return the saved instance"""
        pass
    
    @abstractmethod
    def get_by_id(self, user_id: str) -> Optional[User]:
        """Get a user by ID"""
        pass
    
    @abstractmethod
    def get_by_email(self, email: str) -> Optional[User]:
        """Get a user by email"""
        pass
    
    @abstractmethod
    def get_all(self) -> List[User]:
        """Get all users"""
        pass
    
    @abstractmethod
    def delete(self, user_id: str) -> bool:
        """Delete a user by ID"""
        pass

class InMemoryUserRepository(UserRepository):
    """
    In-memory implementation of UserRepository for testing and development.
    """
    
    def __init__(self):
        self._users: Dict[str, User] = {}
        self._load_test_data()
    
    def save(self, user: User) -> User:
        """Save a user to memory"""
        self._users[user.id] = user
        return user
    
    def get_by_id(self, user_id: str) -> Optional[User]:
        """Get a user by ID"""
        return self._users.get(user_id)
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Get a user by email"""
        for user in self._users.values():
            if user.profile.email == email:
                return user
        return None
    
    def get_all(self) -> List[User]:
        """Get all users"""
        return list(self._users.values())
    
    def delete(self, user_id: str) -> bool:
        """Delete a user by ID"""
        if user_id in self._users:
            del self._users[user_id]
            return True
        return False
    
    def _load_test_data(self):
        """Load test users from test data file"""
        try:
            test_data_path = Path(__file__).parent.parent.parent.parent.parent / "tests" / "test_data" / "gamification_test_data.json"
            with open(test_data_path, 'r') as f:
                data = json.load(f)
            
            for user_data in data.get("users", []):
                # Create user profile
                profile = UserProfile(**user_data["profile"])
                
                # Create gamification stats
                gamification = GamificationStats(**user_data["gamification"])
                
                # Create user
                user = User(
                    id=user_data["id"],
                    profile=profile,
                    gamification=gamification,
                    created_at=datetime.fromisoformat(user_data["created_at"].replace('Z', '+00:00')),
                    last_active=datetime.fromisoformat(user_data["last_active"].replace('Z', '+00:00'))
                )
                
                self._users[user.id] = user
                
        except Exception as e:
            # If test data loading fails, continue with empty repository
            print(f"Warning: Could not load test data: {e}")
            pass

class FileUserRepository(UserRepository):
    """
    File-based implementation of UserRepository for persistence.
    """
    
    def __init__(self, file_path: str = "data/users.json"):
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self._users: Dict[str, User] = {}
        self._load_from_file()
    
    def save(self, user: User) -> User:
        """Save a user to file"""
        self._users[user.id] = user
        self._save_to_file()
        return user
    
    def get_by_id(self, user_id: str) -> Optional[User]:
        """Get a user by ID"""
        return self._users.get(user_id)
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Get a user by email"""
        for user in self._users.values():
            if user.profile.email == email:
                return user
        return None
    
    def get_all(self) -> List[User]:
        """Get all users"""
        return list(self._users.values())
    
    def delete(self, user_id: str) -> bool:
        """Delete a user by ID"""
        if user_id in self._users:
            del self._users[user_id]
            self._save_to_file()
            return True
        return False
    
    def _save_to_file(self):
        """Save users to JSON file"""
        try:
            users_data = []
            for user in self._users.values():
                user_dict = {
                    "id": user.id,
                    "profile": {
                        "email": user.profile.email,
                        "name": user.profile.name,
                        "role": user.profile.role,
                        "team": user.profile.team,
                        "company": user.profile.company
                    },
                    "gamification": {
                        "level": user.gamification.level,
                        "experience_points": user.gamification.experience_points,
                        "total_optimizations": user.gamification.total_optimizations,
                        "successful_optimizations": user.gamification.successful_optimizations,
                        "win_streak": user.gamification.win_streak
                    },
                    "created_at": user.created_at.isoformat() if user.created_at else None,
                    "last_active": user.last_active.isoformat() if user.last_active else None
                }
                users_data.append(user_dict)
            
            with open(self.file_path, 'w') as f:
                json.dump({"users": users_data}, f, indent=2)
                
        except Exception as e:
            print(f"Error saving users to file: {e}")
    
    def _load_from_file(self):
        """Load users from JSON file"""
        try:
            if self.file_path.exists():
                with open(self.file_path, 'r') as f:
                    data = json.load(f)
                
                for user_data in data.get("users", []):
                    # Create user profile
                    profile = UserProfile(**user_data["profile"])
                    
                    # Create gamification stats  
                    gamification = GamificationStats(**user_data["gamification"])
                    
                    # Create user
                    user = User(
                        id=user_data["id"],
                        profile=profile,
                        gamification=gamification,
                        created_at=datetime.fromisoformat(user_data["created_at"]) if user_data.get("created_at") else None,
                        last_active=datetime.fromisoformat(user_data["last_active"]) if user_data.get("last_active") else None
                    )
                    
                    self._users[user.id] = user
                    
        except Exception as e:
            print(f"Error loading users from file: {e}")
            # Continue with empty repository