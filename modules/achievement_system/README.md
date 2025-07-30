# Achievement System Module

## Overview
The Achievement System module provides a comprehensive gamification framework for recognizing and rewarding user accomplishments in the Self-Improving RAG Platform. It implements a sophisticated achievement tracking system with rarity-based XP multipliers, complex trigger conditions, progress tracking, and event-driven unlocking mechanisms.

## Features
- **5-Tier Rarity System**: Common, Silver, Gold, Platinum, Diamond achievements with XP multipliers
- **Complex Trigger Conditions**: Multi-condition achievement requirements (count, success rate, streaks, etc.)
- **Progress Tracking**: Real-time calculation of achievement completion progress
- **Event-Driven Unlocking**: Automatic achievement checking based on user actions
- **Duplicate Prevention**: Ensures users can't unlock the same achievement twice
- **Simultaneous Unlocks**: Handles multiple achievements being unlocked in a single event
- **Comprehensive Statistics**: User achievement analytics and completion tracking

## Architecture

### Domain Layer
- **Entities**: `Achievement` (achievement definitions), `UserAchievement` (user unlock records)
- **Value Objects**: `AchievementRarity` (rarity properties), `AchievementTrigger` (unlock conditions)
- **Domain Services**: Trigger evaluation and progress calculation logic

### Application Layer
- **Services**: `AchievementService` (orchestrates all achievement operations)
- **DTOs**: Request/response objects for achievement operations
- **Use Cases**: Achievement checking, progress tracking, manual awarding, statistics retrieval

### Infrastructure Layer
- **Repositories**: `AchievementRepository`, `UserAchievementRepository` with in-memory and file implementations
- **External Services**: JSON configuration loading for achievement definitions
- **Configuration**: Achievement definitions and rarity system from test data

### API Layer
- **Controllers**: (Future implementation for HTTP endpoints)
- **Routes**: (Future API endpoint definitions)
- **Middleware**: (Future cross-cutting concerns)

## Dependencies

### Internal Dependencies
- **User Management**: Achievement unlocks award bonus XP to users
- **Analytics Module**: Achievement statistics feed into analytics (future integration)

### External Dependencies
- **Python Standard Library**: `dataclasses`, `datetime`, `json`, `uuid`, `typing`, `enum`
- **File System**: JSON configuration files for achievement definitions

## Configuration

### Test Data Files
```bash
tests/test_data/achievement_test_data.json  # Achievement definitions and rarity configuration
```

### Rarity System Configuration
The module supports 5 achievement rarity tiers:

| Rarity   | XP Multiplier | Color    | Probability |
|----------|---------------|----------|-------------|
| Common   | 1.0x          | #808080  | 50%         |
| Silver   | 1.5x          | #C0C0C0  | 25%         |
| Gold     | 2.0x          | #FFD700  | 15%         |
| Platinum | 3.0x          | #E5E4E2  | 8%          |
| Diamond  | 5.0x          | #B9F2FF  | 2%          |

## Usage Examples

### Basic Usage
```python
# Create achievement service
from achievement_system.infrastructure.repositories.achievement_repository import InMemoryAchievementRepository
from achievement_system.infrastructure.repositories.user_achievement_repository import InMemoryUserAchievementRepository
from achievement_system.application.services.achievement_service import AchievementService

achievement_repo = InMemoryAchievementRepository()
user_achievement_repo = InMemoryUserAchievementRepository()
service = AchievementService(achievement_repo, user_achievement_repo)
```

### Checking Achievement Unlocks
```python
# Check for achievement unlocks based on user events
from achievement_system.application.dtos.achievement_requests import CheckAchievementUnlockRequest

request = CheckAchievementUnlockRequest(
    user_id="user-123",
    event_type="optimization_completed",
    event_data={
        "total_optimizations": 10,
        "successful_optimizations": 8,
        "win_streak": 3,
        "success_rate": 0.8
    }
)
response = service.check_achievement_unlock(request)

for unlock in response.unlocked_achievements:
    print(f"🏆 Unlocked: {unlock['name']} ({unlock['rarity']}) - {unlock['xp_awarded']} XP!")
```

