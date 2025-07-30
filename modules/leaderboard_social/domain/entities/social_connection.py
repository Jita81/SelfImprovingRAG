"""
SocialConnection entity for managing user relationships and social features

This entity represents social connections between users, including friendships,
team memberships, and following relationships.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Any, Optional
import uuid


@dataclass
class SocialConnection:
    """
    Entity representing social connections and relationships between users.
    
    Manages friend networks, team memberships, and social comparison data.
    """
    user_id: str
    friends: List[str]
    following: List[str]
    followers: List[str]
    team_name: Optional[str] = None
    
    # Metadata
    connection_id: str = None
    created_at: datetime = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Initialize entity with generated values if not provided"""
        if self.connection_id is None:
            self.connection_id = str(uuid.uuid4())
        
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        
        # Ensure lists are not None
        if self.friends is None:
            self.friends = []
        if self.following is None:
            self.following = []
        if self.followers is None:
            self.followers = []
    
    def add_friend(self, friend_user_id: str) -> None:
        """Add a mutual friend connection"""
        if friend_user_id not in self.friends:
            self.friends.append(friend_user_id)
            self.updated_at = datetime.utcnow()
    
    def remove_friend(self, friend_user_id: str) -> None:
        """Remove a friend connection"""
        if friend_user_id in self.friends:
            self.friends.remove(friend_user_id)
            self.updated_at = datetime.utcnow()
    
    def follow_user(self, target_user_id: str) -> None:
        """Follow another user"""
        if target_user_id not in self.following:
            self.following.append(target_user_id)
            self.updated_at = datetime.utcnow()
    
    def unfollow_user(self, target_user_id: str) -> None:
        """Unfollow a user"""
        if target_user_id in self.following:
            self.following.remove(target_user_id)
            self.updated_at = datetime.utcnow()
    
    def add_follower(self, follower_user_id: str) -> None:
        """Add a follower"""
        if follower_user_id not in self.followers:
            self.followers.append(follower_user_id)
            self.updated_at = datetime.utcnow()
    
    def remove_follower(self, follower_user_id: str) -> None:
        """Remove a follower"""
        if follower_user_id in self.followers:
            self.followers.remove(follower_user_id)
            self.updated_at = datetime.utcnow()
    
    def set_team(self, team_name: str) -> None:
        """Set the user's team"""
        self.team_name = team_name
        self.updated_at = datetime.utcnow()
    
    def get_friend_count(self) -> int:
        """Get number of friends"""
        return len(self.friends)
    
    def get_following_count(self) -> int:
        """Get number of users being followed"""
        return len(self.following)
    
    def get_follower_count(self) -> int:
        """Get number of followers"""
        return len(self.followers)
    
    def is_friend(self, user_id: str) -> bool:
        """Check if a user is a friend"""
        return user_id in self.friends
    
    def is_following(self, user_id: str) -> bool:
        """Check if following a user"""
        return user_id in self.following
    
    def is_follower(self, user_id: str) -> bool:
        """Check if a user is a follower"""
        return user_id in self.followers
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "connection_id": self.connection_id,
            "user_id": self.user_id,
            "friends": self.friends.copy(),
            "following": self.following.copy(),
            "followers": self.followers.copy(),
            "team_name": self.team_name,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SocialConnection':
        """Create SocialConnection from dictionary data"""
        created_at = None
        if data.get("created_at"):
            created_at = datetime.fromisoformat(data["created_at"].replace('Z', '+00:00'))
        
        updated_at = None
        if data.get("updated_at"):
            updated_at = datetime.fromisoformat(data["updated_at"].replace('Z', '+00:00'))
        
        return cls(
            connection_id=data.get("connection_id"),
            user_id=data["user_id"],
            friends=data.get("friends", []).copy(),
            following=data.get("following", []).copy(),
            followers=data.get("followers", []).copy(),
            team_name=data.get("team_name"),
            created_at=created_at,
            updated_at=updated_at
        )