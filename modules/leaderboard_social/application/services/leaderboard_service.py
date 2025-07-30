"""
Leaderboard Service - Main application service for leaderboard functionality

This service orchestrates leaderboard operations including ranking calculations,
social comparisons, and historical snapshot management.
"""

from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime

try:
    from ..dtos.leaderboard_requests import (
        GetLeaderboardRequest, UpdateUserStatsRequest, GetUserRankingRequest,
        GetSocialComparisonRequest, CreateHistoricalSnapshotRequest
    )
    from ..dtos.leaderboard_responses import (
        GetLeaderboardResponse, UpdateUserStatsResponse, GetUserRankingResponse,
        GetSocialComparisonResponse, CreateHistoricalSnapshotResponse
    )
    from ...infrastructure.repositories.leaderboard_repository import LeaderboardRepository
    from ...infrastructure.repositories.user_stats_repository import UserStatsRepository
    from ...domain.entities.leaderboard_entry import LeaderboardEntry
    from ...domain.value_objects.ranking_criteria import RankingCriteria
except ImportError:
    # Alternative imports for direct execution
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    
    from application.dtos.leaderboard_requests import (
        GetLeaderboardRequest, UpdateUserStatsRequest, GetUserRankingRequest,
        GetSocialComparisonRequest, CreateHistoricalSnapshotRequest
    )
    from application.dtos.leaderboard_responses import (
        GetLeaderboardResponse, UpdateUserStatsResponse, GetUserRankingResponse,
        GetSocialComparisonResponse, CreateHistoricalSnapshotResponse
    )
    from infrastructure.repositories.leaderboard_repository import LeaderboardRepository
    from infrastructure.repositories.user_stats_repository import UserStatsRepository
    from domain.entities.leaderboard_entry import LeaderboardEntry
    from domain.value_objects.ranking_criteria import RankingCriteria


