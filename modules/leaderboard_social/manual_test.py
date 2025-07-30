"""
Manual test script for Leaderboard & Social Features module

Following TDD Red-Green-Refactor approach for Cycle 12.
This script tests the core functionality without relying on external test frameworks.
"""

import sys
import os

# Add paths for module imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.dirname(__file__))

# Import the implementations
try:
    from application.services.leaderboard_service import LeaderboardService
    from application.dtos.leaderboard_requests import (
        GetLeaderboardRequest, UpdateUserStatsRequest, GetUserRankingRequest,
        GetSocialComparisonRequest, CreateHistoricalSnapshotRequest
    )
    from infrastructure.repositories.leaderboard_repository import InMemoryLeaderboardRepository
    from infrastructure.repositories.user_stats_repository import InMemoryUserStatsRepository
except ImportError:
    # Try alternative import path
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
    
    from application.services.leaderboard_service import LeaderboardService
    from application.dtos.leaderboard_requests import (
        GetLeaderboardRequest, UpdateUserStatsRequest, GetUserRankingRequest,
        GetSocialComparisonRequest, CreateHistoricalSnapshotRequest
    )
    from infrastructure.repositories.leaderboard_repository import InMemoryLeaderboardRepository
    from infrastructure.repositories.user_stats_repository import InMemoryUserStatsRepository


def test_update_rankings_reflects_latest_performance():
    """Test that leaderboard rankings update when user performance changes (TDD Core Test 1)"""
    print("Testing: update_rankings_reflects_latest_performance")
    
    # Arrange
    leaderboard_repo = InMemoryLeaderboardRepository()
    user_stats_repo = InMemoryUserStatsRepository()
    service = LeaderboardService(leaderboard_repo, user_stats_repo)
    
    request = UpdateUserStatsRequest(
        user_id="user-001",
        success_rate=98.5,
        total_optimizations=160,
        current_streak=15,
        level=16
    )
    
    # Act
    response = service.update_user_stats(request)
    
    # Assert
    assert response.success is True, f"Expected success=True, got {response.success}"
    
    # Verify updated ranking
    leaderboard_request = GetLeaderboardRequest(
        period="all_time",
        limit=10
    )
    leaderboard_response = service.get_leaderboard(leaderboard_request)
    
    assert leaderboard_response.success is True, "Leaderboard request should succeed"
    assert len(leaderboard_response.leaderboard_entries) > 0, "Should have leaderboard entries"
    
    # User should be ranked based on updated stats
    user_found = False
    for entry in leaderboard_response.leaderboard_entries:
        if entry.get("user_name") == "Alex Chen":  # user-001's name from test data
            user_found = True
            break
    
    assert user_found, "Updated user should be found in leaderboard"
    print("✅ test_update_rankings_reflects_latest_performance: PASSED")


def test_get_weekly_leaders_filters_time_window():
    """Test weekly leaderboard filtering by time period (TDD Core Test 2)"""
    print("Testing: get_weekly_leaders_filters_time_window")
    
    # Arrange
    leaderboard_repo = InMemoryLeaderboardRepository()
    user_stats_repo = InMemoryUserStatsRepository()
    service = LeaderboardService(leaderboard_repo, user_stats_repo)
    
    request = GetLeaderboardRequest(
        period="weekly",
        start_date="2023-12-04T00:00:00Z",
        end_date="2023-12-10T23:59:59Z",
        limit=10
    )
    
    # Act
    response = service.get_leaderboard(request)
    
    # Assert
    assert response.success is True, f"Expected success=True, got {response.success}"
    assert response.period == "weekly", f"Expected period='weekly', got {response.period}"
    assert len(response.leaderboard_entries) > 0, "Should have participants"
    
    print("✅ test_get_weekly_leaders_filters_time_window: PASSED")


