from dataclasses import dataclass
from typing import Optional
import re

@dataclass(frozen=True)
class UserProfile:
    """
    Value object representing user profile information.
    Immutable to ensure data integrity.
    """
    email: str
    name: str
    role: str
    team: str
    company: str
    
    def __post_init__(self):
        """Validate the user profile data"""
        if not self._is_valid_email(self.email):
            raise ValueError(f"Invalid email format: {self.email}")
        
        if not self.name or len(self.name.strip()) == 0:
            raise ValueError("Name cannot be empty")
        
        if not self.role or len(self.role.strip()) == 0:
            raise ValueError("Role cannot be empty")
    
    def _is_valid_email(self, email: str) -> bool:
        """Validate email format using regex"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @property
    def display_name(self) -> str:
        """Return formatted display name"""
        return f"{self.name} ({self.role})"
    
    def is_same_company(self, other_profile: 'UserProfile') -> bool:
        """Check if two profiles belong to same company"""
        return self.company == other_profile.company
    
    def is_same_team(self, other_profile: 'UserProfile') -> bool:
        """Check if two profiles belong to same team"""
        return self.company == other_profile.company and self.team == other_profile.team