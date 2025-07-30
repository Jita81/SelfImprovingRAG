"""
Leaderboard API Controller - HTTP endpoints for leaderboard functionality

This controller provides RESTful API endpoints for all leaderboard and social
features, with proper error handling and response formatting.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import json

try:
    from ..application.services.leaderboard_service import LeaderboardService
    from ..application.services.social_integration_service import SocialIntegrationService
    from ..application.dtos.leaderboard_requests import (
        GetLeaderboardRequest, UpdateUserStatsRequest, GetUserRankingRequest,
        GetSocialComparisonRequest, CreateHistoricalSnapshotRequest
    )
    from ..infrastructure.repositories.leaderboard_repository import InMemoryLeaderboardRepository
    from ..infrastructure.repositories.user_stats_repository import InMemoryUserStatsRepository
except ImportError:
    # Placeholder for development
    class LeaderboardService:
        pass
    class SocialIntegrationService:
        pass


class LeaderboardController:
    """
    RESTful API controller for leaderboard and social features.
    
    Provides HTTP endpoints for all leaderboard operations with proper
    error handling, validation, and response formatting.
    """
    
    def __init__(self, 
                 leaderboard_service: Optional['LeaderboardService'] = None,
                 social_integration_service: Optional['SocialIntegrationService'] = None):
        # Initialize services with default implementations if not provided
        if leaderboard_service is None:
            leaderboard_repo = InMemoryLeaderboardRepository()
            user_stats_repo = InMemoryUserStatsRepository()
            self.leaderboard_service = LeaderboardService(leaderboard_repo, user_stats_repo)
        else:
            self.leaderboard_service = leaderboard_service
            
        self.social_integration_service = social_integration_service
    
    # ========== Leaderboard Endpoints ==========
    
    def get_leaderboard(self, query_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        GET /api/leaderboard
        
        Query Parameters:
        - period: string (daily, weekly, monthly, all_time) - default: all_time
        - limit: int (1-100) - default: 10
        - offset: int - default: 0
        - category: string (optional)
        - team_name: string (optional)
        - ranking_criteria: string (default, streak_focused, volume_focused) - default: default
        - respect_privacy: boolean - default: true
        """
        try:
            # Extract and validate query parameters
            period = query_params.get('period', 'all_time')
            limit = min(int(query_params.get('limit', 10)), 100)
            offset = max(int(query_params.get('offset', 0)), 0)
            category = query_params.get('category')
            team_name = query_params.get('team_name')
            ranking_criteria = query_params.get('ranking_criteria', 'default')
            respect_privacy = query_params.get('respect_privacy', 'true').lower() == 'true'
            
            # Create request object
            request = GetLeaderboardRequest(
                period=period,
                limit=limit,
                offset=offset,
                category=category,
                team_name=team_name,
                ranking_criteria=ranking_criteria,
                respect_privacy=respect_privacy
            )
            
            # Validate request
            request.validate()
            
            # Get leaderboard data
            response = self.leaderboard_service.get_leaderboard(request)
            
            if response.success:
                return {
                    "status": "success",
                    "data": {
                        "leaderboard": response.leaderboard_entries,
                        "metadata": {
                            "period": response.period,
                            "category": response.category,
                            "team_name": response.team_name,
                            "total_participants": response.total_participants,
                            "ranking_criteria": response.ranking_criteria,
                            "team_statistics": response.team_statistics
                        },
                        "pagination": {
                            "limit": limit,
                            "offset": offset,
                            "has_more": len(response.leaderboard_entries) == limit
                        }
                    },
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return self._error_response(400, response.error or "Failed to retrieve leaderboard")
                
        except ValueError as e:
            return self._error_response(400, f"Invalid parameter: {str(e)}")
        except Exception as e:
            return self._error_response(500, f"Internal server error: {str(e)}")
    
    def get_user_ranking(self, user_id: str, query_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        GET /api/leaderboard/users/{user_id}/ranking
        
        Query Parameters:
        - period: string - default: all_time
        - category: string (optional)
        - ranking_criteria: string - default: default
        """
        try:
            if not user_id:
                return self._error_response(400, "User ID is required")
            
            period = query_params.get('period', 'all_time')
            category = query_params.get('category')
            ranking_criteria = query_params.get('ranking_criteria', 'default')
            
            request = GetUserRankingRequest(
                user_id=user_id,
                period=period,
                category=category,
                ranking_criteria=ranking_criteria
            )
            
            request.validate()
            response = self.leaderboard_service.get_user_ranking(request)
            
            if response.success:
                return {
                    "status": "success",
                    "data": {
                        "user_id": response.user_id,
                        "rank": response.rank,
                        "composite_score": response.composite_score,
                        "score_breakdown": response.score_breakdown,
                        "period": response.period,
                        "category": response.category
                    },
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return self._error_response(404, response.error or "User not found")
                
        except ValueError as e:
            return self._error_response(400, f"Invalid parameter: {str(e)}")
        except Exception as e:
            return self._error_response(500, f"Internal server error: {str(e)}")
    
    def update_user_stats(self, user_id: str, request_body: Dict[str, Any]) -> Dict[str, Any]:
        """
        PUT /api/leaderboard/users/{user_id}/stats
        
        Request Body:
        {
            "success_rate": float (optional),
            "total_optimizations": int (optional),
            "successful_optimizations": int (optional),
            "current_streak": int (optional),
            "level": int (optional),
            "total_xp": int (optional),
            "optimization_result": boolean (optional)
        }
        """
        try:
            if not user_id:
                return self._error_response(400, "User ID is required")
            
            # Extract request body parameters
            success_rate = request_body.get('success_rate')
            total_optimizations = request_body.get('total_optimizations')
            successful_optimizations = request_body.get('successful_optimizations')
            current_streak = request_body.get('current_streak')
            level = request_body.get('level')
            total_xp = request_body.get('total_xp')
            optimization_result = request_body.get('optimization_result')
            
            request = UpdateUserStatsRequest(
                user_id=user_id,
                success_rate=success_rate,
                total_optimizations=total_optimizations,
                successful_optimizations=successful_optimizations,
                current_streak=current_streak,
                level=level,
                total_xp=total_xp,
                optimization_result=optimization_result
            )
            
            request.validate()
            response = self.leaderboard_service.update_user_stats(request)
            
            if response.success:
                return {
                    "status": "success",
                    "data": {
                        "user_id": response.user_id,
                        "new_rank": response.new_rank,
                        "previous_rank": response.previous_rank,
                        "rank_change": response.rank_change,
                        "new_streak": response.new_streak
                    },
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return self._error_response(400, response.error or "Failed to update user stats")
                
        except ValueError as e:
            return self._error_response(400, f"Invalid parameter: {str(e)}")
        except Exception as e:
            return self._error_response(500, f"Internal server error: {str(e)}")
    
    # ========== Social Features Endpoints ==========
    
    def get_social_comparison(self, user_id: str, query_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        GET /api/leaderboard/users/{user_id}/social-comparison
        
        Query Parameters:
        - comparison_type: string (friends, team, following, global) - default: friends
        - metric: string (success_rate, total_optimizations, level, current_streak) - default: success_rate
        - period: string - default: all_time
        """
        try:
            if not user_id:
                return self._error_response(400, "User ID is required")
            
            comparison_type = query_params.get('comparison_type', 'friends')
            metric = query_params.get('metric', 'success_rate')
            period = query_params.get('period', 'all_time')
            
            request = GetSocialComparisonRequest(
                user_id=user_id,
                comparison_type=comparison_type,
                metric=metric,
                period=period
            )
            
            request.validate()
            response = self.leaderboard_service.get_social_comparison(request)
            
            if response.success:
                return {
                    "status": "success",
                    "data": {
                        "user_id": response.user_id,
                        "comparison_type": response.comparison_type,
                        "metric": response.metric,
                        "comparison_data": response.comparison_data
                    },
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return self._error_response(404, response.error or "Social data not found")
                
        except ValueError as e:
            return self._error_response(400, f"Invalid parameter: {str(e)}")
        except Exception as e:
            return self._error_response(500, f"Internal server error: {str(e)}")
    
    # ========== Team Management Endpoints ==========
    
    def join_team(self, user_id: str, request_body: Dict[str, Any]) -> Dict[str, Any]:
        """
        POST /api/leaderboard/users/{user_id}/team/join
        
        Request Body:
        {
            "team_name": string
        }
        """
        try:
            if not user_id:
                return self._error_response(400, "User ID is required")
            
            team_name = request_body.get('team_name')
            if not team_name:
                return self._error_response(400, "Team name is required")
            
            if self.social_integration_service:
                result = self.social_integration_service.manage_team_membership(
                    user_id=user_id,
                    team_name=team_name,
                    action="join"
                )
                
                if result["success"]:
                    return {
                        "status": "success",
                        "data": result["updates"],
                        "message": f"Successfully joined team: {team_name}",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                else:
                    return self._error_response(400, result.get("error", "Failed to join team"))
            else:
                return self._error_response(501, "Team management not available")
                
        except Exception as e:
            return self._error_response(500, f"Internal server error: {str(e)}")
    
    def leave_team(self, user_id: str) -> Dict[str, Any]:
        """
        POST /api/leaderboard/users/{user_id}/team/leave
        """
        try:
            if not user_id:
                return self._error_response(400, "User ID is required")
            
            if self.social_integration_service:
                result = self.social_integration_service.manage_team_membership(
                    user_id=user_id,
                    team_name="",  # Will be ignored for leave action
                    action="leave"
                )
                
                if result["success"]:
                    return {
                        "status": "success",
                        "data": result["updates"],
                        "message": "Successfully left team",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                else:
                    return self._error_response(400, result.get("error", "Failed to leave team"))
            else:
                return self._error_response(501, "Team management not available")
                
        except Exception as e:
            return self._error_response(500, f"Internal server error: {str(e)}")
    
    # ========== Historical Data Endpoints ==========
    
    def create_snapshot(self, request_body: Dict[str, Any]) -> Dict[str, Any]:
        """
        POST /api/leaderboard/snapshots
        
        Request Body:
        {
            "period": string,
            "snapshot_date": string (ISO format),
            "category": string (optional)
        }
        """
        try:
            period = request_body.get('period')
            snapshot_date = request_body.get('snapshot_date')
            category = request_body.get('category')
            
            if not period:
                return self._error_response(400, "Period is required")
            if not snapshot_date:
                return self._error_response(400, "Snapshot date is required")
            
            request = CreateHistoricalSnapshotRequest(
                period=period,
                snapshot_date=snapshot_date,
                category=category
            )
            
            request.validate()
            response = self.leaderboard_service.create_historical_snapshot(request)
            
            if response.success:
                return {
                    "status": "success",
                    "data": {
                        "snapshot_id": response.snapshot_id,
                        "period": response.period,
                        "snapshot_date": response.snapshot_date,
                        "participants_count": response.participants_count
                    },
                    "message": "Historical snapshot created successfully",
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return self._error_response(400, response.error or "Failed to create snapshot")
                
        except ValueError as e:
            return self._error_response(400, f"Invalid parameter: {str(e)}")
        except Exception as e:
            return self._error_response(500, f"Internal server error: {str(e)}")
    
    def get_snapshot(self, snapshot_id: str) -> Dict[str, Any]:
        """
        GET /api/leaderboard/snapshots/{snapshot_id}
        """
        try:
            if not snapshot_id:
                return self._error_response(400, "Snapshot ID is required")
            
            snapshot = self.leaderboard_service.get_historical_snapshot(snapshot_id)
            
            if snapshot:
                return {
                    "status": "success",
                    "data": snapshot,
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return self._error_response(404, "Snapshot not found")
                
        except Exception as e:
            return self._error_response(500, f"Internal server error: {str(e)}")
    
    # ========== Cross-Module Integration Endpoints ==========
    
    def process_optimization(self, user_id: str, request_body: Dict[str, Any]) -> Dict[str, Any]:
        """
        POST /api/leaderboard/users/{user_id}/optimization
        
        Process a complete optimization workflow across all modules.
        
        Request Body:
        {
            "optimization_successful": boolean,
            "xp_gained": int (optional, default: 30),
            "difficulty_level": string (optional, default: "medium")
        }
        """
        try:
            if not user_id:
                return self._error_response(400, "User ID is required")
            
            optimization_successful = request_body.get('optimization_successful')
            if optimization_successful is None:
                return self._error_response(400, "optimization_successful is required")
            
            xp_gained = request_body.get('xp_gained', 30)
            difficulty_level = request_body.get('difficulty_level', 'medium')
            
            if self.social_integration_service:
                result = self.social_integration_service.process_optimization_completion(
                    user_id=user_id,
                    optimization_successful=optimization_successful,
                    xp_gained=xp_gained,
                    difficulty_level=difficulty_level
                )
                
                if result["success"]:
                    return {
                        "status": "success",
                        "data": result,
                        "message": "Optimization processed successfully",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                else:
                    return self._error_response(400, result.get("error", "Failed to process optimization"))
            else:
                return self._error_response(501, "Cross-module integration not available")
                
        except Exception as e:
            return self._error_response(500, f"Internal server error: {str(e)}")
    
    def get_comprehensive_profile(self, user_id: str) -> Dict[str, Any]:
        """
        GET /api/leaderboard/users/{user_id}/comprehensive-profile
        
        Get complete user profile across all modules.
        """
        try:
            if not user_id:
                return self._error_response(400, "User ID is required")
            
            if self.social_integration_service:
                profile = self.social_integration_service.get_comprehensive_user_profile(user_id)
                
                if profile["success"]:
                    return {
                        "status": "success",
                        "data": profile["data"],
                        "timestamp": datetime.utcnow().isoformat()
                    }
                else:
                    return self._error_response(404, profile.get("error", "User profile not found"))
            else:
                return self._error_response(501, "Comprehensive profiles not available")
                
        except Exception as e:
            return self._error_response(500, f"Internal server error: {str(e)}")
    
    # ========== Utility Methods ==========
    
    def _error_response(self, status_code: int, message: str) -> Dict[str, Any]:
        """Create standardized error response"""
        return {
            "status": "error",
            "error": {
                "code": status_code,
                "message": message
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_api_documentation(self) -> Dict[str, Any]:
        """
        GET /api/leaderboard/docs
        
        Get API documentation for all endpoints.
        """
        return {
            "status": "success",
            "data": {
                "title": "Leaderboard & Social Features API",
                "version": "1.0.0",
                "description": "RESTful API for leaderboard, social, and team management features",
                "endpoints": {
                    "GET /api/leaderboard": "Get leaderboard with filtering options",
                    "GET /api/leaderboard/users/{user_id}/ranking": "Get user ranking details",
                    "PUT /api/leaderboard/users/{user_id}/stats": "Update user statistics",
                    "GET /api/leaderboard/users/{user_id}/social-comparison": "Get social comparison data",
                    "POST /api/leaderboard/users/{user_id}/team/join": "Join a team",
                    "POST /api/leaderboard/users/{user_id}/team/leave": "Leave current team",
                    "POST /api/leaderboard/snapshots": "Create historical snapshot",
                    "GET /api/leaderboard/snapshots/{snapshot_id}": "Get historical snapshot",
                    "POST /api/leaderboard/users/{user_id}/optimization": "Process optimization workflow",
                    "GET /api/leaderboard/users/{user_id}/comprehensive-profile": "Get complete user profile",
                    "GET /api/leaderboard/docs": "Get API documentation"
                },
                "base_url": "/api/leaderboard",
                "content_type": "application/json"
            },
            "timestamp": datetime.utcnow().isoformat()
        }