# User Management Module

## Overview
The User Management module provides comprehensive user profile management and gamification functionality for the Self-Improving RAG Platform. It implements user creation, experience point tracking, level progression, and optimization result tracking with a complete hexagonal architecture.

## Features
- **User Profile Management**: Create and manage user profiles with email validation
- **Gamification System**: Experience points, level progression, and achievement tracking
- **Win Streak Tracking**: Monitor consecutive successful optimizations
- **Level System**: 9-tier progression from "Novice" to "Grand Master"
- **Optimization Tracking**: Record and analyze user optimization attempts and success rates
- **Repository Abstraction**: Support for in-memory and file-based data persistence

## Architecture

### Domain Layer
- **Entities**: `User` (aggregate root for user-related operations)
- **Value Objects**: `UserProfile` (immutable user data), `GamificationStats` (mutable stats tracking)
- **Domain Services**: Level calculation and XP progression logic

### Application Layer
- **Services**: `UserService` (orchestrates all user operations)
- **DTOs**: Request/response objects for all user operations
- **Use Cases**: User creation, XP gain, profile updates, optimization tracking

### Infrastructure Layer
- **Repositories**: `UserRepository` (abstract), `InMemoryUserRepository`, `FileUserRepository`
- **External Services**: JSON configuration loading for level system
- **Configuration**: Gamification rules and level thresholds from test data

### API Layer
- **Controllers**: (Future implementation for HTTP endpoints)
- **Routes**: (Future API endpoint definitions)
- **Middleware**: (Future cross-cutting concerns)

## Dependencies

### Internal Dependencies
- **Achievement System**: User XP gain can trigger achievement unlocks (future integration)
- **Analytics Module**: User statistics feed into analytics (future integration)

### External Dependencies
- **Python Standard Library**: `dataclasses`, `datetime`, `json`, `uuid`, `typing`
- **File System**: JSON configuration files for level system and initial data

## Configuration

### Test Data Files
```bash
tests/test_data/gamification_test_data.json  # Level system configuration and sample data
```

### Level System Configuration
The module loads level thresholds and titles from the gamification test data:
- **Level 1 (Novice)**: 0 XP
- **Level 2 (Beginner)**: 100 XP  
- **Level 3 (Apprentice)**: 300 XP
- **Level 4 (Practitioner)**: 600 XP
- **Level 5 (Specialist)**: 1000 XP
- **Level 6 (Expert)**: 1500 XP
- **Level 7 (Master)**: 2100 XP
- **Level 8 (Grandmaster)**: 2800 XP
- **Level 9 (Legend)**: 3600 XP

## Usage Examples

### Basic Usage
```python
# Create user service
from user_management.infrastructure.repositories.user_repository import InMemoryUserRepository
from user_management.application.services.user_service import UserService

repository = InMemoryUserRepository()
service = UserService(repository)

# Create a new user
from user_management.application.dtos.user_requests import CreateUserRequest

request = CreateUserRequest(
    email="user@example.com",
    name="John Doe",
    role="Developer",
    team="Engineering",
    company="TechCorp"
)
response = service.create_user(request)
user_id = response.user_id
```

### Experience and Level Progression
```python
# Award experience points
from user_management.application.dtos.user_requests import GainExperienceRequest

xp_request = GainExperienceRequest(
    user_id=user_id,
    experience_points=150,
    reason="Successful optimization"
)
xp_response = service.gain_experience(xp_request)

if xp_response.level_up_occurred:
    print(f"Level up! New level: {xp_response.new_level}")
    print(f"Level title: {xp_response.level_title}")
```

### Optimization Tracking
```python
# Track optimization results
from user_management.application.dtos.user_requests import TrackOptimizationRequest

optimization_request = TrackOptimizationRequest(
    user_id=user_id,
    was_successful=True,
    optimization_type="Context Window Optimization"
)
track_response = service.track_optimization(optimization_request)
print(f"New success rate: {track_response.success_rate:.1%}")
```

## API Reference

