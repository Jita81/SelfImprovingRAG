#!/usr/bin/env python3
"""
Manual test script for User Management module
Verifies TDD Cycle 10 implementation without pytest
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
from user_management.application.services.user_service import UserService
from user_management.infrastructure.repositories.user_repository import InMemoryUserRepository
from user_management.application.dtos.user_requests import CreateUserRequest, GainExperienceRequest
from user_management.domain.entities.user import User
from user_management.domain.value_objects.user_profile import UserProfile
from user_management.domain.value_objects.gamification_stats import GamificationStats

def test_create_user():
    """Test user creation with gamification initialization"""
    print("=== Testing User Creation ===")
    
    # Setup
    repository = InMemoryUserRepository()
    service = UserService(repository)
    
    # Create user request
    request = CreateUserRequest(
        email="test.user@example.com",
        name="Test User",
        role="developer",
        team="backend",
        company="TestCorp"
    )
    
    # Execute
    result = service.create_user(request)
    
    # Verify
    assert result.success, f"User creation failed: {result.error_message}"
    assert result.user is not None, "User object not returned"
    assert result.user.gamification.level == 1, f"Expected level 1, got {result.user.gamification.level}"
    assert result.user.gamification.experience_points == 0, f"Expected 0 XP, got {result.user.gamification.experience_points}"
    assert result.user.gamification.total_optimizations == 0, f"Expected 0 optimizations, got {result.user.gamification.total_optimizations}"
    assert result.user.profile.email == "test.user@example.com", f"Email mismatch: {result.user.profile.email}"
    
    print("✓ User creation test passed")
    return result.user.id

def test_gain_experience_without_levelup(user_id):
    """Test gaining experience without level up"""
    print("=== Testing Experience Gain (No Level Up) ===")
    
    # Setup  
    repository = InMemoryUserRepository()
    service = UserService(repository)
    
    # Create a user with known stats - use level 10 with 1600 XP (need 1500 for level 10, 3000 for level 12)
    # So adding 150 XP should give 1750 total, still at level 10
    profile = UserProfile(
        email="alex.chen@example.com",
        name="Alex Chen", 
        role="developer",
        team="backend",
        company="TechCorp"
    )
    
    gamification = GamificationStats(
        level=10,
        experience_points=1600,  # Level 10 requires 1500, level 12 requires 3000
        total_optimizations=156,
        successful_optimizations=142,
        win_streak=7
    )
    
    user = User(id="test_user_001", profile=profile, gamification=gamification)
    repository.save(user)
    
    # Debug: Print initial stats
    print(f"Initial state: Level {user.gamification.level}, XP {user.gamification.experience_points}")
    print(f"Level 10 threshold: {user.gamification._get_level_threshold(10)}")
    print(f"Level 12 threshold: {user.gamification._get_level_threshold(12)}")
    print(f"Current level XP: {user.gamification.current_level_xp}")
    print(f"XP until next: {user.gamification.xp_until_next_level}")
    
    # Create gain experience request  
    request = GainExperienceRequest(
        user_id="test_user_001",
        points=150,
        reason="successful_optimization"
    )
    
    # Execute
    result = service.gain_experience(request)
    
    # Debug: Print result
    print(f"Result: success={result.success}, level_up={result.level_up}")
    print(f"Old level: {result.old_level}, New level: {result.new_level}")
    print(f"New XP: {result.new_xp}, XP until next: {result.xp_until_next}")
    
    # Verify
    assert result.success, f"Experience gain failed: {result.error_message}"
    assert result.level_up == False, f"Unexpected level up occurred"
    assert result.old_level == 10, f"Expected old level 10, got {result.old_level}"
    assert result.new_level == 10, f"Expected new level 10, got {result.new_level}"
    # User should have 1750 total XP, which is 250 XP into level 10 (1750 - 1500)
    assert result.new_xp == 250, f"Expected 250 current level XP, got {result.new_xp}"
    
    print("✓ Experience gain (no level up) test passed")

def test_gain_experience_with_levelup():
    """Test gaining experience with level up"""
    print("=== Testing Experience Gain (With Level Up) ===")
    
    # Setup
    repository = InMemoryUserRepository()
    service = UserService(repository)
    
    # Create a user close to level up (level 10 with 2900 XP, needs 3000 for level 12)
    profile = UserProfile(
        email="levelup.test@example.com",
        name="Level Up Test",
        role="developer", 
        team="backend",
        company="TechCorp"
    )
    
    gamification = GamificationStats(
        level=10,
        experience_points=2900,  # Close to level 12 threshold of 3000
        total_optimizations=156,
        successful_optimizations=142,
        win_streak=7
    )
    
    user = User(id="levelup_user", profile=profile, gamification=gamification)
    repository.save(user)
    
    # Debug: Print initial stats
    print(f"Initial state: Level {user.gamification.level}, XP {user.gamification.experience_points}")
    print(f"Current level XP: {user.gamification.current_level_xp}")
    print(f"XP until next: {user.gamification.xp_until_next_level}")
    
    # Create gain experience request that should trigger level up
    request = GainExperienceRequest(
        user_id="levelup_user",
        points=200,  # 2900 + 200 = 3100, which exceeds 3000 threshold for level 12
        reason="achievement_unlock"
    )
    
    # Execute
    result = service.gain_experience(request)
    
    # Debug: Print result
    print(f"Result: success={result.success}, level_up={result.level_up}")
    print(f"Old level: {result.old_level}, New level: {result.new_level}")
    print(f"New XP: {result.new_xp}, XP until next: {result.xp_until_next}")
    
    # Verify
    assert result.success, f"Experience gain failed: {result.error_message}"
    assert result.level_up == True, f"Expected level up but didn't occur"
    assert result.old_level == 10, f"Expected old level 10, got {result.old_level}"
    assert result.new_level == 12, f"Expected new level 12, got {result.new_level}"
    # User should have 3100 total XP, which is 100 XP into level 12 (3100 - 3000)
    assert result.new_xp == 100, f"Expected 100 current level XP, got {result.new_xp}"
    
    print("✓ Experience gain (with level up) test passed")

def test_track_optimization_results():
    """Test tracking optimization results and win streaks"""
    print("=== Testing Optimization Tracking ===")
    
    # Setup
    repository = InMemoryUserRepository()
    service = UserService(repository)
    
    # Create a user
    profile = UserProfile(
        email="optimization.test@example.com",
        name="Optimization Test",
        role="developer",
        team="backend", 
        company="TechCorp"
    )
    
    gamification = GamificationStats(
        level=5,
        experience_points=500,
        total_optimizations=10,
        successful_optimizations=8,
        win_streak=3
    )
    
    user = User(id="optimization_user", profile=profile, gamification=gamification)
    repository.save(user)
    
    # Test successful optimization (should increment win streak)
    result = service.track_optimization_result("optimization_user", success=True)
    
    assert result.success, f"Optimization tracking failed: {result.error_message}"
    assert result.new_win_streak == 4, f"Expected win streak 4, got {result.new_win_streak}"
    assert result.total_optimizations == 11, f"Expected 11 total optimizations, got {result.total_optimizations}"
    assert result.successful_optimizations == 9, f"Expected 9 successful optimizations, got {result.successful_optimizations}"
    
    # Test failed optimization (should reset win streak)
    result = service.track_optimization_result("optimization_user", success=False)
    
    assert result.success, f"Optimization tracking failed: {result.error_message}"
    assert result.new_win_streak == 0, f"Expected win streak 0, got {result.new_win_streak}"
    assert result.total_optimizations == 12, f"Expected 12 total optimizations, got {result.total_optimizations}"
    assert result.successful_optimizations == 9, f"Expected 9 successful optimizations (no change), got {result.successful_optimizations}"
    
    print("✓ Optimization tracking test passed")

def test_invalid_email():
    """Test user creation with invalid email"""
    print("=== Testing Invalid Email Validation ===")
    
    # Setup
    repository = InMemoryUserRepository()
    service = UserService(repository)
    
    # Create user request with invalid email
    request = CreateUserRequest(
        email="invalid-email",  # Invalid format
        name="Test User",
        role="developer",
        team="backend",
        company="TestCorp"
    )
    
    # Execute
    result = service.create_user(request)
    
    # Verify
    assert result.success == False, "Expected failure for invalid email"
    assert "email" in result.error_message.lower(), f"Expected email error message, got: {result.error_message}"
    
    print("✓ Invalid email validation test passed")

def test_get_user_profile():
    """Test getting user profile with calculated metrics"""
    print("=== Testing Get User Profile ===")
    
    # Setup
    repository = InMemoryUserRepository()
    service = UserService(repository)
    
    # Create a user with known stats
    profile = UserProfile(
        email="profile.test@example.com",
        name="Profile Test",
        role="developer",
        team="backend",
        company="TechCorp"
    )
    
    gamification = GamificationStats(
        level=12,
        experience_points=3200,  # Level 12 + some XP
        total_optimizations=156,
        successful_optimizations=142,
        win_streak=7
    )
    
    user = User(id="profile_user", profile=profile, gamification=gamification)
    repository.save(user)
    
    # Execute
    result = service.get_user_profile("profile_user")
    
    # Verify
    assert result.success, f"Get user profile failed: {result.error_message}"
    assert result.user is not None, "User object not returned"
    assert result.user.id == "profile_user", "Wrong user returned"
    assert abs(result.success_rate - 0.910) < 0.001, f"Expected success rate ~0.910, got {result.success_rate}"  # 142/156
    assert result.current_level_title == "Context Master", f"Expected 'Context Master', got '{result.current_level_title}'"
    
    print("✓ Get user profile test passed")

def main():
    """Run all manual tests"""
    print("Running User Management Module Manual Tests...")
    print("=" * 50)
    
    try:
        # Test user creation
        user_id = test_create_user()
        
        # Test experience gain without level up
        test_gain_experience_without_levelup(user_id)
        
        # Test experience gain with level up
        test_gain_experience_with_levelup()
        
        # Test optimization tracking
        test_track_optimization_results()
        
        # Test validation
        test_invalid_email()
        
        # Test get user profile
        test_get_user_profile()
        
        print("=" * 50)
        print("🎉 All tests passed! User Management module is working correctly.")
        print("TDD Cycle 10 implementation is complete and functional.")
        print()
        print("Key Features Implemented:")
        print("• User creation with email validation")
        print("• Gamification stats initialization (level 1, 0 XP)")
        print("• Experience point gain with level up detection")
        print("• Win streak tracking for optimizations")
        print("• Success rate calculation")
        print("• Level system with titles and thresholds")
        print("• Comprehensive error handling")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)