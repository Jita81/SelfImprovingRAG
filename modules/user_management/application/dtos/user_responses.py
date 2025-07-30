from dataclasses import dataclass
from typing import Optional, Dict, Any
from ...domain.entities.user import User

@dataclass
class BaseResponse:
    """Base response class with success/error handling"""
    success: bool
    error_message: Optional[str] = None
    
    @classmethod
    def success_response(cls, **kwargs):
        """Create a successful response"""
        return cls(success=True, **kwargs)
    
    @classmethod
    def error_response(cls, message: str, **kwargs):
        """Create an error response"""
        return cls(success=False, error_message=message, **kwargs)

@dataclass
class CreateUserResponse(BaseResponse):
    """Response for user creation"""
    user: Optional[User] = None

@dataclass 
class GainExperienceResponse(BaseResponse):
    """Response for experience gain operation"""
    level_up: bool = False
    old_level: int = 0
    new_level: int = 0
    new_xp: int = 0
    xp_until_next: int = 0

@dataclass
class GetUserProfileResponse(BaseResponse):
    """Response for getting user profile"""
    user: Optional[User] = None
    success_rate: float = 0.0
    current_level_title: str = ""
    
@dataclass
class TrackOptimizationResponse(BaseResponse):
    """Response for tracking optimization results"""
    new_win_streak: int = 0
    total_optimizations: int = 0
    successful_optimizations: int = 0
    success_rate: float = 0.0

@dataclass
class UserStatsResponse(BaseResponse):
    """Response for user statistics"""
    user: Optional[User] = None
    performance_metrics: Optional[Dict[str, Any]] = None
    level_progress: Optional[Dict[str, Any]] = None