### Core Services
- `UserService`: Main service class
  - `create_user()`: Create new user with profile and initial gamification stats
  - `gain_experience()`: Award XP with automatic level-up detection
  - `get_user_profile()`: Retrieve user profile information
  - `get_user_stats()`: Get comprehensive user statistics
  - `track_optimization()`: Record optimization attempts and results

### DTOs

#### Request DTOs
- `CreateUserRequest`: User creation with profile information
- `GainExperienceRequest`: XP award with reason
- `UpdateProfileRequest`: Profile information updates
- `TrackOptimizationRequest`: Optimization result recording

#### Response DTOs
- `CreateUserResponse`: User creation confirmation with ID
- `GainExperienceResponse`: XP award results with level-up info
- `GetUserProfileResponse`: Complete user profile data
- `UserStatsResponse`: Comprehensive user statistics
- `TrackOptimizationResponse`: Updated optimization statistics

For detailed API documentation, see [API.md](./API.md).

## Testing

### Running Tests
```bash
# Run all tests for this module
cd modules/user_management
python3 manual_test.py

# Run with debug output
export MODULE_DEBUG=true
python3 manual_test.py
```

### Test Coverage
- **Unit Tests**: 100% coverage (8 test scenarios)
- **Integration Tests**: Service-repository integration
- **End-to-End Tests**: Complete user lifecycle workflows

### Test Scenarios
1. **User Creation**: Valid profile creation with initial gamification stats
2. **XP Gain Without Level-up**: Standard experience point awards
3. **XP Gain With Level-up**: Level progression with XP carryover
4. **Win Streak Tracking**: Consecutive success monitoring
5. **Profile Retrieval**: Complete user data access
6. **Invalid Email Validation**: Error handling for malformed emails
7. **Statistics Calculation**: Success rates and derived metrics
8. **Optimization Tracking**: Success/failure result recording

For detailed testing information, see [TESTING.md](./TESTING.md).

## Data Management

### Data Models

#### User Entity (Aggregate Root)
- **ID**: Unique user identifier (UUID)
- **Profile**: Immutable user profile information
- **Stats**: Mutable gamification statistics
- **Created/Updated**: Timestamp tracking

#### UserProfile Value Object
- **Email**: Validated email address (required)
- **Name**: User's full name
- **Role**: Job role/position
- **Team**: Team/department
- **Company**: Organization name

#### GamificationStats Value Object
- **Level**: Current user level (1-9)
- **Experience Points**: Total XP accumulated
- **Total Optimizations**: All optimization attempts
- **Successful Optimizations**: Successful attempts only
- **Win Streak**: Current consecutive successes
- **Derived Properties**: Success rate, current level XP, XP until next level

### Data Flow
1. **User Creation**: Profile validation → Stats initialization → Entity creation → Repository storage
2. **XP Gain**: XP addition → Level calculation → Carryover handling → Stats update → Storage
3. **Optimization Tracking**: Result recording → Success rate calculation → Win streak update → Storage

### Persistence
- **Repository Pattern**: Abstract `UserRepository` interface
- **In-Memory Implementation**: `InMemoryUserRepository` for testing and development
- **File-Based Implementation**: `FileUserRepository` for persistent storage
- **Database Implementation**: Future PostgreSQL/MongoDB integration

## Integration

### Event Publishing
This module will publish the following events:
- `UserCreated`: When new user is successfully created
- `UserLeveledUp`: When user reaches new level
- `ExperienceGained`: When user receives XP
- `OptimizationCompleted`: When optimization result is recorded

### Event Subscription
This module will subscribe to:
- `AchievementUnlocked`: From Achievement System (to award bonus XP)
- `OptimizationResultCalculated`: From Core RAG module

### API Integration
- **APIs Provided**: User profile access, gamification statistics, XP awards
- **APIs Consumed**: Achievement system for bonus XP calculations

## Error Handling

### Common Errors
- `ValueError`: Invalid email format, negative XP values, missing required fields
- `KeyError`: User not found in repository
- `TypeError`: Invalid data types in requests

