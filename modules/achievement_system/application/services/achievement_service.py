from typing import List, Dict, Any, Optional
import logging
from datetime import datetime, timezone

from ...domain.entities.achievement import Achievement
from ...domain.entities.user_achievement import UserAchievement
from ...domain.value_objects.achievement_rarity import AchievementRarity
from ..dtos.achievement_requests import (
    CheckAchievementUnlockRequest, GetUserAchievementsRequest, 
    GetAchievementProgressRequest, AwardAchievementRequest
)
from ..dtos.achievement_responses import (
    CheckAchievementUnlockResponse, GetUserAchievementsResponse, 
    GetAchievementProgressResponse, AwardAchievementResponse, AchievementStatsResponse
)
from ...infrastructure.repositories.achievement_repository import AchievementRepository
from ...infrastructure.repositories.user_achievement_repository import UserAchievementRepository

logger = logging.getLogger(__name__)

class AchievementService:
    """
    Application service for achievement management operations.
    Implements TDD Cycle 11: Achievement System
    """
    
    def __init__(self, achievement_repository: AchievementRepository, 
                 user_achievement_repository: UserAchievementRepository):
        self.achievement_repository = achievement_repository
        self.user_achievement_repository = user_achievement_repository
    
    def check_achievement_unlock(self, request: CheckAchievementUnlockRequest) -> CheckAchievementUnlockResponse:
        """
        Check if any achievements should be unlocked based on the provided event.
        
        Behavior: Evaluates all achievements, unlocks eligible ones, awards XP, tracks progress
        """
        try:
            # Validate request
            if not request.validate():
                return CheckAchievementUnlockResponse.error_response("Invalid request data")
            
            # Get all achievements and user's current achievements
            all_achievements = self.achievement_repository.get_all()
            user_achievements = self.user_achievement_repository.get_user_achievements(request.user_id)
            unlocked_achievement_ids = {ua.achievement_id for ua in user_achievements}
            
            unlocked_achievements = []
            total_xp_awarded = 0
            progress_updates = []
            
            for achievement in all_achievements:
                # Skip if already unlocked
                if achievement.id in unlocked_achievement_ids:
                    continue
                
                # Check if achievement conditions are met
                if achievement.check_unlock_conditions(request.event_data):
                    # Achievement unlocked!
                    final_xp = achievement.calculate_final_xp_reward()
                    
                    # Create user achievement record
                    user_achievement = UserAchievement.create_new(
                        user_id=request.user_id,
                        achievement_id=achievement.id,
                        xp_awarded=final_xp
                    )
                    
                    # Save to repository
                    self.user_achievement_repository.save_user_achievement(user_achievement)
                    
                    unlocked_achievements.append(achievement)
                    total_xp_awarded += final_xp
                    
                    logger.info(
                        f"Achievement unlocked: User {request.user_id} earned '{achievement.name}' "
                        f"({achievement.rarity.value}) for {final_xp} XP"
                    )
                else:
                    # Calculate progress for achievements not yet unlocked
                    progress = achievement.calculate_progress(request.event_data)
                    if progress["progress_percentage"] > 0:
                        progress_updates.append(progress)
            
            return CheckAchievementUnlockResponse.success_response(
                unlocked_achievements=unlocked_achievements,
                total_xp_awarded=total_xp_awarded,
                progress_updates=progress_updates
            )
            
        except Exception as e:
            logger.error(f"Error checking achievement unlock for user {request.user_id}: {e}")
            return CheckAchievementUnlockResponse.error_response(f"Failed to check achievements: {str(e)}")
    
    def get_user_achievements(self, request: GetUserAchievementsRequest) -> GetUserAchievementsResponse:
        """
        Get comprehensive achievement data for a user.
        
        Behavior: Returns unlocked/locked achievements with statistics and progress
        """
        try:
            # Validate request
            if not request.validate():
                return GetUserAchievementsResponse.error_response("Invalid request data")
            
            # Get all achievements and user's achievements
            all_achievements = self.achievement_repository.get_all()
            user_achievements = self.user_achievement_repository.get_user_achievements(request.user_id)
            
            # Filter by category if requested
            if request.category_filter:
                all_achievements = [a for a in all_achievements if a.category == request.category_filter]
            
            # Build lookup of unlocked achievements
            unlocked_lookup = {ua.achievement_id: ua for ua in user_achievements}
            
            # Separate unlocked and locked achievements
            unlocked_achievements = []
            locked_achievements = []
            
            for achievement in all_achievements:
                if achievement.id in unlocked_lookup:
                    unlocked_achievements.append(achievement)
                elif request.include_locked:
                    locked_achievements.append(achievement)
            
            # Calculate statistics
            unlocked_count = len(unlocked_achievements)
            total_achievements = len(all_achievements)
            completion_percentage = (unlocked_count / total_achievements * 100) if total_achievements > 0 else 0
            
            # Calculate total XP from achievements
            total_xp_from_achievements = sum(ua.xp_awarded for ua in user_achievements)
            
            # Count rare achievements
            rare_achievements_count = sum(1 for ach in unlocked_achievements if ach.is_rare)
            
            # Get recent achievements (within 7 days)
            recent_achievements = [ua for ua in user_achievements if ua.is_recent]
            
            # Calculate progress for locked achievements
            achievement_progress = []
            for achievement in locked_achievements:
                # For progress calculation, we would need current user stats
                # For now, return basic progress structure
                progress = {
                    "achievement_id": achievement.id,
                    "name": achievement.name,
                    "current_progress": 0,
                    "required_progress": 1,
                    "progress_percentage": 0
                }
                achievement_progress.append(progress)
            
            logger.info(f"Retrieved achievement data for user {request.user_id}: {unlocked_count}/{total_achievements} unlocked")
            
            return GetUserAchievementsResponse.success_response(
                unlocked_achievements=unlocked_achievements,
                locked_achievements=locked_achievements,
                unlocked_count=unlocked_count,
                total_achievements=total_achievements,
                completion_percentage=completion_percentage,
                total_xp_from_achievements=total_xp_from_achievements,
                rare_achievements_count=rare_achievements_count,
                recent_achievements=recent_achievements,
                achievement_progress=achievement_progress
            )
            
        except Exception as e:
            logger.error(f"Error getting user achievements for {request.user_id}: {e}")
            return GetUserAchievementsResponse.error_response(f"Failed to get achievements: {str(e)}")
    
    def get_achievement_progress(self, request: GetAchievementProgressRequest) -> GetAchievementProgressResponse:
        """
        Get detailed progress information for achievements.
        """
        try:
            # Validate request
            if not request.validate():
                return GetAchievementProgressResponse.error_response("Invalid request data")
            
            # Get achievements (specific one or all)
            if request.achievement_id:
                achievement = self.achievement_repository.get_by_id(request.achievement_id)
                achievements = [achievement] if achievement else []
            else:
                achievements = self.achievement_repository.get_all()
            
            # Get user's unlocked achievements
            user_achievements = self.user_achievement_repository.get_user_achievements(request.user_id)
            unlocked_ids = {ua.achievement_id for ua in user_achievements}
            
            # Calculate progress for non-unlocked achievements
            achievement_progress = []
            achievements_near_completion = []
            
            for achievement in achievements:
                if achievement.id not in unlocked_ids:
                    # For now, return basic progress (would need user stats for real calculation)
                    progress = {
                        "achievement_id": achievement.id,
                        "name": achievement.name,
                        "description": achievement.description,
                        "current_progress": 0,
                        "required_progress": 1,
                        "progress_percentage": 0,
                        "trigger_description": achievement.trigger.description
                    }
                    achievement_progress.append(progress)
                    
                    # Check if near completion (>75% progress)
                    if progress["progress_percentage"] > 75:
                        achievements_near_completion.append(progress)
            
            total_achievements = len(achievements)
            unlocked_count = sum(1 for a in achievements if a.id in unlocked_ids)
            overall_completion = (unlocked_count / total_achievements * 100) if total_achievements > 0 else 0
            
            return GetAchievementProgressResponse.success_response(
                achievement_progress=achievement_progress,
                overall_completion_percentage=overall_completion,
                achievements_near_completion=achievements_near_completion
            )
            
        except Exception as e:
            logger.error(f"Error getting achievement progress for {request.user_id}: {e}")
            return GetAchievementProgressResponse.error_response(f"Failed to get progress: {str(e)}")
    
    def award_achievement(self, request: AwardAchievementRequest) -> AwardAchievementResponse:
        """
        Manually award an achievement to a user (admin function).
        """
        try:
            # Validate request
            if not request.validate():
                return AwardAchievementResponse.error_response("Invalid request data")
            
            # Get achievement
            achievement = self.achievement_repository.get_by_id(request.achievement_id)
            if not achievement:
                return AwardAchievementResponse.error_response("Achievement not found")
            
            # Check if user already has this achievement
            user_achievements = self.user_achievement_repository.get_user_achievements(request.user_id)
            if any(ua.achievement_id == request.achievement_id for ua in user_achievements):
                return AwardAchievementResponse.error_response("User already has this achievement")
            
            # Calculate XP reward
            xp_awarded = achievement.calculate_final_xp_reward()
            
            # Create user achievement
            user_achievement = UserAchievement.create_new(
                user_id=request.user_id,
                achievement_id=request.achievement_id,
                xp_awarded=xp_awarded
            )
            
            # Save to repository
            self.user_achievement_repository.save_user_achievement(user_achievement)
            
            logger.info(
                f"Achievement manually awarded: User {request.user_id} received '{achievement.name}' "
                f"for {xp_awarded} XP. Reason: {request.reason}"
            )
            
            return AwardAchievementResponse.success_response(
                achievement=achievement,
                user_achievement=user_achievement,
                xp_awarded=xp_awarded
            )
            
        except Exception as e:
            logger.error(f"Error awarding achievement to user {request.user_id}: {e}")
            return AwardAchievementResponse.error_response(f"Failed to award achievement: {str(e)}")
    
    def get_achievement_stats(self, user_id: str) -> AchievementStatsResponse:
        """
        Get comprehensive achievement statistics for a user.
        """
        try:
            # Get all achievements and user achievements
            all_achievements = self.achievement_repository.get_all()
            user_achievements = self.user_achievement_repository.get_user_achievements(user_id)
            
            # Calculate basic stats
            total_achievements = len(all_achievements)
            unlocked_achievements = len(user_achievements)
            completion_percentage = (unlocked_achievements / total_achievements * 100) if total_achievements > 0 else 0
            total_xp_earned = sum(ua.xp_awarded for ua in user_achievements)
            
            # Count rare achievements
            unlocked_ids = {ua.achievement_id for ua in user_achievements}
            unlocked_achievement_objects = [a for a in all_achievements if a.id in unlocked_ids]
            rare_achievements_unlocked = sum(1 for a in unlocked_achievement_objects if a.is_rare)
            
            # Get completed categories
            unlocked_categories = set(a.category for a in unlocked_achievement_objects)
            all_categories = set(a.category for a in all_achievements)
            categories_completed = []
            for category in all_categories:
                category_achievements = [a for a in all_achievements if a.category == category]
                category_unlocked = [a for a in unlocked_achievement_objects if a.category == category]
                if len(category_unlocked) == len(category_achievements):
                    categories_completed.append(category)
            
            # Get most recent achievement
            most_recent_achievement = None
            if user_achievements:
                most_recent_achievement = max(user_achievements, key=lambda ua: ua.unlocked_at)
            
            return AchievementStatsResponse.success_response(
                total_achievements=total_achievements,
                unlocked_achievements=unlocked_achievements,
                completion_percentage=completion_percentage,
                total_xp_earned=total_xp_earned,
                rare_achievements_unlocked=rare_achievements_unlocked,
                categories_completed=categories_completed,
                longest_unlock_streak=0,  # Would need to calculate from unlock dates
                most_recent_achievement=most_recent_achievement
            )
            
        except Exception as e:
            logger.error(f"Error getting achievement stats for user {user_id}: {e}")
            return AchievementStatsResponse.error_response(f"Failed to get stats: {str(e)}")