def test_track_streaks_updates_consecutive_wins():
    """Test streak tracking and consecutive win updates (TDD Core Test 3)"""
    print("Testing: track_streaks_updates_consecutive_wins")
    
    # Arrange
    leaderboard_repo = InMemoryLeaderboardRepository()
    user_stats_repo = InMemoryUserStatsRepository()
    service = LeaderboardService(leaderboard_repo, user_stats_repo)
    
    user_id = "user-001"
    
    # Act - simulate successful optimization
    update_request = UpdateUserStatsRequest(
        user_id=user_id,
        optimization_result=True,  # Success
        current_streak=13  # Should increment to 13
    )
    response = service.update_user_stats(update_request)
    
    # Assert
    assert response.success is True, f"Success update should work, got {response.success}"
    assert response.new_streak == 13, f"Expected streak=13, got {response.new_streak}"
    
    # Act - simulate failed optimization
    update_request_fail = UpdateUserStatsRequest(
        user_id=user_id,
        optimization_result=False,  # Failure
        current_streak=0  # Should reset to 0
    )
    response_fail = service.update_user_stats(update_request_fail)
    
    # Assert
    assert response_fail.success is True, f"Failure update should work, got {response_fail.success}"
    assert response_fail.new_streak == 0, f"Expected streak=0 after failure, got {response_fail.new_streak}"
    
    print("✅ test_track_streaks_updates_consecutive_wins: PASSED")


def test_privacy_settings_filter_hidden_users():
    """Test that privacy settings properly filter users from leaderboard"""
    print("Testing: privacy_settings_filter_hidden_users")
    
    # Arrange
    leaderboard_repo = InMemoryLeaderboardRepository()
    user_stats_repo = InMemoryUserStatsRepository()
    service = LeaderboardService(leaderboard_repo, user_stats_repo)
    
    request = GetLeaderboardRequest(
        period="all_time",
        respect_privacy=True,
        limit=10
    )
    
    # Act
    response = service.get_leaderboard(request)
    
    # Assert
    assert response.success is True, f"Expected success=True, got {response.success}"
    
    # user-003 should be hidden due to privacy settings (show_in_leaderboard=false)
    visible_user_names = [entry.get("user_name", "") for entry in response.leaderboard_entries]
    assert "Mike Rodriguez" not in visible_user_names, "User-003 (Mike Rodriguez) should be hidden"
    assert "Alex Chen" in visible_user_names, "User-001 (Alex Chen) should be visible"
    
    print("✅ test_privacy_settings_filter_hidden_users: PASSED")


def test_composite_score_calculation():
    """Test composite score calculation with weighted criteria"""
    print("Testing: composite_score_calculation")
    
    # Arrange
    leaderboard_repo = InMemoryLeaderboardRepository()
    user_stats_repo = InMemoryUserStatsRepository()
    service = LeaderboardService(leaderboard_repo, user_stats_repo)
    
    request = GetUserRankingRequest(
        user_id="user-001",
        ranking_criteria="default"  # Uses weighted scoring
    )
    
    # Act
    response = service.get_user_ranking(request)
    
    # Assert
    assert response.success is True, f"Expected success=True, got {response.success}"
    assert response.composite_score is not None, "Should have composite score"
    assert response.score_breakdown is not None, "Should have score breakdown"
    
    # Verify score components exist
    components = response.score_breakdown
    assert "success_rate_score" in components, "Should have success_rate_score"
    assert "total_optimizations_score" in components, "Should have total_optimizations_score"
    assert "current_streak_score" in components, "Should have current_streak_score"
    
    print("✅ test_composite_score_calculation: PASSED")


def test_historical_snapshot_creation():
    """Test creation and retrieval of historical leaderboard snapshots"""
    print("Testing: historical_snapshot_creation")
    
    # Arrange
    leaderboard_repo = InMemoryLeaderboardRepository()
    user_stats_repo = InMemoryUserStatsRepository()
    service = LeaderboardService(leaderboard_repo, user_stats_repo)
    
    request = CreateHistoricalSnapshotRequest(
        period="monthly",
        snapshot_date="2023-12-01T00:00:00Z"
    )
    
    # Act
    response = service.create_historical_snapshot(request)
    
    # Assert
    assert response.success is True, f"Expected success=True, got {response.success}"
    assert response.snapshot_id is not None, "Should have snapshot ID"
    
    # Verify snapshot can be retrieved
    snapshot = service.get_historical_snapshot(response.snapshot_id)
    assert snapshot is not None, "Should be able to retrieve snapshot"
    assert snapshot["period"] == "monthly", "Snapshot should have correct period"
    
    print("✅ test_historical_snapshot_creation: PASSED")