class LeaderboardService:
    """
    Service for managing leaderboards and social comparisons.
    
    Handles ranking calculations, user statistics updates, social features,
    and historical snapshot management.
    """
    
    def __init__(self, leaderboard_repo: LeaderboardRepository, user_stats_repo: UserStatsRepository):
        self.leaderboard_repo = leaderboard_repo
        self.user_stats_repo = user_stats_repo
    
    def get_leaderboard(self, request: GetLeaderboardRequest) -> GetLeaderboardResponse:
        """
        Get leaderboard data with filtering and ranking.
        
        Args:
            request: Leaderboard request with filtering options
            
        Returns:
            GetLeaderboardResponse with leaderboard entries
        """
        try:
            request.validate()
            
            # Get entries based on filters
            if request.team_name:
                entries = self.leaderboard_repo.find_entries_by_team(request.team_name, request.period)
            elif request.category:
                entries = self.leaderboard_repo.find_entries_by_category(request.category, request.limit)
            else:
                entries = self.leaderboard_repo.find_entries_by_period(request.period, request.limit, request.offset)
            
            # Apply privacy filtering
            if request.respect_privacy:
                entries = [e for e in entries if e.is_visible]
            
            # Apply ranking criteria
            ranking_criteria = self._get_ranking_criteria(request.ranking_criteria)
            entries = self._apply_ranking(entries, ranking_criteria)
            
            # Set period-specific attributes for weekly entries
            if request.period == "weekly":
                for entry in entries:
                    entry.weekly_success_rate = entry.period_success_rate or entry.success_rate
            
            # Convert to display format
            leaderboard_data = [entry.get_display_data() for entry in entries]
            
            # Get team statistics if team filter is applied
            team_stats = None
            if request.team_name:
                team_stats = self._calculate_team_statistics(request.team_name, entries)
            
            return GetLeaderboardResponse(
                success=True,
                leaderboard_entries=leaderboard_data,
                period=request.period,
                category=request.category,
                team_name=request.team_name,
                total_participants=len(entries),
                ranking_criteria=request.ranking_criteria,
                team_statistics=team_stats
            )
            
        except Exception as e:
            return GetLeaderboardResponse(
                success=False,
                error=str(e)
            )
    
    def update_user_stats(self, request: UpdateUserStatsRequest) -> UpdateUserStatsResponse:
        """
        Update user statistics and recalculate rankings.
        
        Args:
            request: User statistics update request
            
        Returns:
            UpdateUserStatsResponse with updated ranking info
        """
        try:
            request.validate()
            
            # Get or create user entry
            entry = self.leaderboard_repo.find_entry_by_user_id(request.user_id)
            if not entry:
                # Create new entry with basic data
                entry = LeaderboardEntry(
                    user_id=request.user_id,
                    rank=999,  # Will be recalculated
                    user_name=f"User {request.user_id}",
                    success_rate=request.success_rate or 0.0,
                    total_optimizations=request.total_optimizations or 0,
                    successful_optimizations=request.successful_optimizations or 0,
                    current_streak=request.current_streak or 0,
                    best_streak=request.current_streak or 0,
                    level=request.level or 1,
                    total_xp=request.total_xp or 0
                )
            
            previous_rank = entry.rank
            
            # Update statistics
            entry.update_statistics(
                success_rate=request.success_rate,
                total_optimizations=request.total_optimizations,
                successful_optimizations=request.successful_optimizations,
                current_streak=request.current_streak,
                level=request.level,
                total_xp=request.total_xp
            )
            
            # Handle streak updates based on optimization result
            new_streak = entry.current_streak
            if request.optimization_result is not None:
                if request.optimization_result:
                    # Only increment if current_streak wasn't already provided in request
                    if request.current_streak is None:
                        new_streak = entry.current_streak + 1
                    else:
                        new_streak = request.current_streak
                else:
                    new_streak = 0
                entry.current_streak = new_streak
                if new_streak > entry.best_streak:
                    entry.best_streak = new_streak
            elif request.current_streak is not None:
                # Use provided streak value
                new_streak = request.current_streak
            
            # Save updated entry
            self.leaderboard_repo.save_entry(entry)
            
            # Recalculate rankings for all users
            all_entries = self.leaderboard_repo.find_entries_by_period("all_time", limit=100)
            ranking_criteria = RankingCriteria.create_default()
            ranked_entries = self._apply_ranking(all_entries, ranking_criteria)
            
            # Find new rank
            new_rank = entry.rank
            for ranked_entry in ranked_entries:
                if ranked_entry.user_id == request.user_id:
                    new_rank = ranked_entry.rank
                    break
            
            rank_change = previous_rank - new_rank if previous_rank != 999 else 0
            
            return UpdateUserStatsResponse(
                success=True,
                user_id=request.user_id,
                new_rank=new_rank,
                previous_rank=previous_rank if previous_rank != 999 else None,
                new_streak=new_streak,
                rank_change=rank_change
            )
            
        except Exception as e:
            return UpdateUserStatsResponse(
                success=False,
                error=str(e)
            )
    
    def get_user_ranking(self, request: GetUserRankingRequest) -> GetUserRankingResponse:
        """
        Get specific user's ranking and composite score.
        
        Args:
            request: User ranking request
            
        Returns:
            GetUserRankingResponse with user's ranking details
        """
        try:
            request.validate()
            
            entry = self.leaderboard_repo.find_entry_by_user_id(request.user_id, request.period)
            if not entry:
                return GetUserRankingResponse(
                    success=False,
                    error="User not found in leaderboard"
                )
            
            # Calculate composite score
            ranking_criteria = self._get_ranking_criteria(request.ranking_criteria)
            user_stats = {
                "success_rate": entry.success_rate,
                "total_optimizations": entry.total_optimizations,
                "current_streak": entry.current_streak,
                "level": entry.level
            }
            
            composite_score, score_breakdown = ranking_criteria.calculate_composite_score(user_stats)
            
            return GetUserRankingResponse(
                success=True,
                user_id=request.user_id,
                rank=entry.rank,
                composite_score=composite_score,
                score_breakdown=score_breakdown,
                period=request.period,
                category=request.category
            )
            
        except Exception as e:
            return GetUserRankingResponse(
                success=False,
                error=str(e)
            )
    
    def get_social_comparison(self, request: GetSocialComparisonRequest) -> GetSocialComparisonResponse:
        """
        Get social comparison data for a user.
        
        Args:
            request: Social comparison request
            
        Returns:
            GetSocialComparisonResponse with comparison data
        """
        try:
            request.validate()
            
            # Get user's social connections
            social_data = self.user_stats_repo.get_user_social_data(request.user_id)
            if not social_data:
                return GetSocialComparisonResponse(
                    success=False,
                    error="Social data not found for user"
                )
            
            comparison_data = {}
            
            if request.comparison_type == "friends":
                friends_stats = []
                for friend_id in social_data.friends:
                    friend_entry = self.leaderboard_repo.find_entry_by_user_id(friend_id)
                    if friend_entry:
                        metric_value = getattr(friend_entry, request.metric, 0)
                        friends_stats.append(metric_value)
                
                if friends_stats:
                    friends_average = sum(friends_stats) / len(friends_stats)
                    user_entry = self.leaderboard_repo.find_entry_by_user_id(request.user_id)
                    user_value = getattr(user_entry, request.metric, 0) if user_entry else 0
                    
                    # Calculate rank among friends
                    friends_stats.append(user_value)
                    friends_stats.sort(reverse=True)
                    user_rank_among_friends = friends_stats.index(user_value) + 1
                    
                    comparison_data = {
                        "friends_average": friends_average,
                        "user_rank_among_friends": user_rank_among_friends,
                        "friends_count": len(social_data.friends),
                        "user_value": user_value
                    }
                else:
                    comparison_data = {
                        "friends_average": 0,
                        "user_rank_among_friends": 1,
                        "friends_count": 0,
                        "user_value": 0
                    }
            
            return GetSocialComparisonResponse(
                success=True,
                user_id=request.user_id,
                comparison_type=request.comparison_type,
                metric=request.metric,
                comparison_data=comparison_data
            )
            
        except Exception as e:
            return GetSocialComparisonResponse(
                success=False,
                error=str(e)
            )
    
    def create_historical_snapshot(self, request: CreateHistoricalSnapshotRequest) -> CreateHistoricalSnapshotResponse:
        """
        Create a historical snapshot of the leaderboard.
        
        Args:
            request: Historical snapshot creation request
            
        Returns:
            CreateHistoricalSnapshotResponse with snapshot details
        """
        try:
            request.validate()
            
            # Get current leaderboard state
            entries = self.leaderboard_repo.find_entries_by_period(request.period, limit=100)
            
            # Generate snapshot ID
            snapshot_id = str(uuid.uuid4())
            
            # Save snapshot
            self.leaderboard_repo.save_historical_snapshot(
                snapshot_id=snapshot_id,
                period=request.period,
                snapshot_date=request.snapshot_date,
                entries=entries
            )
            
            return CreateHistoricalSnapshotResponse(
                success=True,
                snapshot_id=snapshot_id,
                period=request.period,
                snapshot_date=request.snapshot_date,
                participants_count=len(entries)
            )
            
        except Exception as e:
            return CreateHistoricalSnapshotResponse(
                success=False,
                error=str(e)
            )
    
    def get_historical_snapshot(self, snapshot_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a historical snapshot.
        
        Args:
            snapshot_id: ID of the snapshot to retrieve
            
        Returns:
            Snapshot data or None if not found
        """
        return self.leaderboard_repo.get_historical_snapshot(snapshot_id)
    
    def _get_ranking_criteria(self, criteria_type: str) -> RankingCriteria:
        """Get ranking criteria based on type"""
        if criteria_type == "streak_focused":
            return RankingCriteria.create_streak_focused()
        elif criteria_type == "volume_focused":
            return RankingCriteria.create_volume_focused()
        else:
            return RankingCriteria.create_default()
    
    def _apply_ranking(self, entries: List[LeaderboardEntry], criteria: RankingCriteria) -> List[LeaderboardEntry]:
        """Apply ranking criteria to sort and rank entries"""
        # Sort entries using ranking criteria
        def sort_key(entry):
            user_stats = {
                "success_rate": entry.success_rate,
                "total_optimizations": entry.total_optimizations,
                "current_streak": entry.current_streak,
                "level": entry.level
            }
            score, _ = criteria.calculate_composite_score(user_stats)
            return score
        
        entries.sort(key=sort_key, reverse=True)
        
        # Assign ranks and calculate scores
        for i, entry in enumerate(entries):
            entry.rank = i + 1
            user_stats = {
                "success_rate": entry.success_rate,
                "total_optimizations": entry.total_optimizations,
                "current_streak": entry.current_streak,
                "level": entry.level
            }
            score, breakdown = criteria.calculate_composite_score(user_stats)
            entry.set_composite_score(score, breakdown)
        
        return entries
    
    def _calculate_team_statistics(self, team_name: str, team_entries: List[LeaderboardEntry]) -> Dict[str, Any]:
        """Calculate team-level statistics"""
        if not team_entries:
            return {}
        
        total_optimizations = sum(entry.total_optimizations for entry in team_entries)
        average_success_rate = sum(entry.success_rate for entry in team_entries) / len(team_entries)
        average_level = sum(entry.level for entry in team_entries) / len(team_entries)
        
        return {
            "average_success_rate": round(average_success_rate, 1),
            "total_team_optimizations": total_optimizations,
            "team_level_average": round(average_level, 1),
            "member_count": len(team_entries)
        }