### Progress Tracking
```python
# Get achievement progress for a user
from achievement_system.application.dtos.achievement_requests import GetAchievementProgressRequest

progress_request = GetAchievementProgressRequest(
    user_id="user-123",
    achievement_id="first_success"  # Optional: specific achievement
)
progress_response = service.get_achievement_progress(progress_request)

for progress in progress_response.progress_data:
    print(f"{progress['name']}: {progress['progress_percentage']:.1%} complete")
```

### Manual Achievement Awards
```python
# Manually award achievement (admin function)
from achievement_system.application.dtos.achievement_requests import AwardAchievementRequest

award_request = AwardAchievementRequest(
    user_id="user-123",
    achievement_id="special_contributor",
    reason="Exceptional community contribution"
)
award_response = service.award_achievement(award_request)

if award_response.success:
    print(f"Manually awarded: {award_response.achievement_name}")
```

## API Reference

### Core Services
- `AchievementService`: Main service class
  - `check_achievement_unlock()`: Check and unlock achievements based on events
  - `get_user_achievements()`: Retrieve all user achievements with statistics
  - `get_achievement_progress()`: Calculate progress toward uncompleted achievements
  - `award_achievement()`: Manually award achievements (admin function)

### DTOs

#### Request DTOs
- `CheckAchievementUnlockRequest`: Event-based achievement checking
- `GetUserAchievementsRequest`: User achievement retrieval
- `GetAchievementProgressRequest`: Progress calculation
- `AwardAchievementRequest`: Manual achievement awarding

#### Response DTOs
- `CheckAchievementUnlockResponse`: Achievement unlock results with XP awards
- `GetUserAchievementsResponse`: Complete user achievement data
- `GetAchievementProgressResponse`: Progress tracking information
- `AwardAchievementResponse`: Manual award confirmation

For detailed API documentation, see [API.md](./API.md).

## Testing

### Running Tests
```bash
# Run all tests for this module
cd modules/achievement_system
python3 manual_test.py

# Run with debug output
export MODULE_DEBUG=true
python3 manual_test.py
```

### Test Coverage
- **Unit Tests**: 100% coverage (9 test scenarios)
- **Integration Tests**: Service-repository integration
- **End-to-End Tests**: Complete achievement workflows

### Test Scenarios
1. **Simple Achievement Unlock**: Single-condition achievement unlocking
2. **Complex Achievement Unlock**: Multi-condition achievement unlocking
3. **Insufficient Conditions**: Achievement not unlocked when conditions not met
4. **Duplicate Prevention**: Prevention of duplicate achievement unlocks
5. **Rarity Multipliers**: Correct XP calculation based on achievement rarity
6. **User Achievement Retrieval**: Complete user achievement data access
7. **Progress Tracking**: Progress calculation for incomplete achievements
8. **Multiple Simultaneous Unlocks**: Multiple achievements unlocked in single event
9. **Manual Award System**: Admin-initiated achievement awards

For detailed testing information, see [TESTING.md](./TESTING.md).

## Data Management

### Data Models

#### Achievement Entity
- **ID**: Unique achievement identifier
- **Name**: Human-readable achievement name
- **Description**: Achievement description and requirements
- **Category**: Achievement grouping (e.g., "optimization", "milestone", "social")
- **Base XP**: Base experience point value
- **Rarity**: Achievement rarity level (affects XP multiplier)
- **Trigger**: Unlock condition specification
- **Icon**: Achievement visual representation (future)

#### UserAchievement Entity
- **User ID**: Reference to user who unlocked achievement
- **Achievement ID**: Reference to achievement definition
- **Unlocked At**: Timestamp of achievement unlock
- **XP Awarded**: Actual XP awarded (base XP × rarity multiplier)

#### AchievementRarity Value Object
- **Rarity Level**: Enum value (COMMON, SILVER, GOLD, PLATINUM, DIAMOND)
- **XP Multiplier**: Multiplication factor for base XP
- **Color**: Visual color representation
- **Probability**: Relative probability of achievements of this rarity

