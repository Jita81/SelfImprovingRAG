from dataclasses import dataclass
from typing import Optional

@dataclass
class CreateUserRequest:
    """Request DTO for creating a new user"""
    email: str
    name: str
    role: str
    team: str
    company: str
    
    def validate(self) -> bool:
        """Validate the request data"""
        return (
            self.email and
            self.name and
            self.role and
            self.team and
            self.company
        )

@dataclass
class GainExperienceRequest:
    """Request DTO for awarding experience points"""
    user_id: str
    points: int
    reason: str
    
    def validate(self) -> bool:
        """Validate the request data"""
        return (
            self.user_id and
            self.points >= 0 and
            self.reason
        )

@dataclass
class UpdateProfileRequest:
    """Request DTO for updating user profile"""
    user_id: str
    name: Optional[str] = None
    role: Optional[str] = None
    team: Optional[str] = None
    
    def validate(self) -> bool:
        """Validate the request data"""
        return bool(self.user_id)

@dataclass
class TrackOptimizationRequest:
    """Request DTO for tracking optimization results"""
    user_id: str
    success: bool
    duration_seconds: Optional[float] = None
    tokens_used: Optional[int] = None
    
    def validate(self) -> bool:
        """Validate the request data"""
        return bool(self.user_id)