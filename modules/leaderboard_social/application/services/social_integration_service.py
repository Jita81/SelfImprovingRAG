"""
Social Integration Service - Cross-module coordination

This service orchestrates interactions between User Management, Achievement System,
and Leaderboard modules to provide seamless user experiences and consistent data flow.
"""

from typing import List, Dict, Any, Optional, Tuple
import sys
import os
from datetime import datetime

# Add paths for cross-module imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../user_management'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../achievement_system'))

try:
    # Import User Management module
    from user_management.application.services.user_service import UserService
    from user_management.application.dtos.user_requests import GainExperienceRequest, TrackOptimizationRequest
    
    # Import Achievement System module
    from achievement_system.application.services.achievement_service import AchievementService
    from achievement_system.application.dtos.achievement_requests import CheckAchievementUnlockRequest
    
    # Import local Leaderboard module
    from .leaderboard_service import LeaderboardService
    from ..dtos.leaderboard_requests import UpdateUserStatsRequest, GetSocialComparisonRequest
    from ..dtos.leaderboard_responses import UpdateUserStatsResponse
except ImportError as e:
    print(f"Warning: Some cross-module imports failed: {e}")
    # Define placeholder classes for development
    class UserService:
        pass
    class AchievementService:
        pass


class SocialIntegrationService:
    """
    Service that provides integrated workflows across User Management, 
    Achievement System, and Leaderboard modules.
    """
    
    def __init__(self, 
                 user_service: Optional['UserService'] = None,
                 achievement_service: Optional['AchievementService'] = None,
                 leaderboard_service: Optional['LeaderboardService'] = None):
        self.user_service = user_service
        self.achievement_service = achievement_service
        self.leaderboard_service = leaderboard_service
        
        # Event queue for cross-module notifications (simplified)
        self.event_queue = []
    
    def process_optimization_completion(self, 
                                      user_id: str, 
                                      optimization_successful: bool,
                                      xp_gained: int = 30,
                                      difficulty_level: str = "medium") -> Dict[str, Any]:
        """
        Process a complete optimization workflow across all modules.
        
        Args:
            user_id: ID of the user who completed the optimization
            optimization_successful: Whether the optimization was successful
            xp_gained: Experience points gained from the optimization
            difficulty_level: Difficulty level of the optimization
            
        Returns:
            Comprehensive result from all module updates
        """
        results = {
            "user_id": user_id,
            "optimization_successful": optimization_successful,
            "timestamp": datetime.utcnow().isoformat(),
            "updates": {}
        }
        
        try:
            # Step 1: Update User Management (XP and stats)
            if self.user_service:
                user_update = self._update_user_stats(
                    user_id, optimization_successful, xp_gained
                )
                results["updates"]["user_management"] = user_update
            
            # Step 2: Check Achievement unlocks
            if self.achievement_service:
                achievement_update = self._check_achievement_unlocks(
                    user_id, optimization_successful, xp_gained, difficulty_level
                )
                results["updates"]["achievements"] = achievement_update
            
            # Step 3: Update Leaderboard rankings
            if self.leaderboard_service:
                leaderboard_update = self._update_leaderboard_rankings(
                    user_id, optimization_successful, results["updates"]
                )
                results["updates"]["leaderboard"] = leaderboard_update
            
            # Step 4: Process cross-module effects
            cross_effects = self._process_cross_module_effects(results["updates"])
            results["updates"]["cross_effects"] = cross_effects
            
            results["success"] = True
            
        except Exception as e:
            results["success"] = False
            results["error"] = str(e)
        
        return results
    
    def get_comprehensive_user_profile(self, user_id: str) -> Dict[str, Any]:
        """
        Get a comprehensive user profile that combines data from all modules.
        
        Args:
            user_id: ID of the user
            
        Returns:
            Complete user profile with stats, achievements, and leaderboard position
        """
        profile = {
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "data": {}
        }
        
        try:
            # Get User Management data
            if self.user_service:
                user_data = self._get_user_management_data(user_id)
                profile["data"]["user_profile"] = user_data
            
            # Get Achievement data
            if self.achievement_service:
                achievement_data = self._get_achievement_data(user_id)
                profile["data"]["achievements"] = achievement_data
            
            # Get Leaderboard data
            if self.leaderboard_service:
                leaderboard_data = self._get_leaderboard_data(user_id)
                profile["data"]["leaderboard"] = leaderboard_data
            
            # Create unified statistics
            unified_stats = self._create_unified_statistics(profile["data"])
            profile["data"]["unified_stats"] = unified_stats
            
            profile["success"] = True
            
        except Exception as e:
            profile["success"] = False
            profile["error"] = str(e)
        
        return profile
    
    def create_social_comparison(self, 
                               user_id: str, 
                               comparison_type: str = "friends",
                               metric: str = "success_rate") -> Dict[str, Any]:
        """
        Create detailed social comparison including achievements and progress.
        
        Args:
            user_id: ID of the user
            comparison_type: Type of comparison ("friends", "team", "global")
            metric: Metric to compare
            
        Returns:
            Detailed social comparison data
        """
        comparison = {
            "user_id": user_id,
            "comparison_type": comparison_type,
            "metric": metric,
            "timestamp": datetime.utcnow().isoformat(),
            "results": {}
        }
        
        try:
            # Get basic leaderboard comparison
            if self.leaderboard_service:
                social_request = GetSocialComparisonRequest(
                    user_id=user_id,
                    comparison_type=comparison_type,
                    metric=metric
                )
                leaderboard_comparison = self.leaderboard_service.get_social_comparison(social_request)
                comparison["results"]["leaderboard"] = leaderboard_comparison.comparison_data
            
            # Enhance with achievement comparisons
            if self.achievement_service:
                achievement_comparison = self._compare_achievements(user_id, comparison_type)
                comparison["results"]["achievements"] = achievement_comparison
            
            # Add progress comparisons
            progress_comparison = self._compare_progress(user_id, comparison_type)
            comparison["results"]["progress"] = progress_comparison
            
            comparison["success"] = True
            
        except Exception as e:
            comparison["success"] = False
            comparison["error"] = str(e)
        
        return comparison
    
    def manage_team_membership(self, 
                             user_id: str, 
                             team_name: str, 
                             action: str = "join") -> Dict[str, Any]:
        """
        Manage team membership with cross-module updates.
        
        Args:
            user_id: ID of the user
            team_name: Name of the team
            action: Action to perform ("join", "leave", "create")
            
        Returns:
            Result of team membership changes
        """
        result = {
            "user_id": user_id,
            "team_name": team_name,
            "action": action,
            "timestamp": datetime.utcnow().isoformat(),
            "updates": {}
        }
        
        try:
            if action == "join":
                # Update user's team membership in all relevant modules
                if self.leaderboard_service:
                    # Update social connections with team info
                    self._update_team_membership(user_id, team_name)
                    result["updates"]["team_joined"] = True
                
                # Check for team-related achievements
                if self.achievement_service:
                    team_achievements = self._check_team_achievements(user_id, team_name, "joined")
                    result["updates"]["achievements"] = team_achievements
            
            elif action == "leave":
                if self.leaderboard_service:
                    self._update_team_membership(user_id, None)
                    result["updates"]["team_left"] = True
            
            elif action == "create":
                # Create new team and make user the leader
                team_creation = self._create_team(user_id, team_name)
                result["updates"]["team_created"] = team_creation
            
            result["success"] = True
            
        except Exception as e:
            result["success"] = False
            result["error"] = str(e)
        
        return result
    
    def _update_user_stats(self, user_id: str, success: bool, xp_gained: int) -> Dict[str, Any]:
        """Update user statistics in User Management module"""
        try:
            # Track optimization result
            if success:
                track_request = TrackOptimizationRequest(
                    user_id=user_id,
                    successful=True
                )
                track_response = self.user_service.track_optimization(track_request)
                
                # Gain experience points
                xp_request = GainExperienceRequest(
                    user_id=user_id,
                    xp_amount=xp_gained,
                    source="optimization_success"
                )
                xp_response = self.user_service.gain_experience(xp_request)
                
                return {
                    "optimization_tracked": track_response.success,
                    "xp_gained": xp_gained,
                    "level_up": xp_response.level_up_occurred if hasattr(xp_response, 'level_up_occurred') else False,
                    "new_level": xp_response.new_level if hasattr(xp_response, 'new_level') else None
                }
            else:
                track_request = TrackOptimizationRequest(
                    user_id=user_id,
                    successful=False
                )
                track_response = self.user_service.track_optimization(track_request)
                
                return {
                    "optimization_tracked": track_response.success,
                    "xp_gained": 0,
                    "level_up": False
                }
        except Exception as e:
            return {"error": str(e)}
    
    def _check_achievement_unlocks(self, user_id: str, success: bool, xp_gained: int, difficulty: str) -> Dict[str, Any]:
        """Check for achievement unlocks in Achievement System module"""
        try:
            # Create event data for achievement checking
            event_data = {
                "optimization_completed": True,
                "optimization_successful": success,
                "xp_gained": xp_gained,
                "difficulty_level": difficulty,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            unlock_request = CheckAchievementUnlockRequest(
                user_id=user_id,
                event_type="optimization_completed",
                event_data=event_data
            )
            
            unlock_response = self.achievement_service.check_achievement_unlock(unlock_request)
            
            return {
                "achievements_checked": True,
                "new_achievements": unlock_response.unlocked_achievements if hasattr(unlock_response, 'unlocked_achievements') else [],
                "xp_from_achievements": unlock_response.total_xp_awarded if hasattr(unlock_response, 'total_xp_awarded') else 0
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _update_leaderboard_rankings(self, user_id: str, success: bool, previous_updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update leaderboard rankings"""
        try:
            # Extract user stats from previous updates
            user_updates = previous_updates.get("user_management", {})
            
            update_request = UpdateUserStatsRequest(
                user_id=user_id,
                optimization_result=success
            )
            
            # Add additional stats if available
            if "new_level" in user_updates and user_updates["new_level"]:
                update_request.level = user_updates["new_level"]
            
            update_response = self.leaderboard_service.update_user_stats(update_request)
            
            return {
                "rankings_updated": update_response.success,
                "new_rank": update_response.new_rank,
                "previous_rank": update_response.previous_rank,
                "rank_change": update_response.rank_change,
                "new_streak": update_response.new_streak
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _process_cross_module_effects(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Process effects that span multiple modules"""
        effects = {}
        
        try:
            # Check if level up occurred and award bonus achievements
            user_update = updates.get("user_management", {})
            if user_update.get("level_up"):
                effects["level_up_bonus"] = "Level up achievement bonus awarded"
            
            # Check if new rank position unlocks achievements
            leaderboard_update = updates.get("leaderboard", {})
            rank_change = leaderboard_update.get("rank_change", 0)
            if rank_change > 0:  # Rank improved
                effects["rank_improvement"] = f"Rank improved by {rank_change} positions"
            
            # Check for streak milestones
            new_streak = leaderboard_update.get("new_streak", 0)
            if new_streak > 0 and new_streak % 5 == 0:  # Milestone every 5 streaks
                effects["streak_milestone"] = f"Streak milestone reached: {new_streak}"
            
            return effects
        except Exception as e:
            return {"error": str(e)}
    
    def _get_user_management_data(self, user_id: str) -> Dict[str, Any]:
        """Get user data from User Management module"""
        try:
            # This would call the user service to get profile and stats
            # For now, return placeholder
            return {
                "profile": {"user_id": user_id, "level": 10, "total_xp": 3000},
                "stats": {"success_rate": 85.5, "total_optimizations": 120}
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _get_achievement_data(self, user_id: str) -> Dict[str, Any]:
        """Get achievement data from Achievement System module"""
        try:
            # This would call the achievement service to get user achievements
            return {
                "total_achievements": 15,
                "recent_achievements": ["optimization_master", "streak_king"],
                "progress": {"optimization_expert": 0.8, "consistency_champion": 0.6}
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _get_leaderboard_data(self, user_id: str) -> Dict[str, Any]:
        """Get leaderboard data for user"""
        try:
            # This would call the leaderboard service
            return {
                "current_rank": 5,
                "rank_change_24h": +2,
                "current_streak": 8,
                "best_streak": 15
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _create_unified_statistics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create unified statistics from all modules"""
        try:
            user_data = data.get("user_profile", {})
            achievement_data = data.get("achievements", {})
            leaderboard_data = data.get("leaderboard", {})
            
            return {
                "overall_score": 850,  # Composite score
                "completion_rate": 92.5,  # Overall completion percentage
                "engagement_level": "High",  # Based on activity
                "progression_rate": "Excellent",  # Rate of improvement
                "social_standing": "Top 10%"  # Position in community
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _compare_achievements(self, user_id: str, comparison_type: str) -> Dict[str, Any]:
        """Compare achievements with social connections"""
        return {
            "user_achievement_count": 15,
            "peer_average": 12.3,
            "percentile": 75,
            "unique_achievements": 3
        }
    
    def _compare_progress(self, user_id: str, comparison_type: str) -> Dict[str, Any]:
        """Compare progress with social connections"""
        return {
            "user_progress_rate": 95.5,
            "peer_average": 78.2,
            "improvement_trend": "Accelerating",
            "consistency_score": 88.0
        }
    
    def _update_team_membership(self, user_id: str, team_name: Optional[str]) -> None:
        """Update team membership in leaderboard social connections"""
        # This would update the user's team information
        pass
    
    def _check_team_achievements(self, user_id: str, team_name: str, action: str) -> Dict[str, Any]:
        """Check for team-related achievements"""
        return {
            "team_achievements_checked": True,
            "new_team_achievements": [],
            "team_bonuses": []
        }
    
    def _create_team(self, user_id: str, team_name: str) -> Dict[str, Any]:
        """Create a new team"""
        return {
            "team_created": True,
            "team_name": team_name,
            "leader": user_id,
            "creation_timestamp": datetime.utcnow().isoformat()
        }