#### AchievementTrigger Value Object
- **Type**: Trigger type (e.g., "count", "percentage", "streak")
- **Field**: Data field to evaluate
- **Operator**: Comparison operator (">=", "==", etc.)
- **Value**: Target value for comparison
- **Additional Conditions**: Secondary requirements

### Data Flow
1. **Event Processing**: User action → Event data → Trigger evaluation → Achievement unlock
2. **Progress Calculation**: Current stats → Trigger requirements → Progress percentage
3. **XP Award**: Base XP → Rarity multiplier → Final XP → User Management integration

### Persistence
- **Repository Pattern**: Abstract interfaces for data access
- **In-Memory Implementation**: Fast access for testing and development
- **File-Based Implementation**: JSON persistence for development
- **Database Implementation**: Future PostgreSQL/MongoDB integration

## Integration

### Event Publishing
This module will publish the following events:
- `AchievementUnlocked`: When user unlocks new achievement
- `AchievementProgressUpdated`: When progress toward achievement changes
- `RareAchievementUnlocked`: When Diamond/Platinum achievement is unlocked

### Event Subscription
This module subscribes to:
- `ExperienceGained`: From User Management (for XP-based achievements)
- `OptimizationCompleted`: From Core RAG module
- `UserLeveledUp`: From User Management (for level-based achievements)
- `SocialActionPerformed`: From Social modules (for community achievements)

### API Integration
- **APIs Provided**: Achievement status, progress tracking, unlock notifications
- **APIs Consumed**: User Management for XP awards and user statistics

## Achievement Categories

### Optimization Achievements
- **First Success**: Complete first successful optimization
- **Optimization Master**: Complete 100 optimizations
- **High Performer**: Achieve 90%+ success rate with 20+ optimizations
- **Perfectionist**: Achieve 100% success rate with 10+ optimizations

### Milestone Achievements
- **Getting Started**: Complete user registration and first optimization
- **Dedicated User**: Use platform for 30 consecutive days
- **Power User**: Complete 500 total optimizations
- **Platform Expert**: Reach maximum user level

### Streak Achievements
- **On Fire**: Achieve 5-optimization win streak
- **Unstoppable**: Achieve 10-optimization win streak
- **Legendary**: Achieve 20-optimization win streak

### Social Achievements (Future)
- **Team Player**: Collaborate with 5 different team members
- **Mentor**: Help 10 new users get started
- **Community Leader**: Receive 100 positive feedback points

### Special Achievements
- **Early Adopter**: Among first 100 platform users
- **Beta Tester**: Participate in beta testing program
- **Contributor**: Contribute to platform improvement

## Error Handling

### Common Errors
- `ValueError`: Invalid achievement ID, malformed event data
- `KeyError`: Achievement or user achievement not found
- `TypeError`: Invalid data types in trigger conditions

### Error Response Format
```json
{
  "success": false,
  "error": "Achievement not found: invalid_achievement_id",
  "unlocked_achievements": [],
  "timestamp": "2023-12-07T10:30:00Z"
}
```

## Performance Considerations

### Optimization Notes
- **Trigger Evaluation**: O(1) lookup for achievement definitions
- **Progress Calculation**: Efficient condition checking
- **In-Memory Caching**: Fast access to frequently checked achievements
- **Batch Processing**: Multiple achievement checks in single operation

### Monitoring
- **Achievement Unlock Rate**: Frequency of achievement unlocks
- **Rarity Distribution**: Balance of common vs. rare achievement unlocks
- **Progress Completion**: Average progress toward achievements
- **Event Processing Time**: Performance of trigger evaluation

## Security Considerations

### Data Protection
- **Achievement Integrity**: Prevent unauthorized achievement unlocks
- **Event Validation**: Validate all incoming event data
- **Admin Functions**: Secure manual achievement award capabilities

### Privacy Considerations
- **Achievement Privacy**: User control over achievement visibility
- **Data Minimization**: Only store necessary achievement data
- **Anonymization**: Future analytics will anonymize achievement data

## Troubleshooting

### Common Issues
1. **Import Error**: `ImportError: attempted relative import beyond top-level package`
   - **Cause**: Incorrect Python path configuration
   - **Solution**: Add workspace and modules to `sys.path`