### Error Response Format
```json
{
  "success": false,
  "error": "Invalid email format: not-an-email",
  "user_id": null,
  "timestamp": "2023-12-07T10:30:00Z"
}
```

## Performance Considerations

### Optimization Notes
- **Level Calculation**: O(1) lookup using pre-calculated thresholds
- **XP Processing**: Efficient carryover calculation for multi-level gains
- **In-Memory Storage**: Fast access for development and testing
- **JSON Loading**: Configuration loaded once at startup

### Monitoring
- **User Creation Rate**: New users per time period
- **XP Award Frequency**: Experience gain patterns
- **Level Distribution**: User progression analytics
- **Success Rate Trends**: Optimization performance over time

## Security Considerations

### Data Protection
- **Email Validation**: Prevents malformed data entry
- **Input Sanitization**: All request data validated before processing
- **No Sensitive Data**: Passwords handled by separate authentication module

### Privacy Considerations
- **User Consent**: Profile data collection with explicit user agreement
- **Data Minimization**: Only necessary fields collected
- **Anonymization**: Future analytics will anonymize user data

## Troubleshooting

### Common Issues
1. **Import Error**: `ImportError: attempted relative import beyond top-level package`
   - **Cause**: Incorrect Python path configuration
   - **Solution**: Add workspace and modules to `sys.path`

2. **Test Data Loading Error**: `FileNotFoundError: gamification_test_data.json`
   - **Cause**: Missing test data file or incorrect path
   - **Solution**: Ensure test data file exists in `tests/test_data/`

3. **Level Calculation Error**: Incorrect level assignment
   - **Cause**: Missing level definitions in test data
   - **Solution**: Verify level system completeness in configuration

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
6. Update all documentation

### Code Style
- Follow PEP 8 for Python code
- Use type hints consistently (`typing` module)
- Write descriptive docstrings for all public methods
- Use dataclasses for DTOs and value objects
- Follow Repository pattern for data access

## Changelog

### Version 1.0.0 - 2023-12-07
#### Added
- Initial implementation of User Management module
- User profile creation with email validation
- Gamification system with 9-level progression
- Experience point tracking with automatic level-up
- Win streak monitoring for consecutive successes
- Optimization result tracking and success rate calculation
- Hexagonal architecture with domain/application/infrastructure separation
- Repository pattern with in-memory and file-based implementations
- Comprehensive manual testing framework
- JSON-based configuration for level system

#### Core Features
- **User Creation**: Profile validation and initial stats setup
- **XP System**: Experience gain with level progression and carryover
- **Statistics**: Success rate calculation and performance tracking
- **Level System**: 9 tiers from Novice to Legend with XP thresholds
- **Data Persistence**: Multiple repository implementations

#### Testing
- Unit tests for all domain entities and value objects
- Integration tests for service-repository interactions
- End-to-end tests for complete user workflows
- Manual test script with comprehensive scenarios
- Test data fixtures with realistic user profiles

#### Documentation
- Comprehensive README with usage examples
- API documentation with request/response schemas
- Testing documentation with scenario descriptions
- Inline code documentation for all public methods

For detailed changelog, see [CHANGELOG.md](./CHANGELOG.md).

## Contributing

### Development Setup
1. Navigate to `modules/user_management/`
2. Ensure Python 3.8+ is available
3. Verify test data file exists: `../../tests/test_data/gamification_test_data.json`

### Pull Request Process
1. Update documentation (README, API, TESTING, CHANGELOG)
2. Add/update tests for new functionality
3. Ensure all manual tests pass
4. Update level system configuration if needed
5. Verify integration with other modules

## Related Documentation
- [Main Project README](../../README.md)
- [Architecture Overview](../../docs/architecture/)
- [API Documentation](./API.md)
- [Testing Guide](./TESTING.md)
- [Module Implementation Summary](../../module_implementation_summary.md)
- [TDD Cycles Documentation](../../tdd_cycles_self_improving_rag.md)
- [Gamification Test Data](../../tests/test_data/gamification_test_data.json)
