#!/usr/bin/env python3
"""
Manual test script for Achievement System module
Verifies TDD Cycle 11 implementation without pytest
"""

import sys
import os

# Add the correct paths to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
modules_dir = os.path.dirname(current_dir)
workspace_dir = os.path.dirname(modules_dir)

sys.path.insert(0, workspace_dir)
sys.path.insert(0, modules_dir)
sys.path.insert(0, current_dir)

# Now import with absolute paths
from achievement_system.application.services.achievement_service import AchievementService
from achievement_system.infrastructure.repositories.achievement_repository import InMemoryAchievementRepository
from achievement_system.infrastructure.repositories.user_achievement_repository import InMemoryUserAchievementRepository
from achievement_system.application.dtos.achievement_requests import CheckAchievementUnlockRequest, GetUserAchievementsRequest
from achievement_system.domain.entities.achievement import Achievement
from achievement_system.domain.entities.user_achievement import UserAchievement
from achievement_system.domain.value_objects.achievement_rarity import AchievementRarity
from achievement_system.domain.value_objects.achievement_trigger import AchievementTrigger

def test_simple_achievement_unlock():
    """Test unlocking a simple achievement"""
    print("=== Testing Simple Achievement Unlock ===")
    
    # Setup - Create empty repositories without loading test data
    achievement_repo = InMemoryAchievementRepository()
    achievement_repo._achievements = {}  # Clear any test data
    user_achievement_repo = InMemoryUserAchievementRepository()
    user_achievement_repo._user_achievements = {}  # Clear any test data
    service = AchievementService(achievement_repo, user_achievement_repo)
    
    # Create a simple achievement
    first_steps_achievement = Achievement(
        id="test_achievement_001",  # Use different ID to avoid conflicts
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
    
    # Add achievement to repository
    achievement_repo.save(first_steps_achievement)
    
    # Debug: Check if achievement was saved
    all_achievements = achievement_repo.get_all()
    print(f"Debug: Achievements in repo: {len(all_achievements)}")
    if all_achievements:
        print(f"Debug: First achievement: {all_achievements[0].name}, ID: {all_achievements[0].id}")
    
    # Check user has no existing achievements
    existing_achievements = user_achievement_repo.get_user_achievements("test_user_001")
    print(f"Debug: User existing achievements: {len(existing_achievements)}")
    
    # Create unlock request
    request = CheckAchievementUnlockRequest(
        user_id="test_user_001",
        event_type="optimization_completed",
        event_data={
            "success": True,
            "optimization_count": 1
        }
    )
    
    # Debug: Check trigger logic
    print(f"Debug: Event data: {request.event_data}")
    if all_achievements:
        trigger_result = all_achievements[0].check_unlock_conditions(request.event_data)
        print(f"Debug: Trigger check result: {trigger_result}")
    
    # Execute
    result = service.check_achievement_unlock(request)
    
    # Debug: Print result details
    print(f"Debug: Service result success: {result.success}")
    print(f"Debug: Unlocked achievements count: {len(result.unlocked_achievements)}")
    print(f"Debug: Total XP awarded: {result.total_xp_awarded}")
    print(f"Debug: Error message: {result.error_message}")
    
    if result.unlocked_achievements:
        print(f"Debug: Unlocked achievement ID: {result.unlocked_achievements[0].id}")
    
    # Verify
    assert result.success is True, f"Achievement unlock failed: {result.error_message}"
    assert len(result.unlocked_achievements) == 1, f"Expected 1 achievement, got {len(result.unlocked_achievements)}"
    assert result.unlocked_achievements[0].id == "test_achievement_001", f"Wrong achievement unlocked: {result.unlocked_achievements[0].id}"
    assert result.total_xp_awarded == 50, f"Expected 50 XP, got {result.total_xp_awarded}"
    
    print("✓ Simple achievement unlock test passed")

def test_complex_achievement_trigger():
    """Test achievement with complex trigger conditions"""
    print("=== Testing Complex Achievement Trigger ===")
    
    # Setup - Create clean repositories
    achievement_repo = InMemoryAchievementRepository()
    achievement_repo._achievements = {}  # Clear any test data
    user_achievement_repo = InMemoryUserAchievementRepository()
    user_achievement_repo._user_achievements = {}  # Clear any test data
    service = AchievementService(achievement_repo, user_achievement_repo)
    
    # Create complex achievement
    context_optimizer_achievement = Achievement(
        id="test_achievement_002",
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
    
    achievement_repo.save(context_optimizer_achievement)
    
    # Test with sufficient conditions
    request = CheckAchievementUnlockRequest(
        user_id="test_user_002",
        event_type="optimization_completed",
        event_data={
            "success": True,
            "total_optimizations": 10,
            "successful_optimizations": 9,
            "success_rate": 0.9
        }
    )
    
    # Execute
    result = service.check_achievement_unlock(request)
    
    # Verify
    assert result.success is True, f"Achievement unlock failed: {result.error_message}"
    assert len(result.unlocked_achievements) == 1, f"Expected 1 achievement, got {len(result.unlocked_achievements)}"
    assert result.unlocked_achievements[0].id == "test_achievement_002", f"Wrong achievement unlocked"
    # Gold rarity has 2x multiplier, so 200 * 2 = 400 XP
    assert result.total_xp_awarded == 400, f"Expected 400 XP (with gold multiplier), got {result.total_xp_awarded}"
    
    print("✓ Complex achievement trigger test passed")

def test_insufficient_conditions():
    """Test that achievement doesn't unlock with insufficient conditions"""
    print("=== Testing Insufficient Conditions ===")
    
    # Setup - Create clean repositories
    achievement_repo = InMemoryAchievementRepository()
    achievement_repo._achievements = {}  # Clear any test data
    user_achievement_repo = InMemoryUserAchievementRepository()
    user_achievement_repo._user_achievements = {}  # Clear any test data
    service = AchievementService(achievement_repo, user_achievement_repo)
    
    # Create achievement requiring 10 attempts
    context_optimizer_achievement = Achievement(
        id="test_achievement_002",
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
    
    achievement_repo.save(context_optimizer_achievement)
    
    # Test with insufficient attempts (only 5 instead of 10)
    request = CheckAchievementUnlockRequest(
        user_id="test_user_003",
        event_type="optimization_completed",
        event_data={
            "success": True,
            "total_optimizations": 5,  # Not enough attempts
            "successful_optimizations": 5,
            "success_rate": 1.0  # Perfect rate but not enough attempts
        }
    )
    
    # Execute
    result = service.check_achievement_unlock(request)
    
    # Verify
    assert result.success is True, f"Service call failed: {result.error_message}"
    assert len(result.unlocked_achievements) == 0, f"No achievements should unlock, got {len(result.unlocked_achievements)}"
    assert result.total_xp_awarded == 0, f"No XP should be awarded, got {result.total_xp_awarded}"
    
    print("✓ Insufficient conditions test passed")

def test_duplicate_achievement_prevention():
    """Test that already unlocked achievements don't unlock again"""
    print("=== Testing Duplicate Achievement Prevention ===")
    
    # Setup - Create clean repositories
    achievement_repo = InMemoryAchievementRepository()
    achievement_repo._achievements = {}  # Clear any test data
    user_achievement_repo = InMemoryUserAchievementRepository()
    user_achievement_repo._user_achievements = {}  # Clear any test data
    service = AchievementService(achievement_repo, user_achievement_repo)
    
    # Create achievement
    first_steps_achievement = Achievement(
        id="test_achievement_001",
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
    
    achievement_repo.save(first_steps_achievement)
    
    # Pre-create user achievement (user already has this achievement)
    existing_user_achievement = UserAchievement.create_new(
        user_id="test_user_004",
        achievement_id="test_achievement_001",
        xp_awarded=50
    )
    user_achievement_repo.save_user_achievement(existing_user_achievement)
    
    # Try to unlock the same achievement again
    request = CheckAchievementUnlockRequest(
        user_id="test_user_004",
        event_type="optimization_completed",
        event_data={
            "success": True,
            "optimization_count": 5  # Well above threshold
        }
    )
    
    # Execute
    result = service.check_achievement_unlock(request)
    
    # Verify
    assert result.success is True, f"Service call failed: {result.error_message}"
    assert len(result.unlocked_achievements) == 0, f"No new achievements should unlock, got {len(result.unlocked_achievements)}"
    assert result.total_xp_awarded == 0, f"No additional XP should be awarded, got {result.total_xp_awarded}"
    
    print("✓ Duplicate achievement prevention test passed")

def test_rarity_multiplier():
    """Test that rarity multiplier affects XP rewards correctly"""
    print("=== Testing Rarity Multiplier ===")
    
    # Setup - Create clean repositories
    achievement_repo = InMemoryAchievementRepository()
    achievement_repo._achievements = {}  # Clear any test data
    user_achievement_repo = InMemoryUserAchievementRepository()
    user_achievement_repo._user_achievements = {}  # Clear any test data
    service = AchievementService(achievement_repo, user_achievement_repo)
    
    # Create diamond achievement (5x multiplier)
    diamond_achievement = Achievement(
        id="test_achievement_007",
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
    
    achievement_repo.save(diamond_achievement)
    
    # Test unlock
    request = CheckAchievementUnlockRequest(
        user_id="test_user_005",
        event_type="daily_streak_updated",
        event_data={
            "streak_days": 15
        }
    )
    
    # Execute
    result = service.check_achievement_unlock(request)
    
    # Verify
    assert result.success is True, f"Achievement unlock failed: {result.error_message}"
    assert len(result.unlocked_achievements) == 1, f"Expected 1 achievement, got {len(result.unlocked_achievements)}"
    # Diamond rarity has 5.0x multiplier, so 100 * 5 = 500 XP
    assert result.total_xp_awarded == 500, f"Expected 500 XP (with diamond multiplier), got {result.total_xp_awarded}"
    
    print("✓ Rarity multiplier test passed")

def test_get_user_achievements():
    """Test getting comprehensive user achievement data"""
    print("=== Testing Get User Achievements ===")
    
    # Setup - Create clean repositories
    achievement_repo = InMemoryAchievementRepository()
    achievement_repo._achievements = {}  # Clear any test data
    user_achievement_repo = InMemoryUserAchievementRepository()
    user_achievement_repo._user_achievements = {}  # Clear any test data
    service = AchievementService(achievement_repo, user_achievement_repo)
    
    # Create achievements
    achievements = [
        Achievement(
            id="test_achievement_001", name="First Steps", 
            rarity=AchievementRarity.COMMON, icon="target", xp_reward=50,
            trigger=AchievementTrigger("optimization_count", 1), category="getting_started",
            description="Complete your first optimization"
        ),
        Achievement(
            id="test_achievement_002", name="Context Optimizer", 
            rarity=AchievementRarity.GOLD, icon="trophy", xp_reward=200,
            trigger=AchievementTrigger("success_rate", 0.9), category="performance",
            description="Achieve 90% success rate"
        ),
        Achievement(
            id="test_achievement_003", name="Speed Demon", 
            rarity=AchievementRarity.SILVER, icon="zap", xp_reward=150,
            trigger=AchievementTrigger("speed_optimization", 30), category="efficiency",
            description="Complete fast optimizations"
        )
    ]
    
    for achievement in achievements:
        achievement_repo.save(achievement)
    
    # Create user achievements (user has first two achievements)
    user_achievements = [
        UserAchievement.create_new("test_user_006", "test_achievement_001", 50),
        UserAchievement.create_new("test_user_006", "test_achievement_002", 400)  # Gold with multiplier
    ]
    
    for ua in user_achievements:
        user_achievement_repo.save_user_achievement(ua)
    
    # Test get user achievements
    request = GetUserAchievementsRequest(user_id="test_user_006")
    result = service.get_user_achievements(request)
    
    # Verify
    assert result.success is True, f"Get user achievements failed: {result.error_message}"
    assert result.unlocked_count == 2, f"Expected 2 unlocked achievements, got {result.unlocked_count}"
    assert result.total_achievements == 3, f"Expected 3 total achievements, got {result.total_achievements}"
    assert abs(result.completion_percentage - 66.67) < 0.1, f"Expected ~66.67% completion, got {result.completion_percentage}"
    assert result.total_xp_from_achievements == 450, f"Expected 450 total XP, got {result.total_xp_from_achievements}"
    assert result.rare_achievements_count == 1, f"Expected 1 rare achievement, got {result.rare_achievements_count}"
    assert len(result.unlocked_achievements) == 2, f"Expected 2 unlocked achievements list, got {len(result.unlocked_achievements)}"
    assert len(result.locked_achievements) == 1, f"Expected 1 locked achievement, got {len(result.locked_achievements)}"
    
    print("✓ Get user achievements test passed")

def test_progress_tracking():
    """Test achievement progress tracking"""
    print("=== Testing Achievement Progress Tracking ===")
    
    # Setup - Create clean repositories
    achievement_repo = InMemoryAchievementRepository()
    achievement_repo._achievements = {}  # Clear any test data
    user_achievement_repo = InMemoryUserAchievementRepository()
    user_achievement_repo._user_achievements = {}  # Clear any test data
    service = AchievementService(achievement_repo, user_achievement_repo)
    
    # Create achievement requiring 10 wins
    betting_achievement = Achievement(
        id="test_achievement_004",
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
    
    achievement_repo.save(betting_achievement)
    
    # Test with partial progress (7 out of 10)
    request = CheckAchievementUnlockRequest(
        user_id="test_user_007",
        event_type="betting_win",
        event_data={
            "streak": 7  # 7 out of 10 needed
        }
    )
    
    # Execute
    result = service.check_achievement_unlock(request)
    
    # Verify
    assert result.success is True, f"Service call failed: {result.error_message}"
    assert len(result.unlocked_achievements) == 0, f"Achievement should not unlock yet, got {len(result.unlocked_achievements)}"
    assert len(result.progress_updates) == 1, f"Expected 1 progress update, got {len(result.progress_updates)}"
    
    progress = result.progress_updates[0]
    assert progress["achievement_id"] == "test_achievement_004", f"Wrong achievement in progress: {progress['achievement_id']}"
    assert progress["current_progress"] == 7, f"Expected current progress 7, got {progress['current_progress']}"
    assert progress["required_progress"] == 10, f"Expected required progress 10, got {progress['required_progress']}"
    assert progress["progress_percentage"] == 70, f"Expected 70% progress, got {progress['progress_percentage']}"
    
    print("✓ Achievement progress tracking test passed")

def test_multiple_achievements_unlock():
    """Test unlocking multiple achievements simultaneously"""
    print("=== Testing Multiple Achievements Unlock ===")
    
    # Setup - Create clean repositories
    achievement_repo = InMemoryAchievementRepository()
    achievement_repo._achievements = {}  # Clear any test data
    user_achievement_repo = InMemoryUserAchievementRepository()
    user_achievement_repo._user_achievements = {}  # Clear any test data
    service = AchievementService(achievement_repo, user_achievement_repo)
    
    # Create achievements that can both trigger on first optimization
    achievements = [
        Achievement(
            id="test_achievement_001", name="First Steps", 
            rarity=AchievementRarity.COMMON, icon="target", xp_reward=50,
            trigger=AchievementTrigger("optimization_count", 1), category="getting_started",
            description="Complete your first optimization"
        ),
        Achievement(
            id="test_achievement_005", name="Team Player", 
            rarity=AchievementRarity.GOLD, icon="users", xp_reward=250,
            trigger=AchievementTrigger("first_optimization", 1), category="social",
            description="Complete your first optimization"
        )
    ]
    
    for achievement in achievements:
        achievement_repo.save(achievement)
    
    # Test with event that satisfies both conditions
    request = CheckAchievementUnlockRequest(
        user_id="test_user_008",
        event_type="optimization_completed",
        event_data={
            "success": True,
            "optimization_count": 1,
            "is_first_optimization": True
        }
    )
    
    # Execute
    result = service.check_achievement_unlock(request)
    
    # Verify
    assert result.success is True, f"Achievement unlock failed: {result.error_message}"
    assert len(result.unlocked_achievements) == 2, f"Expected 2 achievements, got {len(result.unlocked_achievements)}"
    
    achievement_ids = [ach.id for ach in result.unlocked_achievements]
    assert "test_achievement_001" in achievement_ids, "First Steps achievement should be unlocked"
    assert "test_achievement_005" in achievement_ids, "Team Player achievement should be unlocked"
    
    # Total XP: 50 (common) + 500 (gold with 2x multiplier) = 550
    expected_xp = 50 + (250 * 2)
    assert result.total_xp_awarded == expected_xp, f"Expected {expected_xp} XP, got {result.total_xp_awarded}"
    
    print("✓ Multiple achievements unlock test passed")

def main():
    """Run all manual tests"""
    print("Running Achievement System Module Manual Tests...")
    print("=" * 50)
    
    try:
        # Test basic achievement unlock
        test_simple_achievement_unlock()
        
        # Test complex trigger conditions
        test_complex_achievement_trigger()
        
        # Test insufficient conditions
        test_insufficient_conditions()
        
        # Test duplicate prevention
        test_duplicate_achievement_prevention()
        
        # Test rarity multiplier
        test_rarity_multiplier()
        
        # Test getting user achievements
        test_get_user_achievements()
        
        # Test progress tracking
        test_progress_tracking()
        
        # Test multiple achievements unlock
        test_multiple_achievements_unlock()
        
        print("=" * 50)
        print("🎉 All tests passed! Achievement System module is working correctly.")
        print("TDD Cycle 11 implementation is complete and functional.")
        print()
        print("Key Features Implemented:")
        print("• Simple and complex achievement triggers")
        print("• Rarity system with XP multipliers (Common, Silver, Gold, Platinum, Diamond)")
        print("• Achievement progress tracking")
        print("• Duplicate achievement prevention")
        print("• Multiple simultaneous achievement unlocks")
        print("• Comprehensive user achievement statistics")
        print("• Event-driven achievement checking")
        print("• Repository pattern for data persistence")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)