2. **Test Data Loading Error**: `FileNotFoundError: achievement_test_data.json`
   - **Cause**: Missing test data file or incorrect path
   - **Solution**: Ensure test data file exists in `tests/test_data/`

3. **Trigger Evaluation Error**: Achievement not unlocking despite meeting conditions
   - **Cause**: Incorrect trigger condition configuration
   - **Solution**: Verify trigger field names and operators in test data

4. **Repository Conflicts**: Achievements appearing in wrong tests
   - **Cause**: Shared repository state between tests
   - **Solution**: Clear repository state before each test

### Debug Mode
```bash
# Enable debug logging
export MODULE_DEBUG=true
python3 manual_test.py
```

## Development Guidelines

### Adding New Features
1. Update domain entities/value objects in `domain/`
2. Implement application services in `application/services/`
3. Add infrastructure support in `infrastructure/`
4. Create API endpoints in `api/` (future)
5. Write comprehensive tests
6. Update achievement definitions in test data
7. Update all documentation

### Code Style
- Follow PEP 8 for Python code
- Use type hints consistently (`typing` module)
- Write descriptive docstrings for all public methods
- Use dataclasses for DTOs and value objects
- Use Enums for fixed value sets (rarity levels)
- Follow Repository pattern for data access

### Adding New Achievements
1. Define achievement in `achievement_test_data.json`
2. Specify trigger conditions and rarity
3. Add test cases for new achievement
4. Update documentation with new achievement description
5. Verify integration with User Management XP system

## Changelog

### Version 1.0.0 - 2023-12-07
#### Added
- Initial implementation of Achievement System module
- 5-tier rarity system with XP multipliers (Common to Diamond)
- Complex trigger condition system for achievement unlocking
- Event-driven achievement checking with multiple condition support
- Progress tracking for incomplete achievements
- Duplicate prevention system
- Manual achievement award functionality (admin)
- Comprehensive statistics and user achievement retrieval
- Hexagonal architecture with domain/application/infrastructure separation
- Repository pattern with in-memory and file-based implementations
- Comprehensive manual testing framework
- JSON-based configuration for achievement definitions

#### Core Features
- **Achievement Definitions**: Comprehensive achievement catalog with categories
- **Rarity System**: 5-tier system with appropriate XP multipliers
- **Trigger Engine**: Complex condition evaluation for unlocks
- **Progress Tracking**: Real-time progress calculation
- **Event Integration**: Automatic checking based on user actions
- **Statistics**: Complete user achievement analytics

#### Achievement Categories
- **Optimization**: Success-based achievements
- **Milestone**: Progress-based achievements  
- **Streak**: Consecutive success achievements
- **Special**: Unique and rare achievements

#### Testing
- Unit tests for all domain entities and value objects
- Integration tests for service-repository interactions
- End-to-end tests for complete achievement workflows
- Manual test script with comprehensive scenarios
- Test data fixtures with realistic achievement definitions

#### Documentation
- Comprehensive README with usage examples
- API documentation with request/response schemas
- Testing documentation with scenario descriptions
- Inline code documentation for all public methods

For detailed changelog, see [CHANGELOG.md](./CHANGELOG.md).

## Contributing

### Development Setup
1. Navigate to `modules/achievement_system/`
2. Ensure Python 3.8+ is available
3. Verify test data file exists: `../../tests/test_data/achievement_test_data.json`

### Pull Request Process
1. Update documentation (README, API, TESTING, CHANGELOG)
2. Add/update tests for new functionality
3. Ensure all manual tests pass
4. Update achievement definitions if needed
5. Verify integration with User Management module

## Related Documentation
- [Main Project README](../../README.md)
- [Architecture Overview](../../docs/architecture/)
- [API Documentation](./API.md)
- [Testing Guide](./TESTING.md)
- [Module Implementation Summary](../../module_implementation_summary.md)
- [TDD Cycles Documentation](../../tdd_cycles_self_improving_rag.md)
- [Achievement Test Data](../../tests/test_data/achievement_test_data.json)
- [User Management Module](../user_management/README.md)
