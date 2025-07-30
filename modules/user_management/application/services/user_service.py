from typing import Optional
import logging
from datetime import datetime, timezone

from ...domain.entities.user import User
from ...domain.value_objects.user_profile import UserProfile
from ...domain.value_objects.gamification_stats import GamificationStats
from ..dtos.user_requests import CreateUserRequest, GainExperienceRequest, TrackOptimizationRequest
from ..dtos.user_responses import (
    CreateUserResponse, GainExperienceResponse, GetUserProfileResponse, 
    TrackOptimizationResponse, UserStatsResponse
)
from ...infrastructure.repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)

class UserService:
    """
    Application service for user management operations.
    Implements TDD Cycle 10: User Management & Gamification System
    """
    
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
    
    def create_user(self, request: CreateUserRequest) -> CreateUserResponse:
        """
        Create a new user with initial gamification stats.
        
        Behavior: Creates user with level 1, 0 XP, and empty optimization stats
        """
        try:
            # Validate request
            if not request.validate():
                return CreateUserResponse.error_response("Invalid request data")
            
            # Create user profile (this will validate email format)
            try:
                profile = UserProfile(
                    email=request.email,
                    name=request.name,
                    role=request.role,
                    team=request.team,
                    company=request.company
                )
            except ValueError as e:
                return CreateUserResponse.error_response(str(e))
            
            # Create user with initial gamification stats
            user = User.create_new_user(profile)
            
            # Save to repository
            saved_user = self.user_repository.save(user)
            
            logger.info(f"Created new user: {saved_user.id} ({saved_user.profile.email})")
            
            return CreateUserResponse.success_response(user=saved_user)
            
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return CreateUserResponse.error_response(f"Failed to create user: {str(e)}")
    
    def gain_experience(self, request: GainExperienceRequest) -> GainExperienceResponse:
        """
        Award experience points to a user and handle level ups.
        
        Behavior: Updates XP, calculates level ups, manages XP carryover
        """
        try:
            # Validate request
            if not request.validate():
                return GainExperienceResponse.error_response("Invalid request data")
            
            # Get user
            user = self.user_repository.get_by_id(request.user_id)
            if not user:
                return GainExperienceResponse.error_response("User not found")
            
            # Gain experience
            result = user.gain_experience(request.points, request.reason)
            
            # Save updated user
            self.user_repository.save(user)
            
            logger.info(
                f"User {user.id} gained {request.points} XP for {request.reason}. "
                f"Level up: {result['level_up']}"
            )
            
            return GainExperienceResponse.success_response(
                level_up=result["level_up"],
                old_level=result["old_level"], 
                new_level=result["new_level"],
                new_xp=result["new_xp"],
                xp_until_next=result["xp_until_next"]
            )
            
        except Exception as e:
            logger.error(f"Error gaining experience for user {request.user_id}: {e}")
            return GainExperienceResponse.error_response(f"Failed to gain experience: {str(e)}")
    
    def track_optimization_result(self, user_id: str, success: bool) -> TrackOptimizationResponse:
        """
        Track an optimization attempt and update user stats.
        
        Behavior: Updates optimization counts, manages win streaks
        """
        try:
            # Get user
            user = self.user_repository.get_by_id(user_id)
            if not user:
                return TrackOptimizationResponse.error_response("User not found")
            
            # Track optimization
            result = user.track_optimization_result(success)
            
            # Save updated user
            self.user_repository.save(user)
            
            logger.info(
                f"Tracked optimization for user {user_id}: success={success}, "
                f"win_streak={result['new_win_streak']}"
            )
            
            return TrackOptimizationResponse.success_response(
                new_win_streak=result["new_win_streak"],
                total_optimizations=result["total_optimizations"],
                successful_optimizations=result["successful_optimizations"],
                success_rate=result["success_rate"]
            )
            
        except Exception as e:
            logger.error(f"Error tracking optimization for user {user_id}: {e}")
            return TrackOptimizationResponse.error_response(f"Failed to track optimization: {str(e)}")
    
    def get_user_profile(self, user_id: str) -> GetUserProfileResponse:
        """
        Get complete user profile with gamification stats and derived metrics.
        
        Behavior: Returns full user information with calculated metrics
        """
        try:
            # Get user
            user = self.user_repository.get_by_id(user_id)
            if not user:
                return GetUserProfileResponse.error_response("User not found")
            
            # Calculate derived metrics
            success_rate = user.gamification.success_rate
            current_level_title = user.gamification.current_level_title
            
            logger.info(f"Retrieved profile for user {user_id}")
            
            return GetUserProfileResponse.success_response(
                user=user,
                success_rate=success_rate,
                current_level_title=current_level_title
            )
            
        except Exception as e:
            logger.error(f"Error getting user profile {user_id}: {e}")
            return GetUserProfileResponse.error_response(f"Failed to get user profile: {str(e)}")
    
    def get_user_stats(self, user_id: str) -> UserStatsResponse:
        """
        Get comprehensive user statistics including performance and level progress.
        """
        try:
            # Get user
            user = self.user_repository.get_by_id(user_id)
            if not user:
                return UserStatsResponse.error_response("User not found")
            
            # Compile performance metrics
            performance_metrics = {
                "total_optimizations": user.gamification.total_optimizations,
                "successful_optimizations": user.gamification.successful_optimizations,
                "success_rate": user.gamification.success_rate,
                "current_win_streak": user.gamification.win_streak,
                "is_active_user": user.is_active_user
            }
            
            # Compile level progress
            level_progress = user.experience_level_info
            
            return UserStatsResponse.success_response(
                user=user,
                performance_metrics=performance_metrics,
                level_progress=level_progress
            )
            
        except Exception as e:
            logger.error(f"Error getting user stats for {user_id}: {e}")
            return UserStatsResponse.error_response(f"Failed to get user stats: {str(e)}")
    
    def update_user_profile(self, user_id: str, **updates) -> GetUserProfileResponse:
        """
        Update user profile information.
        Note: Profile is immutable, so this creates a new profile.
        """
        try:
            # Get user
            user = self.user_repository.get_by_id(user_id)
            if not user:
                return GetUserProfileResponse.error_response("User not found")
            
            # Create updated profile
            profile_data = {
                "email": updates.get("email", user.profile.email),
                "name": updates.get("name", user.profile.name),
                "role": updates.get("role", user.profile.role),
                "team": updates.get("team", user.profile.team),
                "company": updates.get("company", user.profile.company)
            }
            
            try:
                new_profile = UserProfile(**profile_data)
            except ValueError as e:
                return GetUserProfileResponse.error_response(f"Invalid profile data: {str(e)}")
            
            # Create updated user
            user.profile = new_profile
            user.update_last_active()
            
            # Save updated user
            self.user_repository.save(user)
            
            logger.info(f"Updated profile for user {user_id}")
            
            return GetUserProfileResponse.success_response(
                user=user,
                success_rate=user.gamification.success_rate,
                current_level_title=user.gamification.current_level_title
            )
            
        except Exception as e:
            logger.error(f"Error updating user profile {user_id}: {e}")
            return GetUserProfileResponse.error_response(f"Failed to update profile: {str(e)}")