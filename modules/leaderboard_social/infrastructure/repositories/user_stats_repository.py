"""
User Stats Repository for social connections and team data

Abstract repository interface and in-memory implementation for
user social connections and team memberships.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import json
import os

try:
    from ...domain.entities.social_connection import SocialConnection
except ImportError:
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    from domain.entities.social_connection import SocialConnection


class UserStatsRepository(ABC):
    """Abstract repository interface for user stats and social data"""
    
    @abstractmethod
    def get_user_social_data(self, user_id: str) -> Optional[SocialConnection]:
        """Get social connections for a user"""
        pass
    
    @abstractmethod
    def save_user_social_data(self, connection: SocialConnection) -> SocialConnection:
        """Save user social connections"""
        pass
    
    @abstractmethod
    def get_team_members(self, team_name: str) -> List[str]:
        """Get team member IDs"""
        pass


class InMemoryUserStatsRepository(UserStatsRepository):
    """In-memory implementation for testing"""
    
    def __init__(self):
        self._social_connections: Dict[str, SocialConnection] = {}
        self._team_memberships: Dict[str, List[str]] = {}
        self._load_test_data()
    
    def _load_test_data(self) -> None:
        """Load test data from JSON file"""
        try:
            test_data_path = os.path.join(os.path.dirname(__file__), '../../../../tests/test_data/leaderboard_test_data.json')
            
            if os.path.exists(test_data_path):
                with open(test_data_path, 'r') as f:
                    data = json.load(f)
                
                # Load social connections
                for connection_data in data.get('social_features', {}).get('friend_connections', []):
                    connection = SocialConnection.from_dict(connection_data)
                    self._social_connections[connection.user_id] = connection
                
                # Load team memberships
                for team_data in data.get('social_features', {}).get('team_leaderboards', []):
                    team_name = team_data['team_name']
                    members = team_data['members']
                    self._team_memberships[team_name] = members
                    
        except Exception as e:
            print(f"Warning: Could not load social test data: {e}")
    
    def get_user_social_data(self, user_id: str) -> Optional[SocialConnection]:
        """Get social connections for a user"""
        return self._social_connections.get(user_id)
    
    def save_user_social_data(self, connection: SocialConnection) -> SocialConnection:
        """Save user social connections"""
        self._social_connections[connection.user_id] = connection
        return connection
    
    def get_team_members(self, team_name: str) -> List[str]:
        """Get team member IDs"""
        return self._team_memberships.get(team_name, [])