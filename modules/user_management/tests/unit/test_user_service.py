import pytest
import json
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import Mock, patch
import sys
import os

# Add the module path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from application.services.user_service import UserService
from domain.entities.user import User
from domain.value_objects.gamification_stats import GamificationStats
from domain.value_objects.user_profile import UserProfile
from application.dtos.user_requests import CreateUserRequest, GainExperienceRequest
from infrastructure.repositories.user_repository import UserRepository

class TestUserService:
    """
    TDD Cycle 10: User Management & Gamification System
    Following Kent Beck's TDD principles - testing behaviors, not implementation
    """
    
    @pytest.fixture
    def test_data(self):
        """Load test data for user management tests"""
        test_data_path = Path(__file__).parent.parent.parent.parent.parent / "tests" / "test_data" / "gamification_test_data.json"
        with open(test_data_path, 'r') as f:
            return json.load(f)
    
    @pytest.fixture
    def user_repository_mock(self):
        return Mock(spec=UserRepository)
    
    @pytest.fixture
    def user_service(self, user_repository_mock):
        return UserService(user_repository_mock)

    # RED PHASE: Test that will fail initially
    def test_create_user_with_valid_input_initializes_gamification_stats(self, user_service, user_repository_mock, test_data):
        """
        Behavior: When creating a new user, the system should initialize their gamification stats
        Expected: User created with level 1, 0 XP, and empty optimization stats
        """
        # Arrange
        create_request = CreateUserRequest(
            email="new.user@example.com",
            name="New User", 
            role="developer",
            team="backend",
            company="TechCorp"
        )
        
        expected_user = User(
            id="generated_id",
            profile=UserProfile(
                email="new.user@example.com",
                name="New User",
                role="developer", 
                team="backend",
                company="TechCorp"
            ),
            gamification=GamificationStats(
                level=1,
                experience_points=0,
                total_optimizations=0,
                successful_optimizations=0,
                win_streak=0
            )
        )
        
        user_repository_mock.save.return_value = expected_user
        
        # Act
        result = user_service.create_user(create_request)
        
        # Assert
        assert result.success is True
        assert result.user.gamification.level == 1
        assert result.user.gamification.experience_points == 0
        assert result.user.gamification.total_optimizations == 0
        assert result.user.gamification.successful_optimizations == 0
        assert result.user.gamification.win_streak == 0
        assert result.user.profile.email == "new.user@example.com"
        user_repository_mock.save.assert_called_once()

    def test_gain_experience_without_level_up_updates_xp_correctly(self, user_service, user_repository_mock, test_data):
        """
        Behavior: When user gains XP but doesn't reach next level threshold, only XP should increase
        Expected: XP increased, level unchanged, correct XP until next level calculated
        """
        # Arrange
        existing_user = User(
            id="user_001",
            profile=UserProfile(email="alex.chen@example.com", name="Alex Chen", role="developer", team="backend", company="TechCorp"),
            gamification=GamificationStats(level=12, experience_points=2847, total_optimizations=156, successful_optimizations=142, win_streak=7)
        )
        
        user_repository_mock.get_by_id.return_value = existing_user
        
        gain_request = GainExperienceRequest(
            user_id="user_001",
            points=150,
            reason="successful_optimization"
        )
        
        # Act
        result = user_service.gain_experience(gain_request)
        
        # Assert
        assert result.success is True
        assert result.level_up is False
        assert result.new_xp == 2997  # 2847 + 150
        assert result.xp_until_next == 3  # 3000 - 2997
        assert result.old_level == 12
        assert result.new_level == 12
        user_repository_mock.save.assert_called_once()

    def test_gain_experience_with_level_up_updates_level_and_carries_over_xp(self, user_service, user_repository_mock, test_data):
        """
        Behavior: When user gains XP that exceeds level threshold, level up occurs with XP carryover
        Expected: Level incremented, excess XP carried to next level, proper calculations
        """
        # Arrange
        existing_user = User(
            id="user_001",
            profile=UserProfile(email="alex.chen@example.com", name="Alex Chen", role="developer", team="backend", company="TechCorp"),
            gamification=GamificationStats(level=12, experience_points=2847, total_optimizations=156, successful_optimizations=142, win_streak=7)
        )
        
        user_repository_mock.get_by_id.return_value = existing_user
        
        gain_request = GainExperienceRequest(
            user_id="user_001",
            points=200,  # This should cause level up: 2847 + 200 = 3047, threshold is 3000
            reason="achievement_unlock"
        )
        
        # Act  
        result = user_service.gain_experience(gain_request)
        
        # Assert
        assert result.success is True
        assert result.level_up is True
        assert result.old_level == 12
        assert result.new_level == 13
        assert result.new_xp == 47  # 3047 - 3000 (carried over to next level)
        assert result.xp_until_next == 953  # Assuming level 13 requires 1000 XP total
        user_repository_mock.save.assert_called_once()

    def test_track_win_streak_increments_on_success(self, user_service, user_repository_mock):
        """
        Behavior: When user has successful optimization, win streak should increment
        Expected: Win streak increased by 1
        """
        # Arrange
        existing_user = User(
            id="user_001",
            profile=UserProfile(email="alex.chen@example.com", name="Alex Chen", role="developer", team="backend", company="TechCorp"),
            gamification=GamificationStats(level=12, experience_points=2847, total_optimizations=156, successful_optimizations=142, win_streak=7)
        )
        
        user_repository_mock.get_by_id.return_value = existing_user
        
        # Act
        result = user_service.track_optimization_result("user_001", success=True)
        
        # Assert
        assert result.success is True
        assert result.new_win_streak == 8
        assert result.total_optimizations == 157
        assert result.successful_optimizations == 143
        user_repository_mock.save.assert_called_once()

    def test_track_win_streak_resets_on_failure(self, user_service, user_repository_mock):
        """
        Behavior: When user has failed optimization, win streak should reset to 0
        Expected: Win streak reset, totals updated correctly
        """
        # Arrange
        existing_user = User(
            id="user_001",
            profile=UserProfile(email="alex.chen@example.com", name="Alex Chen", role="developer", team="backend", company="TechCorp"),
            gamification=GamificationStats(level=12, experience_points=2847, total_optimizations=156, successful_optimizations=142, win_streak=7)
        )
        
        user_repository_mock.get_by_id.return_value = existing_user
        
        # Act
        result = user_service.track_optimization_result("user_001", success=False)
        
        # Assert
        assert result.success is True
        assert result.new_win_streak == 0
        assert result.total_optimizations == 157
        assert result.successful_optimizations == 142  # No change on failure
        user_repository_mock.save.assert_called_once()

    def test_get_user_profile_returns_complete_user_stats(self, user_service, user_repository_mock, test_data):
        """
        Behavior: When requesting user profile, system should return complete user information
        Expected: Full user profile with gamification stats and derived metrics
        """
        # Arrange
        test_user_data = test_data["users"][0]  # Alex Chen
        existing_user = User(
            id=test_user_data["id"],
            profile=UserProfile(**test_user_data["profile"]),
            gamification=GamificationStats(**test_user_data["gamification"])
        )
        
        user_repository_mock.get_by_id.return_value = existing_user
        
        # Act
        result = user_service.get_user_profile("user_001")
        
        # Assert
        assert result.success is True
        assert result.user.id == "user_001"
        assert result.user.profile.name == "Alex Chen"
        assert result.user.gamification.level == 12
        assert result.user.gamification.experience_points == 2847
        assert result.success_rate == pytest.approx(0.910, rel=1e-3)  # 142/156
        assert result.current_level_title == "Context Master"

    def test_create_user_with_invalid_email_returns_error(self, user_service, user_repository_mock):
        """
        Behavior: When creating user with invalid email, system should return validation error
        Expected: Error result with appropriate message
        """
        # Arrange
        create_request = CreateUserRequest(
            email="invalid-email",  # Invalid email format
            name="Test User",
            role="developer",
            team="backend", 
            company="TechCorp"
        )
        
        # Act
        result = user_service.create_user(create_request)
        
        # Assert
        assert result.success is False
        assert "email" in result.error_message.lower()
        user_repository_mock.save.assert_not_called()

    def test_gain_experience_for_nonexistent_user_returns_error(self, user_service, user_repository_mock):
        """
        Behavior: When trying to gain XP for non-existent user, system should return error
        Expected: Error result indicating user not found
        """
        # Arrange
        user_repository_mock.get_by_id.return_value = None
        
        gain_request = GainExperienceRequest(
            user_id="nonexistent_user",
            points=100,
            reason="test"
        )
        
        # Act
        result = user_service.gain_experience(gain_request)
        
        # Assert
        assert result.success is False
        assert "not found" in result.error_message.lower()
        user_repository_mock.save.assert_not_called()