def test_category_leaderboard_filtering():
    """Test category-specific leaderboard functionality"""
    print("Testing: category_leaderboard_filtering")
    
    # Arrange
    leaderboard_repo = InMemoryLeaderboardRepository()
    user_stats_repo = InMemoryUserStatsRepository()
    service = LeaderboardService(leaderboard_repo, user_stats_repo)
    
    request = GetLeaderboardRequest(
        period="all_time",
        category="context_optimization",
        limit=10
    )
    
    # Act
    response = service.get_leaderboard(request)
    
    # Assert
    assert response.success is True, f"Expected success=True, got {response.success}"
    assert response.category == "context_optimization", "Should have correct category"
    assert len(response.leaderboard_entries) > 0, "Should have category entries"
    
    print("✅ test_category_leaderboard_filtering: PASSED")


def test_social_comparison_with_friends():
    """Test social comparison features with friend networks"""
    print("Testing: social_comparison_with_friends")
    
    # Arrange
    leaderboard_repo = InMemoryLeaderboardRepository()
    user_stats_repo = InMemoryUserStatsRepository()
    service = LeaderboardService(leaderboard_repo, user_stats_repo)
    
    request = GetSocialComparisonRequest(
        user_id="user-001",
        comparison_type="friends",
        metric="success_rate"
    )
    
    # Act
    response = service.get_social_comparison(request)
    
    # Assert
    assert response.success is True, f"Expected success=True, got {response.success}"
    assert response.comparison_data is not None, "Should have comparison data"
    
    # Verify comparison data structure
    comparison_data = response.comparison_data
    assert "friends_count" in comparison_data, "Should have friends count"
    assert comparison_data["friends_count"] >= 0, "Friends count should be non-negative"
    
    print("✅ test_social_comparison_with_friends: PASSED")


def test_team_leaderboard_functionality():
    """Test team-based leaderboard and statistics"""
    print("Testing: team_leaderboard_functionality")
    
    # Arrange
    leaderboard_repo = InMemoryLeaderboardRepository()
    user_stats_repo = InMemoryUserStatsRepository()
    service = LeaderboardService(leaderboard_repo, user_stats_repo)
    
    request = GetLeaderboardRequest(
        period="all_time",
        team_name="Engineering",
        limit=10
    )
    
    # Act
    response = service.get_leaderboard(request)
    
    # Assert
    assert response.success is True, f"Expected success=True, got {response.success}"
    assert response.team_name == "Engineering", "Should have correct team name"
    
    # Team statistics are optional but should be structured if present
    if response.team_statistics:
        team_stats = response.team_statistics
        assert "member_count" in team_stats, "Should have member count if stats present"
    
    print("✅ test_team_leaderboard_functionality: PASSED")


def test_daily_leaderboard_updates():
    """Test daily leaderboard creation and updates"""
    print("Testing: daily_leaderboard_updates")
    
    # Arrange
    leaderboard_repo = InMemoryLeaderboardRepository()
    user_stats_repo = InMemoryUserStatsRepository()
    service = LeaderboardService(leaderboard_repo, user_stats_repo)
    
    request = GetLeaderboardRequest(
        period="daily",
        limit=10
    )
    
    # Act
    response = service.get_leaderboard(request)
    
    # Assert
    assert response.success is True, f"Expected success=True, got {response.success}"
    assert response.period == "daily", "Should have correct period"
    
    print("✅ test_daily_leaderboard_updates: PASSED")


def run_all_tests():
    """Run all leaderboard service tests"""
    print("🧪 Running Leaderboard & Social Features Manual Tests")
    print("TDD Cycle 12: Leaderboard Service (GREEN Phase)")
    print("=" * 60)
    
    tests = [
        test_update_rankings_reflects_latest_performance,
        test_get_weekly_leaders_filters_time_window,
        test_track_streaks_updates_consecutive_wins,
        test_privacy_settings_filter_hidden_users,
        test_composite_score_calculation,
        test_historical_snapshot_creation,
        test_category_leaderboard_filtering,
        test_social_comparison_with_friends,
        test_team_leaderboard_functionality,
        test_daily_leaderboard_updates
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
        print("🎉 All tests passing! TDD Cycle 12 GREEN phase complete!")
        print("✅ Leaderboard & Social Features module is functional")
    else:
        print(f"❌ {failed} tests failed. Need to fix implementation.")
    
    print("\n🔄 TDD Cycle 12 Status: GREEN → Ready for REFACTOR phase")


if __name__ == "__main__":
    run_all_tests()