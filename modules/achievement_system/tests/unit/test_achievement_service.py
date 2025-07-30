import pytest
import json
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import Mock, patch
import sys
import os

# Add the module path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from application.services.achievement_service import AchievementService
from domain.entities.achievement import Achievement
from domain.entities.user_achievement import UserAchievement
from domain.value_objects.achievement_trigger import AchievementTrigger
from domain.value_objects.achievement_rarity import AchievementRarity
from application.dtos.achievement_requests import CheckAchievementUnlockRequest, GetUserAchievementsRequest
from infrastructure.repositories.achievement_repository import AchievementRepository
from infrastructure.repositories.user_achievement_repository import UserAchievementRepository

class TestAchievementService:
    """
    TDD Cycle 11: Achievement System
    Following Kent Beck's TDD principles - testing behaviors, not implementation
    """
    
    @pytest.fixture
    def test_data(self):
        """Load test data for achievement tests"""
        test_data_path = Path(__file__).parent.parent.parent.parent.parent / "tests" / "test_data" / "achievement_test_data.json"
        with open(test_data_path, 'r') as f:
            return json.load(f)
    
    @pytest.fixture
    def achievement_repository_mock(self):
        return Mock(spec=AchievementRepository)
    
    @pytest.fixture
    def user_achievement_repository_mock(self):
        return Mock(spec=UserAchievementRepository)
    
    @pytest.fixture
    def achievement_service(self, achievement_repository_mock, user_achievement_repository_mock):
        return AchievementService(achievement_repository_mock, user_achievement_repository_mock)

    # RED PHASE: Test that will fail initially
    def test_check_achievement_unlock_with_simple_trigger_unlocks_achievement(self, achievement_service, achievement_repository_mock, user_achievement_repository_mock, test_data):
        """
        Behavior: When user completes their first optimization, "First Steps" achievement should unlock
        Expected: Achievement unlocked, XP awarded, achievement saved to user's record
        """
        # Arrange
        first_steps_achievement = Achievement(
            id="achievement_001",
            name="First Steps",
            description="Complete your first context build optimization",
            rarity=AchievementRarity.COMMON,
            icon="target",
            xp_reward=50,
            trigger=AchievementTrigger(
                trigger_type="optimization_count",
                threshold=1
            ),
            category="getting_started"
        )
        
        achievement_repository_mock.get_all.return_value = [first_steps_achievement]
        user_achievement_repository_mock.get_user_achievements.return_value = []  # No previous achievements
        
        check_request = CheckAchievementUnlockRequest(
            user_id="user_001",
            event_type="optimization_completed",
            event_data={
                "success": True,
                "optimization_count": 1
            }
        )
        
        # Act
        result = achievement_service.check_achievement_unlock(check_request)
        
        # Assert
        assert result.success is True
        assert len(result.unlocked_achievements) == 1
        assert result.unlocked_achievements[0].id == "achievement_001"
        assert result.total_xp_awarded == 50
        user_achievement_repository_mock.save_user_achievement.assert_called_once()

    def test_check_achievement_unlock_with_complex_trigger_requires_multiple_conditions(self, achievement_service, achievement_repository_mock, user_achievement_repository_mock, test_data):
        """
        Behavior: When user has 90%+ success rate over 10+ optimizations, "Context Optimizer" achievement should unlock
        Expected: Achievement unlocked only when both conditions met
        """
        # Arrange
        context_optimizer_achievement = Achievement(
            id="achievement_002",
            name="Context Optimizer",
            description="Achieve 90%+ success rate over 10 optimizations",
            rarity=AchievementRarity.GOLD,
            icon="trophy",
            xp_reward=200,
            trigger=AchievementTrigger(
                trigger_type="success_rate",
                threshold=0.9,
                minimum_attempts=10
            ),
            category="performance"
        )
        
        achievement_repository_mock.get_all.return_value = [context_optimizer_achievement]
        user_achievement_repository_mock.get_user_achievements.return_value = []
        
        check_request = CheckAchievementUnlockRequest(
            user_id="user_001",
            event_type="optimization_completed",
            event_data={
                "success": True,
                "total_optimizations": 10,
                "successful_optimizations": 9,  # 90% success rate
                "success_rate": 0.9
            }
        )
        
        # Act
        result = achievement_service.check_achievement_unlock(check_request)
        
        # Assert
        assert result.success is True
        assert len(result.unlocked_achievements) == 1
        assert result.unlocked_achievements[0].id == "achievement_002"
        assert result.total_xp_awarded == 200
        user_achievement_repository_mock.save_user_achievement.assert_called_once()

    def test_check_achievement_unlock_with_insufficient_conditions_does_not_unlock(self, achievement_service, achievement_repository_mock, user_achievement_repository_mock):
        """
        Behavior: When user has good success rate but insufficient attempts, achievement should not unlock
        Expected: No achievements unlocked, progress tracked if applicable
        """
        # Arrange
        context_optimizer_achievement = Achievement(
            id="achievement_002",
            name="Context Optimizer",
            description="Achieve 90%+ success rate over 10 optimizations",
            rarity=AchievementRarity.GOLD,
            icon="trophy",
            xp_reward=200,
            trigger=AchievementTrigger(
                trigger_type="success_rate",
                threshold=0.9,
                minimum_attempts=10
            ),
            category="performance"
        )
        
        achievement_repository_mock.get_all.return_value = [context_optimizer_achievement]
        user_achievement_repository_mock.get_user_achievements.return_value = []
        
        check_request = CheckAchievementUnlockRequest(
            user_id="user_001",
            event_type="optimization_completed",
            event_data={
                "success": True,
                "total_optimizations": 5,  # Not enough attempts
                "successful_optimizations": 5,  # 100% success rate
                "success_rate": 1.0
            }
        )
        
        # Act
        result = achievement_service.check_achievement_unlock(check_request)
        
        # Assert
        assert result.success is True
        assert len(result.unlocked_achievements) == 0
        assert result.total_xp_awarded == 0
        # Progress should be tracked but no achievement saved
        user_achievement_repository_mock.save_user_achievement.assert_not_called()

    def test_check_achievement_unlock_ignores_already_unlocked_achievements(self, achievement_service, achievement_repository_mock, user_achievement_repository_mock):
        """
        Behavior: When user meets criteria for achievement they already have, should not unlock again
        Expected: No duplicate achievements, no additional XP awarded
        """
        # Arrange
        first_steps_achievement = Achievement(
            id="achievement_001",
            name="First Steps",
            description="Complete your first context build optimization",
            rarity=AchievementRarity.COMMON,
            icon="target",
            xp_reward=50,
            trigger=AchievementTrigger(
                trigger_type="optimization_count",
                threshold=1
            ),
            category="getting_started"
        )
        
        existing_user_achievement = UserAchievement(
            user_id="user_001",
            achievement_id="achievement_001",
            unlocked_at=datetime.now(timezone.utc),
            xp_awarded=50
        )
        
        achievement_repository_mock.get_all.return_value = [first_steps_achievement]
        user_achievement_repository_mock.get_user_achievements.return_value = [existing_user_achievement]
        
        check_request = CheckAchievementUnlockRequest(
            user_id="user_001",
            event_type="optimization_completed",
            event_data={
                "success": True,
                "optimization_count": 5  # Well above threshold
            }
        )
        
        # Act
        result = achievement_service.check_achievement_unlock(check_request)
        
        # Assert
        assert result.success is True
        assert len(result.unlocked_achievements) == 0
        assert result.total_xp_awarded == 0
        user_achievement_repository_mock.save_user_achievement.assert_not_called()

    def test_get_user_achievements_returns_comprehensive_achievement_data(self, achievement_service, achievement_repository_mock, user_achievement_repository_mock, test_data):
        """
        Behavior: When requesting user achievements, should return unlocked achievements with stats
        Expected: Complete achievement data with progress, rarity info, and completion stats
        """
        # Arrange
        all_achievements = [
            Achievement(id="achievement_001", name="First Steps", rarity=AchievementRarity.COMMON, xp_reward=50, trigger=AchievementTrigger("optimization_count", 1), category="getting_started"),
            Achievement(id="achievement_002", name="Context Optimizer", rarity=AchievementRarity.GOLD, xp_reward=200, trigger=AchievementTrigger("success_rate", 0.9), category="performance"),
            Achievement(id="achievement_003", name="Speed Demon", rarity=AchievementRarity.SILVER, xp_reward=150, trigger=AchievementTrigger("speed_optimization", 30), category="efficiency")
        ]
        
        user_achievements = [
            UserAchievement("user_001", "achievement_001", datetime.now(timezone.utc), 50),
            UserAchievement("user_001", "achievement_002", datetime.now(timezone.utc), 200)
        ]
        
        achievement_repository_mock.get_all.return_value = all_achievements
        user_achievement_repository_mock.get_user_achievements.return_value = user_achievements
        
        get_request = GetUserAchievementsRequest(user_id="user_001")
        
        # Act
        result = achievement_service.get_user_achievements(get_request)
        
        # Assert
        assert result.success is True
        assert result.unlocked_count == 2
        assert result.total_achievements == 3
        assert result.completion_percentage == pytest.approx(66.67, rel=1e-2)
        assert result.total_xp_from_achievements == 250
        assert result.rare_achievements_count == 1  # Gold achievement
        assert len(result.unlocked_achievements) == 2
        assert len(result.locked_achievements) == 1

    def test_calculate_rarity_multiplier_affects_xp_reward(self, achievement_service, achievement_repository_mock, user_achievement_repository_mock):
        """
        Behavior: When achievement has higher rarity, XP reward should be multiplied accordingly
        Expected: Rare achievements give bonus XP based on rarity multiplier
        """
        # Arrange
        diamond_achievement = Achievement(
            id="achievement_007",
            name="Consistency Champion", 
            description="Maintain a 15-day optimization streak",
            rarity=AchievementRarity.DIAMOND,
            icon="calendar",
            xp_reward=100,  # Base XP
            trigger=AchievementTrigger(
                trigger_type="daily_streak",
                threshold=15
            ),
            category="engagement"
        )
        
        achievement_repository_mock.get_all.return_value = [diamond_achievement]
        user_achievement_repository_mock.get_user_achievements.return_value = []
        
        check_request = CheckAchievementUnlockRequest(
            user_id="user_001",
            event_type="daily_streak_updated",
            event_data={
                "streak_days": 15
            }
        )
        
        # Act
        result = achievement_service.check_achievement_unlock(check_request)
        
        # Assert
        assert result.success is True
        assert len(result.unlocked_achievements) == 1
        # Diamond rarity has 5.0x multiplier, so 100 * 5 = 500 XP
        assert result.total_xp_awarded == 500

    def test_achievement_progress_tracking_for_partial_completion(self, achievement_service, achievement_repository_mock, user_achievement_repository_mock):
        """
        Behavior: When user makes progress toward achievement but doesn't complete it, progress should be tracked
        Expected: Progress percentage calculated and stored for user feedback
        """
        # Arrange
        betting_achievement = Achievement(
            id="achievement_004",
            name="Token Master",
            description="Win 10 token bets in a row",
            rarity=AchievementRarity.PLATINUM,
            icon="crown",
            xp_reward=300,
            trigger=AchievementTrigger(
                trigger_type="betting_streak",
                threshold=10
            ),
            category="gambling"
        )
        
        achievement_repository_mock.get_all.return_value = [betting_achievement]
        user_achievement_repository_mock.get_user_achievements.return_value = []
        
        check_request = CheckAchievementUnlockRequest(
            user_id="user_001",
            event_type="betting_win",
            event_data={
                "streak": 7  # 7 out of 10 needed
            }
        )
        
        # Act
        result = achievement_service.check_achievement_unlock(check_request)
        
        # Assert
        assert result.success is True
        assert len(result.unlocked_achievements) == 0
        assert len(result.progress_updates) == 1
        progress = result.progress_updates[0]
        assert progress["achievement_id"] == "achievement_004"
        assert progress["current_progress"] == 7
        assert progress["required_progress"] == 10
        assert progress["progress_percentage"] == 70

    def test_multiple_achievements_unlock_simultaneously(self, achievement_service, achievement_repository_mock, user_achievement_repository_mock):
        """
        Behavior: When single event satisfies multiple achievement conditions, all should unlock
        Expected: Multiple achievements unlocked, total XP awarded correctly
        """
        # Arrange
        achievements = [
            Achievement(id="achievement_001", name="First Steps", rarity=AchievementRarity.COMMON, xp_reward=50, 
                       trigger=AchievementTrigger("optimization_count", 1), category="getting_started"),
            Achievement(id="achievement_005", name="Team Player", rarity=AchievementRarity.GOLD, xp_reward=250,
                       trigger=AchievementTrigger("first_optimization", 1), category="social")  # Also triggers on first optimization
        ]
        
        achievement_repository_mock.get_all.return_value = achievements
        user_achievement_repository_mock.get_user_achievements.return_value = []
        
        check_request = CheckAchievementUnlockRequest(
            user_id="user_001",
            event_type="optimization_completed",
            event_data={
                "success": True,
                "optimization_count": 1,
                "is_first_optimization": True
            }
        )
        
        # Act
        result = achievement_service.check_achievement_unlock(check_request)
        
        # Assert
        assert result.success is True
        assert len(result.unlocked_achievements) == 2
        achievement_ids = [ach.id for ach in result.unlocked_achievements]
        assert "achievement_001" in achievement_ids
        assert "achievement_005" in achievement_ids
        # Total XP: 50 (common) + 500 (gold with 2x multiplier) = 550
        expected_xp = 50 + (250 * 2)  # Common + Gold with rarity multiplier
        assert result.total_xp_awarded == expected_xp