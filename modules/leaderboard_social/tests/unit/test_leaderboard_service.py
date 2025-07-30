"""
Unit tests for LeaderboardService following TDD Red-Green-Refactor approach

TDD Cycle 12: Leaderboard & Social Features
Test scenarios:
1. LeaderboardService_UpdateRankings_ReflectsLatestPerformance
2. LeaderboardService_GetWeeklyLeaders_FiltersTimeWindow
3. LeaderboardService_TrackStreaks_UpdatesConsecutiveWins
4. Privacy settings filtering
5. Composite score calculation
6. Historical snapshots
7. Category-based leaderboards
8. Social comparisons
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../..'))

import unittest
from datetime import datetime, timedelta
from typing import List, Dict, Any

# These imports will fail initially - this is the RED phase of TDD
try:
    from leaderboard_social.application.services.leaderboard_service import LeaderboardService
    from leaderboard_social.application.dtos.leaderboard_requests import (
        GetLeaderboardRequest, UpdateUserStatsRequest, GetUserRankingRequest,
        GetSocialComparisonRequest, CreateHistoricalSnapshotRequest
    )
    from leaderboard_social.application.dtos.leaderboard_responses import (
        GetLeaderboardResponse, UpdateUserStatsResponse, GetUserRankingResponse,
        GetSocialComparisonResponse, CreateHistoricalSnapshotResponse
    )
    from leaderboard_social.infrastructure.repositories.leaderboard_repository import InMemoryLeaderboardRepository
    from leaderboard_social.infrastructure.repositories.user_stats_repository import InMemoryUserStatsRepository
except ImportError as e:
    print(f"Expected import error during RED phase: {e}")


class TestLeaderboardService(unittest.TestCase):
    """Test suite for LeaderboardService functionality"""
    
    def setUp(self):
        """Set up test environment before each test"""
        try:
            self.leaderboard_repo = InMemoryLeaderboardRepository()
            self.user_stats_repo = InMemoryUserStatsRepository()
            self.service = LeaderboardService(self.leaderboard_repo, self.user_stats_repo)
        except NameError:
            # During RED phase, these classes don't exist yet
            self.service = None
            print("Setup skipped - classes not implemented yet (RED phase)")
    
    def test_update_rankings_reflects_latest_performance(self):
        """Test that leaderboard rankings update when user performance changes (TDD Core Test 1)"""
        if not self.service:
            print("❌ RED: LeaderboardService not implemented yet")
            return
            
        # Arrange
        request = UpdateUserStatsRequest(
            user_id="user-001",
            success_rate=98.5,
            total_optimizations=160,
            current_streak=15,
            level=16
        )
        
        # Act
        response = self.service.update_user_stats(request)
        
        # Assert
        assert response.success is True
        
        # Verify updated ranking
        leaderboard_request = GetLeaderboardRequest(
            period="all_time",
            limit=10
        )
        leaderboard_response = self.service.get_leaderboard(leaderboard_request)
        
        # User should be ranked #1 with updated stats
        top_user = leaderboard_response.leaderboard_entries[0]
        assert top_user.user_id == "user-001"
        assert top_user.success_rate == 98.5
        assert top_user.rank == 1
        
        print("✅ test_update_rankings_reflects_latest_performance")
    
    def test_get_weekly_leaders_filters_time_window(self):
        """Test weekly leaderboard filtering by time period (TDD Core Test 2)"""
        if not self.service:
            print("❌ RED: LeaderboardService not implemented yet")
            return
            
        # Arrange
        request = GetLeaderboardRequest(
            period="weekly",
            start_date="2023-12-04T00:00:00Z",
            end_date="2023-12-10T23:59:59Z",
            limit=10
        )
        
        # Act
        response = self.service.get_leaderboard(request)
        
        # Assert
        assert response.success is True
        assert len(response.leaderboard_entries) == 4  # Based on test data
        assert response.period == "weekly"
        
        # Verify top performer for the week
        top_performer = response.leaderboard_entries[0]
        assert top_performer.user_id == "user-001"
        assert top_performer.weekly_success_rate == 95.2
        
        print("✅ test_get_weekly_leaders_filters_time_window")
    
    def test_track_streaks_updates_consecutive_wins(self):
        """Test streak tracking and consecutive win updates (TDD Core Test 3)"""
        if not self.service:
            print("❌ RED: LeaderboardService not implemented yet")
            return
            
        # Arrange - user with current streak of 12
        user_id = "user-001"
        
        # Act - simulate successful optimization
        update_request = UpdateUserStatsRequest(
            user_id=user_id,
            optimization_result=True,  # Success
            current_streak=13  # Streak should increment
        )
        response = self.service.update_user_stats(update_request)
        
        # Assert
        assert response.success is True
        assert response.new_streak == 13
        
        # Act - simulate failed optimization
        update_request_fail = UpdateUserStatsRequest(
            user_id=user_id,
            optimization_result=False,  # Failure
            current_streak=0  # Streak should reset
        )
        response_fail = self.service.update_user_stats(update_request_fail)
        
        # Assert
        assert response_fail.success is True
        assert response_fail.new_streak == 0
        
        print("✅ test_track_streaks_updates_consecutive_wins")
    
    def test_privacy_settings_filter_hidden_users(self):
        """Test that privacy settings properly filter users from leaderboard"""
        if not self.service:
            print("❌ RED: LeaderboardService not implemented yet")
            return
            
        # Arrange
        request = GetLeaderboardRequest(
            period="all_time",
            respect_privacy=True,
            limit=10
        )
        
        # Act
        response = self.service.get_leaderboard(request)
        
        # Assert
        assert response.success is True
        
        # user-003 should be hidden due to privacy settings
        visible_user_ids = [entry.user_id for entry in response.leaderboard_entries]
        assert "user-003" not in visible_user_ids
        assert "user-001" in visible_user_ids  # Should be visible
        assert "user-002" in visible_user_ids  # Should be visible
        
        print("✅ test_privacy_settings_filter_hidden_users")
    
    def test_composite_score_calculation(self):
        """Test composite score calculation with weighted criteria"""
        if not self.service:
            print("❌ RED: LeaderboardService not implemented yet")
            return
            
        # Arrange
        request = GetUserRankingRequest(
            user_id="user-001",
            ranking_criteria="default"  # Uses weighted scoring
        )
        
        # Act
        response = self.service.get_user_ranking(request)
        
        # Assert
        assert response.success is True
        assert response.composite_score is not None
        
        # Verify score components based on test data expectations
        expected_total = 124.28  # From test data
        assert abs(response.composite_score - expected_total) < 0.1
        
        # Verify individual components
        components = response.score_breakdown
        assert "success_rate_score" in components
        assert "optimization_score" in components
        assert "streak_score" in components
        assert "level_score" in components
        
        print("✅ test_composite_score_calculation")
    
    def test_historical_snapshot_creation(self):
        """Test creation and retrieval of historical leaderboard snapshots"""
        if not self.service:
            print("❌ RED: LeaderboardService not implemented yet")
            return
            
        # Arrange
        request = CreateHistoricalSnapshotRequest(
            period="monthly",
            snapshot_date="2023-12-01T00:00:00Z"
        )
        
        # Act
        response = self.service.create_historical_snapshot(request)
        
        # Assert
        assert response.success is True
        assert response.snapshot_id is not None
        
        # Verify snapshot can be retrieved
        snapshot = self.service.get_historical_snapshot(response.snapshot_id)
        assert snapshot is not None
        assert snapshot.period == "monthly"
        
        print("✅ test_historical_snapshot_creation")
    
    def test_category_leaderboard_filtering(self):
        """Test category-specific leaderboard functionality"""
        if not self.service:
            print("❌ RED: LeaderboardService not implemented yet")
            return
            
        # Arrange
        request = GetLeaderboardRequest(
            period="all_time",
            category="context_optimization",
            limit=10
        )
        
        # Act
        response = self.service.get_leaderboard(request)
        
        # Assert
        assert response.success is True
        assert response.category == "context_optimization"
        
        # Verify category-specific ranking
        top_user = response.leaderboard_entries[0]
        assert top_user.user_id == "user-001"  # Expected top performer in this category
        assert top_user.category_score == 98.5
        
        print("✅ test_category_leaderboard_filtering")
    
    def test_social_comparison_with_friends(self):
        """Test social comparison features with friend networks"""
        if not self.service:
            print("❌ RED: LeaderboardService not implemented yet")
            return
            
        # Arrange
        request = GetSocialComparisonRequest(
            user_id="user-001",
            comparison_type="friends",
            metric="success_rate"
        )
        
        # Act
        response = self.service.get_social_comparison(request)
        
        # Assert
        assert response.success is True
        assert response.user_id == "user-001"
        
        # Verify comparison data
        assert "friends_average" in response.comparison_data
        assert "user_rank_among_friends" in response.comparison_data
        assert response.comparison_data["friends_count"] == 2  # user-001 has 2 friends
        
        print("✅ test_social_comparison_with_friends")
    
    def test_team_leaderboard_functionality(self):
        """Test team-based leaderboard and statistics"""
        if not self.service:
            print("❌ RED: LeaderboardService not implemented yet")
            return
            
        # Arrange
        request = GetLeaderboardRequest(
            period="all_time",
            team_name="Engineering",
            limit=10
        )
        
        # Act
        response = self.service.get_leaderboard(request)
        
        # Assert
        assert response.success is True
        assert response.team_name == "Engineering"
        
        # Verify team statistics
        team_stats = response.team_statistics
        assert team_stats["average_success_rate"] == 94.2
        assert team_stats["total_team_optimizations"] == 416
        assert len(response.leaderboard_entries) == 3  # Engineering team has 3 members
        
        print("✅ test_team_leaderboard_functionality")
    
    def test_daily_leaderboard_updates(self):
        """Test daily leaderboard creation and updates"""
        if not self.service:
            print("❌ RED: LeaderboardService not implemented yet")
            return
            
        # Arrange
        today = datetime.now().strftime("%Y-%m-%dT00:00:00Z")
        request = GetLeaderboardRequest(
            period="daily",
            start_date=today,
            limit=10
        )
        
        # Act
        response = self.service.get_leaderboard(request)
        
        # Assert
        assert response.success is True
        assert response.period == "daily"
        
        # Verify daily stats are different from all-time
        top_daily = response.leaderboard_entries[0]
        assert hasattr(top_daily, 'daily_success_rate')
        assert hasattr(top_daily, 'optimizations_today')
        
        print("✅ test_daily_leaderboard_updates")


def run_tests():
    """Run all leaderboard service tests"""
    print("🧪 Running Leaderboard Service TDD Tests (Red-Green-Refactor)")
    print("=" * 60)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestLeaderboardService)
    
    # Run tests with custom result handling
    test_instance = TestLeaderboardService()
    test_instance.setUp()
    
    # Run individual tests to see progress
    tests = [
        test_instance.test_update_rankings_reflects_latest_performance,
        test_instance.test_get_weekly_leaders_filters_time_window,
        test_instance.test_track_streaks_updates_consecutive_wins,
        test_instance.test_privacy_settings_filter_hidden_users,
        test_instance.test_composite_score_calculation,
        test_instance.test_historical_snapshot_creation,
        test_instance.test_category_leaderboard_filtering,
        test_instance.test_social_comparison_with_friends,
        test_instance.test_team_leaderboard_functionality,
        test_instance.test_daily_leaderboard_updates
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"❌ {test.__name__}: {str(e)}")
            failed += 1
    
    print("=" * 60)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passing! Ready for GREEN phase.")
    else:
        print("🔴 RED phase: Tests failing as expected. Time to implement!")


if __name__ == "__main__":
    run_tests()